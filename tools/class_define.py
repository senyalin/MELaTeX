
from reportlab.pdfgen import canvas

class Char():

    def __init__(self, bbox = None, char = None, glythbox = None, display = False) -> None:
        self.bbox = bbox #type: list[float]
        self.char = char #type: str
        self.addition = None
        self.sub = None #type: Chunk
        self.sup = None #type: Chunk
        self.elements = None #type: list[Chunk]
        self.display = display
        self.chunk = None #type: Chunk
        self.complete = False
        if glythbox:
            bbox[0] = bbox[0] if glythbox[0] > bbox[0] else glythbox[0]
            bbox[1] = bbox[1] if glythbox[1] > bbox[1] else glythbox[1]
            bbox[2] = bbox[2] if glythbox[2] < bbox[2] else glythbox[2]
            bbox[3] = bbox[3] if glythbox[3] < bbox[3] else glythbox[3]

        
        if glythbox and bbox[1]+bbox[3]<glythbox[1]+glythbox[3]:
            midline = (glythbox[1] + glythbox[3])/2
            if bbox[3] - midline > midline - bbox[1]:
                bbox[3] = midline + midline - bbox[1]
            else:
                bbox[1] = midline + midline - bbox[3]
        
        big_operator_inline = {
            "\\sum","\\int",
        }

        if self.char in big_operator_inline:
            self.bbox = glythbox

    def __str__(self) -> str:
        return self.char
    
    def draw_can(self, can:canvas.Canvas) -> None:
        from tools.mapping import topping
        upperLeft_x = self.bbox[0]
        upperLeft_y = self.bbox[1]
        height = self.bbox[3] - self.bbox[1]
        width = self.bbox[2] - self.bbox[0]
        can.setStrokeColorRGB(0, 1, 0)
        can.rect(upperLeft_x, upperLeft_y, width, height, fill=0, stroke=1)

    def adjust(self, other_bbox:list[float]) -> None:
        self.bbox[0] = self.bbox[0] if other_bbox[0] > self.bbox[0] else other_bbox[0]
        self.bbox[1] = self.bbox[1] if other_bbox[1] > self.bbox[1] else other_bbox[1]
        self.bbox[2] = self.bbox[2] if other_bbox[2] < self.bbox[2] else other_bbox[2]
        self.bbox[3] = self.bbox[3] if other_bbox[3] < self.bbox[3] else other_bbox[3]
        
class Chunk():
    def __init__(self, char:Char) -> None:
        char.addition = None
        char.chunk = self
        self.bbox = char.bbox[:] if char.bbox else None
        self.centerbbox = char.bbox[:] if char.bbox else None
        self.childs = [char]
        self.max_width = self.bbox[2] - self.bbox[0] if char.bbox else None
        self.parent = None #type: Char
        self.next = None
    
    def adjust(self, other_bbox:list[float]) -> None:
        self.centerbbox[0] = self.bbox[0] if other_bbox[0] > self.centerbbox[0] else other_bbox[0]
        self.centerbbox[1] = self.bbox[1] if other_bbox[1] > self.centerbbox[1] else other_bbox[1]
        self.centerbbox[2] = self.bbox[2] if other_bbox[2] < self.centerbbox[2] else other_bbox[2]
        self.centerbbox[3] = self.bbox[3] if other_bbox[3] < self.centerbbox[3] else other_bbox[3]
    
    def merge(self, char:Char, addition=None, split=False) -> None:
        char.chunk = self
        self.bbox[0] = self.bbox[0] if char.bbox[0] > self.bbox[0] else char.bbox[0]
        self.bbox[1] = self.bbox[1] if char.bbox[1] > self.bbox[1] else char.bbox[1]
        self.bbox[2] = self.bbox[2] if char.bbox[2] < self.bbox[2] else char.bbox[2]
        self.bbox[3] = self.bbox[3] if char.bbox[3] < self.bbox[3] else char.bbox[3]
        self.childs.append(char)
        if not split:
            char.addition = addition
        self.centerbbox[0] = self.centerbbox[0] if char.bbox[0] > self.centerbbox[0] else char.bbox[0]
        self.centerbbox[2] = self.centerbbox[2] if char.bbox[2] < self.centerbbox[2] else char.bbox[2]
        if not addition:
            self.centerbbox[1] = char.bbox[1]
            self.centerbbox[3] = char.bbox[3]
        if char.char not in ["\\frac"]:
            self.max_width = self.max_width if char.bbox[2]-char.bbox[0] < self.max_width else char.bbox[2]-char.bbox[0]
    
    def __str__(self) -> str:
        temp = "Chunk: "+str(self.bbox)+"\n"
        for chunk in self.childs:
            if chunk.char:
                temp += str(chunk)+"\n"
            if chunk.sub:
                temp += "sub{\n"
                temp += str(chunk.sub)
                temp += "}\n"
            if chunk.sup:
                temp += "sup{\n"
                temp += str(chunk.sup)
                temp += "}\n"
            if chunk.elements:
                    for element in chunk.elements:
                        temp+="{"+element.chunk2latex()+"}"
        if self.next:
            temp += str(self.next)
        return temp
    
    def chunk2latex(self) -> str:
        latex = ""
        flag = "None"
        for char in self.childs:
            if char.char:
                latex+=str(char)+" "
                
                if char.sub:
                    latex+="_ { "+char.sub.chunk2latex()+"} "
                if char.sup:
                    latex+="^ { "+char.sup.chunk2latex()+"} "
                if char.elements and char.sup:
                    for element in char.elements:
                        latex+=element.chunk2latex()
                elif char.elements:
                    for element in char.elements:
                        latex+="{ "+element.chunk2latex()+"} "

        if flag in ["Above","Under"]:
            latex+="} "
            flag = "None"
        if self.next:
            latex+=self.next.chunk2latex()
        return latex
    
    def split(self,x1:float,x2:float):
        temp = None
        remain = None
        replace = None
        entry = None
        for char in self.childs:
            if char.bbox[0] > x1-0.5 and char.bbox[2] < x2+0.5:
                if not temp:
                    temp = Chunk(char)
                else:
                    temp.merge(char,split=True)
            else:
                if not remain:
                    remain = Chunk(char)
                else:
                    remain.merge(char,split=True)
        if temp:
            for ch in self.childs:
                if not entry and ch in temp.childs:
                    entry = Char(bbox=temp.bbox)
                    if not replace:
                        replace = Chunk(entry)
                    else :
                        replace.merge(entry)
                elif remain and ch in remain.childs:
                    if replace:
                        replace.merge(ch)
                    else:
                        replace = Chunk(ch)
            return (temp,remain,self,replace,entry)
        else:
            return None
    
    
    def draw_can(self,can:canvas.Canvas):
        upperLeft_x = self.bbox[0]-1
        upperLeft_y = self.bbox[1]-1
        height = self.bbox[3] - self.bbox[1] +2
        width = self.bbox[2] - self.bbox[0] +2
        can.setStrokeColorRGB(0.5,0.5,0.5)
        can.rect(upperLeft_x, upperLeft_y, width, height, fill=0, stroke=1)
        for char in self.childs:
            upperLeft_x = char.bbox[0]
            upperLeft_y = char.bbox[1]
            height = char.bbox[3] - char.bbox[1]
            width = char.bbox[2] - char.bbox[0]
            if char.sup :
                char.sup.draw_can(can)
            if char.sub :
                char.sub.draw_can(can)
            if char.elements:
                for element in char.elements:
                    element.draw_can(can)
            if not char.addition:
                can.setStrokeColorRGB(0, 0, 1)
            elif char.addition == "Above":
                can.setStrokeColorRGB(1, 0, 0)
            elif char.addition == "Under":
                can.setStrokeColorRGB(0, 1, 0)
            else:
                can.setStrokeColorRGB(0, 0, 1)
            can.rect(upperLeft_x, upperLeft_y, width, height, fill=0, stroke=1)
            

def char_process(chunk:Chunk):
    text = ""
    flag = True
    for char in chunk.chars:
        if not char.text:
            continue
        text += char.text
        if not flag:
            text += "}"
            flag = True
        if char.text[-1] == "{":
            flag = False
    return text

class Column_instence():
    def __init__(self,element:list[Chunk],align_mode:str) -> None:
        element.sort(key = lambda x:x.centerbbox[1],reverse= True)
        self.element = element
        
        self.align_mode = align_mode
        self.centerbbox = None
        for chunk in element:
            if self.centerbbox == None:
                self.centerbbox = chunk.centerbbox
            else:
                self.centerbbox[0] = self.centerbbox[0] if self.centerbbox[0] < chunk.centerbbox[0] else chunk.centerbbox[0]
                self.centerbbox[1] = self.centerbbox[1] if self.centerbbox[1] < chunk.centerbbox[1] else chunk.centerbbox[1]
                self.centerbbox[2] = self.centerbbox[2] if self.centerbbox[2] > chunk.centerbbox[2] else chunk.centerbbox[2]
                self.centerbbox[3] = self.centerbbox[3] if self.centerbbox[3] > chunk.centerbbox[3] else chunk.centerbbox[3]
        pass


class Array_instence():
    def __init__(self,element:list[Column_instence]) -> None:
        self.element = []
        self.align_mode = element[0].align_mode
        for chunk in element[0].element:
            self.element.append([chunk])
        for column in element[1:]:
            self.align_mode += column.align_mode
            for i,chunk in enumerate(column.element):
                self.element[i].append(chunk)
        
        self.centerbbox = None
        for row in self.element:
            for chunk in row:
                if self.centerbbox == None:
                    self.centerbbox = chunk.centerbbox
                else:
                    self.centerbbox[0] = self.centerbbox[0] if self.centerbbox[0] < chunk.centerbbox[0] else chunk.centerbbox[0]
                    self.centerbbox[1] = self.centerbbox[1] if self.centerbbox[1] < chunk.centerbbox[1] else chunk.centerbbox[1]
                    self.centerbbox[2] = self.centerbbox[2] if self.centerbbox[2] > chunk.centerbbox[2] else chunk.centerbbox[2]
                    self.centerbbox[3] = self.centerbbox[3] if self.centerbbox[3] > chunk.centerbbox[3] else chunk.centerbbox[3]

    def __str__(self) -> str:
        temp = "\\begin{array}{%s}"%self.align_mode
        first_row = True
        for row in self.element:
            if not first_row:
                    temp += " \\\\ "
            else:
                first_row = False
            
            first_column = True
            for column in row:
                if not first_column:
                    temp += " & "
                else:
                    first_column = False
                temp += "{ "+ str(column) + "} "
        temp += "\\end{array}"
        return temp
    def chunk2latex(self) -> str:
        temp = "\\begin{array} { %s } "%" ".join(self.align_mode)
        first_row = True
        for row in self.element:
            if not first_row:
                    temp += "\\\\ "
            else:
                first_row = False
            
            first_column = True
            for column in row:
                if not first_column:
                    temp += "& "
                else:
                    first_column = False
                temp += "{ " + column.chunk2latex() + "} "
        temp += "\\\\ \\end{array} "
        return temp
    
    def draw_can(self,can:canvas.Canvas):
        pass
                 

    

    