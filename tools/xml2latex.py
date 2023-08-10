
from xml.etree.ElementTree import Element
import pdfplumber

from tools.draw import *
from tools.mapping import *
from tools.class_define import *
def xml2chunk(formula:Element,path:str,debug=False):
    pdf = PdfFileReader(open(path, "rb"))

    list_of_chars = char_preprocess(formula)
    list_of_chars += find_lines([float(i) for i in formula.attrib["BBox"].split()],path)

    list_of_chars.sort(key = lambda x:x.bbox[1],reverse=True)
    list_of_chars.sort(key = lambda x:x.bbox[0])
    list_of_chars = big_symbol_convert(list_of_chars)
    list_of_chars = radical_premerge(list_of_chars)
    if debug:
        draw_list_of_char(list_of_chars,"_1_",pdf)
    
    list_of_chunks = first_merge(list_of_chars,debug)
    return list_of_chunks

def xml2latex(formula:Element,path:str,debug=False,config = None)->str:
    pdf = PdfFileReader(open(path, "rb"))

    list_of_chars = char_preprocess(formula)
    list_of_chars += find_lines([float(i) for i in formula.attrib["BBox"].split()],path)

    list_of_chars.sort(key = lambda x:x.bbox[1],reverse=True)
    list_of_chars.sort(key = lambda x:x.bbox[0])
    list_of_chars = big_symbol_convert(list_of_chars)
    list_of_chars = radical_premerge(list_of_chars)
    if debug:
        draw_list_of_char(list_of_chars,"_1_",pdf)
    
    list_of_chunks = first_merge(list_of_chars,debug,config)

    if debug:
        draw_list_of_super_chunk(list_of_chunks,"_2_",pdf)
    
    list_of_chunks = radical_merge(list_of_chunks)
    list_of_chunks = second_merge(list_of_chunks)
    list_of_chunks = display_symbol_merge(list_of_chunks)
    list_of_chunks = bbox_adjust(list_of_chunks)
    list_of_chunks = array_merge(list_of_chunks)
    if debug:
        draw_list_of_super_chunk(list_of_chunks,"_3_",pdf)

    return list_of_chunk_to_str(list_of_chunks)
    
#create Char object from xml file
def char_preprocess(formula:Element)->list[Char]:
    list_of_chars = [] #type: list[Char]
    for char in formula[:-1]:
        list_of_chars.append(Char(
            char = first_mapping(char.attrib["Text2"]),
            bbox = [float(i) for i in char.attrib["BBox2"].split()],
            glythbox = [float(i) for i in char.attrib["BBox"].split()],
            display= char.attrib["Text2"] in big_operator_display.keys(),
        ))
    return list_of_chars

#find symbols(horizontal lines) from original pdf that are not in xml file
def find_lines(boarder:list[float],path:str)->list[Char]:
    boarder = [boarder[0]-5,boarder[1]-5,boarder[2]+5,boarder[3]+5]
    list_of_lines = [] #type: list[Char]
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for img in page.images:
                bbox = [img["x0"],img["y0"]-0.25,img["x1"],img["y1"]+0.25]
                if bbox[3]-bbox[1]<1 and boarder[0]<bbox[0] and boarder[1]<bbox[1] and boarder[2]>bbox[2] and boarder[3]>bbox[3]:
                    list_of_lines.append(Char(bbox=bbox, char="\\frac"))
            for line in page.lines:
                bbox = [line["x0"]-0.5,line["y0"]-0.25,line["x1"]+0.5,line["y1"]+0.25]
                if boarder[0]<bbox[0] and boarder[1]<bbox[1] and boarder[2]>bbox[2] and boarder[3]>bbox[3]:
                    list_of_lines.append(Char(bbox=bbox, char="\\frac"))
    return list_of_lines

#merge multi object symbal to one
def big_symbol_convert(list_of_chars:list[Char])->list[Char]:
    new_list = [] #type: list[Char]
    flag = False
    bbox = None
    text = None
    for char in list_of_chars:
        if is_big_symbol(char):
            if not flag:
                flag = True
                bbox = char.bbox[:]
                text = big_brackets_top[char.char]
            else:
                bbox[0] = bbox[0] if char.bbox[0] > bbox[0] else char.bbox[0]
                bbox[1] = bbox[1] if char.bbox[1] > bbox[1] else char.bbox[1]
                bbox[2] = bbox[2] if char.bbox[2] < bbox[2] else char.bbox[2]
                bbox[3] = bbox[3] if char.bbox[3] < bbox[3] else char.bbox[3]
                if char.char in big_brackets_bottom:
                    flag = False
                    new_list.append(Char(bbox = bbox,char = text))
        else:
            new_list.append(char)
    return new_list

#merge Char by horizontal relation and sup/sub relation
def first_merge(list_of_chars:list[Char],debug,config)->list[Chunk]:

    list_of_chunks = [] #type: list[Chunk]
    list_of_remains = [] #type: list[Char]
    parent_list = [] #type: list[Char]
    temp = None
    while list_of_chars:
        #record if "next_char" is really next to current char
        next_flag = True
        if temp == None:
            temp = Chunk(list_of_chars[0])
            last_char = list_of_chars[0]
            #big char always ends the chunk since it may cause problem(but this also make some problem)
            break_flag = last_char.char in big_element
        else :
            break_flag = False
        for next_char in list_of_chars[1:]:

            if break_flag:
                list_of_remains.append(next_char)
                next_flag = False
                continue
            
            # topping
            if next_char.char in topping.values() and next_flag:
                last_char.char = next_char.char+" { "+last_char.char+" }"
                continue
            # skip overlap with fraction
            if last_char.char == "\\frac" and temp.bbox[2] > (next_char.bbox[0]+next_char.bbox[2])/2 :
                list_of_remains.append(next_char)
                next_flag = False
                continue
            # radical wait unit next is frac
            if last_char.char in radical and next_char.char != "\\frac":
                list_of_remains.append(next_char)
                next_flag = False
                continue
            elif last_char.char in radical and next_char.char == "\\frac":
                temp.merge(next_char)
                last_char = next_char
            # next char is too far
            if next_char.bbox[0] - last_char.bbox[2] > next_char.bbox[2] - next_char.bbox[0] and next_char.bbox[0] - last_char.bbox[2] > temp.max_width:
                list_of_remains.append(next_char)
                next_flag = False
                continue
            # vertical untouched
            if temp.centerbbox[1]>next_char.bbox[3] or temp.centerbbox[3]<next_char.bbox[1]:
                list_of_remains.append(next_char)
                next_flag = False
                continue
            # horizon overlap
            if last_char.bbox[2]>next_char.bbox[2]:
                list_of_remains.append(next_char)
                next_flag = False
                continue
            if next_char.char in big_element:
                list_of_remains.append(next_char)
                break_flag = True
                next_flag = False
                continue
            if parent_list:
                parent_relation = det_relation(parent_list[-1][0].bbox,next_char.bbox,(parent_list[-1][0].char=="\\frac") or (next_char.char=="\\frac"),config)
                
                if relation == None and parent_relation and parent_relation == "Normal":
                    break_flag = True
                    list_of_remains.append(next_char)
                    next_flag = False
                    continue
                elif parent_relation and parent_relation == "Normal+":
                    break_flag = True
                    list_of_remains.append(next_char)
                    next_flag = False
                    continue
            
            relation = det_relation(last_char.bbox,next_char.bbox,(last_char=="\\frac") or (next_char.char=="\\frac"),config)
            if debug:
                print("Relation "+str(last_char)+" with "+str(next_char)+" is "+str(relation))
            if relation:
                next_flag = True
                if relation == "Above":
                    parent_list.append((last_char,list_of_remains,temp))
                    list_of_remains = []
                    temp = last_char.sup = Chunk(next_char)
                    last_char.sup.parent = last_char
                    last_char = next_char

                elif relation == "Under":
                    parent_list.append((last_char,list_of_remains,temp))
                    list_of_remains = []
                    temp = last_char.sub = Chunk(next_char)
                    last_char.sub.parent = last_char
                    last_char = next_char

                else:
                    temp.merge(next_char)
                    last_char = next_char
                    
            else :
                list_of_remains.append(next_char)
                next_flag = False
                continue

            # if next_char.char in big_element:
            #     break_flag = True

        if parent_list:
            list_of_chars = list_of_remains
            last_char,list_of_remains,temp = parent_list.pop()
            list_of_chars.insert(0,None)
        else :
            list_of_chunks.append(temp)
            temp = None
            list_of_chars = list_of_remains
            list_of_remains = []

    return list_of_chunks

#use tan and distence to determine relation
def det_relation(bbox1:list[float],bbox2:list[float],isfrac,config)->bool:
    if config == None:
        thresh_sup = 0.27
        thresh_sub = -0.2
        thresh_dis = 1

        thresh_hor_low = -1
        thresh_hor_upp = 1

        thresh_hor_low_strict = -0.25
        thresh_hor_upp_strict = 0.25

        thresh_big = 0.5
        thresh_max = 3
    else :
        thresh_sup = config["thresh_sup"]
        thresh_sub = config["thresh_sub"]
        thresh_dis = config["thresh_dis"]

        thresh_hor_low = config["thresh_hor_low"]
        thresh_hor_upp = config["thresh_hor_upp"]

        thresh_hor_low_strict = config["thresh_hor_low_strict"]
        thresh_hor_upp_strict = config["thresh_hor_upp_strict"]

        thresh_big = config["thresh_big"]
        thresh_max = config["thresh_max"]

    x_diff = (bbox2[2]+bbox2[0]-bbox1[2]-bbox1[0])
    y_diff = (bbox2[3]+bbox2[1]-bbox1[3]-bbox1[1])

    f_size2 = (bbox2[3]-bbox2[1])
    f_size1 = (bbox1[3]-bbox1[1])

    if (bbox2[0]-bbox1[2]) < 0:
        distance = 0
    else:
        distance = ((bbox2[0]-bbox1[2])**2+(bbox2[3]-bbox2[1]-bbox1[3]+bbox1[1])**2)**0.5/(f_size1+f_size2)
    
    if x_diff <= 0:
        x_diff = 1e-32
    tan = y_diff/x_diff
    if (thresh_hor_low_strict < y_diff/max(f_size1,f_size2) < thresh_hor_upp_strict) and (((f_size1/f_size2) < 3) or isfrac):
        return "Normal+"
    # print("distance <= THRESH_DIS? ",distance <= THRESH_DIS)
    # print("f_size2*THRESH_BIG < f_size1? ",f_size2*THRESH_BIG < f_size1)
    if f_size2*thresh_big < f_size1 and distance <= thresh_dis:
        if thresh_max > tan > thresh_sup:
            return "Above"
        elif -thresh_max < tan < thresh_sub:
            return "Under"
    
    if thresh_hor_low < y_diff/f_size1 < thresh_hor_upp:
        return "Normal"
    else :
        return None

#find left sup script of radicals(ex:cube root)
def radical_premerge(list_of_char:list[Char])->list[Char]:
    temp = [] #type: list[Char]
    for char in list_of_char:
        if char.char in radical:
            for other_char in list_of_char:
                if char == other_char:
                    continue
                if other_char.bbox[0] > char.bbox[0]:
                    pass
                else :
                    mid_diff = (other_char.bbox[1]+other_char.bbox[3]-char.bbox[1]-char.bbox[3])/(char.bbox[3]-char.bbox[1])
                    dis = ((other_char.bbox[2]-char.bbox[0])**2+(other_char.bbox[3]-other_char.bbox[1]-char.bbox[3]+char.bbox[1])**2)**0.5/(char.bbox[3]-char.bbox[1])
                    if -0.2 < mid_diff < 0.2 and dis < 1:
                        temp.append(other_char)

            temp.sort(key = lambda x:x.bbox[0],reverse=True)
            if temp:
                temp[0].char = "^ { "+temp[0].char+"} "
                temp[0].bbox[1],temp[0].bbox[3]=char.bbox[1],char.bbox[3]
    return list_of_char
                
#merge radicals v part and line part
def radical_merge(list_of_chunks:list[Chunk])->list[Chunk]:
    for chunk in list_of_chunks:
        for i,char in enumerate(chunk.childs):
            if char.char == "\\frac" and i>0:
                if chunk.childs[i-1].char in radical:
                    chunk.childs[i].char = "\\sqrt"
                    chunk.childs[i-1].char=None
                    chunk.childs[i].bbox[0] = chunk.childs[i-1].bbox[0]
    list_of_chunks = clean_empty(list_of_chunks)
    return list_of_chunks
    
#merge fraction,radical,overline,underline,and inline big operator, starts from shortest line
def second_merge(list_of_chunks:list[Chunk])->list[Chunk]:

    flag = True
    while flag:
        lower = 0
        upper = float("inf")
        flag = False
        shortest = None

        for chunk in list_of_chunks:
            #find shortest line
            for char in chunk.childs:
                if char.sup:
                    local_min = min_line(char.sup.childs)
                    if local_min:
                        if not shortest or local_min.bbox[2]-local_min.bbox[0] < shortest.bbox[2]-shortest.bbox[0]:
                            shortest = local_min
                        flag = True

                if char.sub:
                    local_min = min_line(char.sub.childs)
                    if local_min:
                        if not shortest or local_min.bbox[2]-local_min.bbox[0] < shortest.bbox[2]-shortest.bbox[0]:
                            shortest = local_min
                        flag = True

                if char.char in {"\\frac","\\sqrt"} and char.elements is None:
                    if not shortest or char.bbox[2]-char.bbox[0] < shortest.bbox[2]-shortest.bbox[0]:
                        shortest = char
                    flag = True
        #use other lines to limit area to find chunks to merge
        if flag:
            for chunk in list_of_chunks:
                for char in chunk.childs:
                    if char.char in {"\\frac","\\sqrt"} and char.elements is None:
                        if char != shortest and char.bbox[0] < shortest.bbox[0] and char.bbox[2] > shortest.bbox[2]:
                            lower = lower if char.bbox[1]+char.bbox[3] > shortest.bbox[1]+shortest.bbox[3] or char.bbox[1]+char.bbox[3] < lower else char.bbox[1]+char.bbox[3]
                            upper = upper if char.bbox[1]+char.bbox[3] < shortest.bbox[1]+shortest.bbox[3] or char.bbox[1]+char.bbox[3] > upper else char.bbox[1]+char.bbox[3]

            fraction_merge(list_of_chunks,shortest,upper,lower)
            #merge cause some char removed and chunk emptied but remove them at merge will cause list messing up,so only clean when one iteration is over
            #(char mark for remove will set ther self.char to None)
            list_of_chunks = clean_empty(list_of_chunks)
            
    return list_of_chunks

#find the shortest line in a given list of Chars(can be seem as a Chunk)
def min_line(list_of_char:list[Char])->Char:

    shortest = None
    for char in list_of_char:
        if char.sup:
            local_min = min_line(char.sup.childs)
            if local_min:
                if not shortest or local_min.bbox[2]-local_min.bbox[0] < shortest.bbox[2]-shortest.bbox[0]:
                    shortest = local_min

        if char.sub:
            local_min = min_line(char.sub.childs)
            if local_min:
                if not shortest or local_min.bbox[2]-local_min.bbox[0] < shortest.bbox[2]-shortest.bbox[0]:
                    shortest = local_min
                    
        if char.char in {"\\frac","\\sqrt"} and not char.elements:
            if not shortest or char.bbox[2]-char.bbox[0] < shortest.bbox[2]-shortest.bbox[0]:
                shortest = char

    return shortest

#merge fraction,radical,overline,underline of the given line also inturrupt by inline big operator merging
def fraction_merge(list_of_chunks:list[Chunk],char:Char,upper_bound:float,lower_bound:float)->None:
    above = [] #type: list[Chunk]
    below = [] #type: list[Chunk]

    #find chunks that are inside bounds and fully above or under the line
    for other_chunk in list_of_chunks:
        if char in other_chunk.childs:
            continue
        if other_chunk.centerbbox[2] < char.bbox[0] or other_chunk.centerbbox[0] > char.bbox[2] or other_chunk.centerbbox[1]+other_chunk.centerbbox[3] > upper_bound or other_chunk.centerbbox[1]+other_chunk.centerbbox[3] < lower_bound:
            pass
        elif other_chunk.centerbbox[1]+other_chunk.centerbbox[3] > char.bbox[1]+char.bbox[3] :
            above.append(other_chunk)
        else:
            below.append(other_chunk)
    
    #cutting chunks to match the line's x range and choose the nearest chunk
    above = [i.split(char.bbox[0],char.bbox[2]) for i in above] #type: list[tuple[Chunk,Chunk,Chunk,Chunk,Char]]
    while None in above :above.remove(None)
    if above:above_chunk = min(above,key=lambda x:x[2].centerbbox[1])
    below = [i.split(char.bbox[0],char.bbox[2]) for i in below] #type: list[tuple[Chunk,Chunk,Chunk,Chunk,Char]]
    while None in below :below.remove(None)
    if below:below_chunk = max(below,key=lambda x:x[2].centerbbox[1])

    #search if there is inline big operator inside
    for chunk in above:
        if chunk[0].childs[-1].char in big_operator.values() and not chunk[0].childs[-1].display and chunk[0].childs[-1].complete is False:
            inline_symbol_merge(list_of_chunks,chunk[0].childs[-1])
            return
    for chunk in below:
        if chunk[0].childs[-1].char in big_operator.values() and not chunk[0].childs[-1].display and chunk[0].childs[-1].complete is False:
            inline_symbol_merge(list_of_chunks,chunk[0].childs[-1])
            return
    
    #line is fraction line
    if above and below:
        char.elements = [above_chunk[0],below_chunk[0]]
        if above_chunk[1]:
            for i,chunk in enumerate(list_of_chunks):
                if chunk == above_chunk[2]:
                    list_of_chunks[i]=above_chunk[1]
        else:
            list_of_chunks.remove(above_chunk[2])

        if below_chunk[1]:
            for i,chunk in enumerate(list_of_chunks):
                if chunk == below_chunk[2]:
                    list_of_chunks[i]=below_chunk[1]
        else:
            list_of_chunks.remove(below_chunk[2])
        if char.chunk.parent:
            check_frac_relation(char)
    #line is underline
    elif above:
        above_chunk[4].char = "\\underline"
        char.char = None
        if above_chunk[2].parent:
            if above_chunk[2].parent.sup == above_chunk[2]:
                above_chunk[2].parent.sup =  above_chunk[3]
            else :
                above_chunk[2].parent.sup =  above_chunk[3]
        else :
            pos = list_of_chunks.index(above_chunk[2])
            list_of_chunks[pos]=above_chunk[2]
        above_chunk[4].elements = [above_chunk[0]]
    #line is squre root or overline
    elif below:
        below_chunk[4].char = char.char if char.char == "\\sqrt" else "\\overline"
        char.char = None
        if below_chunk[2].parent:
            if below_chunk[2].parent.sup == below_chunk[2]:
                below_chunk[2].parent.sup =  below_chunk[3]
            else :
                below_chunk[2].parent.sup =  below_chunk[3]
        else :
            pos = list_of_chunks.index(below_chunk[2])
            list_of_chunks[pos]=below_chunk[3]
        below_chunk[4].elements = [below_chunk[0]]
    
    #fail
    else:
        char.char=None
        return

#merge inline big operator
def inline_symbol_merge(list_of_chunks:list[Chunk],char:Char)->None:
    above = [] #type: list[Chunk]
    below = [] #type: list[Chunk]

    for other_chunk in list_of_chunks:
        if char in other_chunk.childs:
            continue
        if other_chunk.centerbbox[0] < char.bbox[0]:
            pass
        else :
            mid_diff = (other_chunk.bbox[1]+other_chunk.bbox[3]-char.bbox[1]-char.bbox[3])/(char.bbox[3]-char.bbox[1])
            if 0.2 < mid_diff < 2:
                above.append(other_chunk)
            elif -0.2 > mid_diff > -2:
                below.append(other_chunk)

    if above:
        above_chunk = min(above,key=lambda x:x.centerbbox[0])
        char.sup = above_chunk
        list_of_chunks.remove(above_chunk)
        
    if below:
        below_chunk = max(below,key=lambda x:x.centerbbox[0])
        char.sub = below_chunk
        list_of_chunks.remove(below_chunk)
    
    #find horizontal next chunk to attach
    next = None
    min_ = float("inf")
    for other_chunk in list_of_chunks:
        if char in other_chunk.childs:
            continue
        if other_chunk.centerbbox[0] < char.bbox[0]:
            pass
        else :
            mid_diff = (other_chunk.bbox[1]+other_chunk.bbox[3]-char.bbox[1]-char.bbox[3])/(char.bbox[3]-char.bbox[1])
            if min_ > mid_diff:
                next = other_chunk
                min_ = mid_diff
    if next:
        char.elements = [next]
        list_of_chunks.remove(next)
    char.complete = True

#call clean_chunk()
def clean_empty(list_of_chunks:list[Chunk]):
    temp_list = []
    for chunk in list_of_chunks:
        clean_chunk(chunk)
        if chunk.childs:
            temp_list.append(chunk)
    return temp_list    

#remove None marked Char and empty Chunk
def clean_chunk(chunk:Chunk):
    temp = []
    for char in chunk.childs:
        if char.char:
            temp.append(char)
            if char.sub:
                clean_chunk(char.sub)
                if char.sub.childs == None:
                    char.sub = None
            if char.sup:
                clean_chunk(char.sup)
                if char.sup.childs == None:
                    char.sup = None
    if temp:
        chunk.childs = temp
    else:
        chunk.childs = None

#after merging big operator is a good time to check if previous fraction merge if wrong
def check_frac_relation(char:Char):
    width = (char.elements[0].childs[0].bbox[2]-char.elements[0].childs[0].bbox[0]+char.elements[1].childs[0].bbox[2]-char.elements[1].childs[0].bbox[0])/2
    height = (char.elements[0].centerbbox[1]-char.elements[0].centerbbox[3]+char.elements[1].centerbbox[1]-char.elements[1].centerbbox[3])/2
    mid = (char.bbox[1]+char.bbox[3])/2
    fake_bbox = (char.bbox[0],mid-height/2,char.bbox[0]+width,mid+height/2)
    if char.chunk.childs[0] == char and char.chunk.parent.chunk.parent:
        relation = det_relation(char.chunk.parent.bbox,fake_bbox,True)
        relation_2 = det_relation(char.chunk.parent.chunk.parent.bbox,fake_bbox,True)
        if relation == None and relation_2 == "Normal":
            temp = char.chunk
            ppos = temp.parent.chunk.childs.index(temp.parent)
            if ppos == len(temp.parent.chunk.childs)-1:
                for ch in temp.childs:
                    temp.parent.chunk.merge(ch)
            else :
                temp.parent.chunk.childs = temp.parent.chunk.childs[:ppos] + temp.childs + temp.parent.chunk.childs[ppos:]
        if char.chunk.parent.sup == char.chunk:
            char.chunk.parent.sup = None
        else :
            char.chunk.parent.sub = None
    else:
        pos = char.chunk.childs.index(char)
        relation = det_relation(char.chunk.childs[pos-1].bbox,fake_bbox,True)
        relation_2 = det_relation(char.chunk.parent.bbox,fake_bbox,True)
        if relation == None and relation_2 == "Normal":
            temp = char.chunk
            ppos = temp.parent.chunk.childs.index(temp.parent)
            if ppos == len(temp.parent.chunk.childs)-1:
                for ch in temp.childs[pos:]:
                    temp.parent.chunk.merge(ch)
            else :
                temp.parent.chunk.childs = temp.parent.chunk.childs[:ppos] + temp.childs[pos:] + temp.parent.chunk.childs[ppos:]

            temp.childs = temp.childs[:pos]

#merge display big operator
def display_symbol_merge(list_of_chunks:list[Chunk]):
    for chunk in list_of_chunks:
        if chunk.childs[-1].display:
            if chunk.childs[-1].char == "\\int":
                char = chunk.childs[-1]
                above = [] #type: list[Chunk]
                below = [] #type: list[Chunk]
                for other_chunk in list_of_chunks:
                    if char in other_chunk.childs:
                        continue
                    if other_chunk.centerbbox[0] < char.bbox[0]:
                        pass
                    else :
                        mid_diff = (other_chunk.bbox[1]+other_chunk.bbox[3]-char.bbox[1]-char.bbox[3])/(char.bbox[3]-char.bbox[1])
                        if 0.3 < mid_diff < 2:
                            above.append(other_chunk)
                        elif -0.3 > mid_diff > -2:
                            below.append(other_chunk)
                
                if above:
                    above_chunk = min(above,key=lambda x:x.centerbbox[0])
                    char.sup = above_chunk
                    list_of_chunks.remove(above_chunk)
                    
                if below:
                    below_chunk = max(below,key=lambda x:x.centerbbox[0])
                    char.sub = below_chunk
                    list_of_chunks.remove(below_chunk)
            else:
                char = chunk.childs[-1]
                above = [] #type: list[Chunk]
                below = [] #type: list[Chunk]

                for other_chunk in list_of_chunks:
                    if char in other_chunk.childs:
                        continue
                    if other_chunk.centerbbox[2] < char.bbox[0] or other_chunk.centerbbox[0] > char.bbox[2]:
                        pass
                    elif other_chunk.centerbbox[1]+other_chunk.centerbbox[3] > char.bbox[1]+char.bbox[3] :
                        above.append(other_chunk)
                    else:
                        below.append(other_chunk)
                
                above_chunk = min(above,key=lambda x:x.centerbbox[1])
                below_chunk = max(below,key=lambda x:x.centerbbox[1])
                
                if above:
                    char.sup = above_chunk
                    list_of_chunks.remove(above_chunk)
                    
                if below:
                    char.sub = below_chunk
                    list_of_chunks.remove(below_chunk)

    return list_of_chunks

#merge to column first then merge columns
def array_merge(list_of_chunks:list[Chunk]):
    ALIGN_THRESH = 1
    list_of_chunks.sort(key = lambda x:x.centerbbox[0])
    flag = False
    left_align = [] #type: list[list[Chunk]]

    for i,chunk in enumerate(list_of_chunks[:-1]):
        if -ALIGN_THRESH < chunk.centerbbox[0] - list_of_chunks[i+1].centerbbox[0] < ALIGN_THRESH :
            if flag :
                left_align[-1].append(list_of_chunks[i+1])
            else :
                left_align.append([chunk,list_of_chunks[i+1]])
                flag = True
        else :
            flag = False

    list_of_chunks.sort(key = lambda x:x.centerbbox[0]+x.centerbbox[2])
    flag = False
    center_align = [] #type: list[list[Chunk]]
    for i,chunk in enumerate(list_of_chunks[:-1]):
        if -ALIGN_THRESH*2 < chunk.centerbbox[0] + chunk.centerbbox[2] - list_of_chunks[i+1].centerbbox[0] - list_of_chunks[i+1].centerbbox[2] < ALIGN_THRESH*2 :
            if flag :
                center_align[-1].append(list_of_chunks[i+1])
            else :
                center_align.append([chunk,list_of_chunks[i+1]])
                flag = True
        else :
            flag = False

    list_of_chunks.sort(key = lambda x:x.centerbbox[2])
    flag = False
    right_align = [] #type: list[list[Chunk]]
    for i,chunk in enumerate(list_of_chunks[:-1]):
        if -ALIGN_THRESH < chunk.centerbbox[2] - list_of_chunks[i+1].centerbbox[2] < ALIGN_THRESH :
            if flag :
                right_align[-1].append(list_of_chunks[i+1])
            else :
                right_align.append([chunk,list_of_chunks[i+1]])
                flag = True
        else :
            flag = False

    for column in left_align:
        for chunk in column:
            for other_column in center_align:
                if chunk in other_column:
                    if len(column) > len(other_column):
                        other_column[:] = []
                    else:
                        column[:] = []
            for other_column in right_align:
                if chunk in other_column:
                    if len(column) > len(other_column):
                        other_column[:] = []
                    else:
                        column[:] = []
    
    for column in center_align:
        for chunk in column:
            for other_column in right_align:
                if chunk in other_column:
                    if len(column) >= len(other_column):
                        other_column[:] = []
                    else:
                        column[:] = []
    list_of_column = [] #type: list[Column_instence]
    for column in left_align:
        if column:
            list_of_column.append(Column_instence(column,"l"))
            for chunk in column:
                list_of_chunks.remove(chunk)
    for column in center_align:
        if column:
            list_of_column.append(Column_instence(column,"c"))
            for chunk in column:
                list_of_chunks.remove(chunk)
    for column in right_align:
        if column:
            list_of_column.append(Column_instence(column,"r"))
            for chunk in column:
                list_of_chunks.remove(chunk)
    
    l = len(list_of_column)
    for i in range(l):
        column = list_of_column[i]
        if column == None:
            continue
        group = [column]
        r = column.centerbbox[2]
        for j in range(i+1,l):
            other_column = list_of_column[j]
            if other_column == None:
                continue
            if len(column.element) == len(other_column.element):
                mid_diff = (other_column.centerbbox[1]+other_column.centerbbox[3]-column.centerbbox[1]-column.centerbbox[3])/(column.centerbbox[3]-column.centerbbox[1])
                d = other_column.centerbbox[0] - r
                if -0.2 < mid_diff < 0.2 and d < 20:
                    group.append(other_column)
                    r = other_column.centerbbox[2]
                    list_of_column[j] = None
                
        list_of_chunks.append(Array_instence(group))

    return list_of_chunks

#recauculate bbox of chunk, call bbox_adjust2()
def bbox_adjust(list_of_chunks:list[Chunk]):
    for chunk in list_of_chunks:
        bbox_adjust2(chunk)
    return list_of_chunks
        
def bbox_adjust2(chunk:Chunk):
    for char in chunk.childs:
        if char.sub:
            bbox_adjust2(char.sub)
            char.adjust(char.sub.centerbbox)
        if char.sup:
            bbox_adjust2(char.sup)
            char.adjust(char.sup.centerbbox)
        if char.elements:
            for element in char.elements:
                bbox_adjust2(element)
                char.adjust(element.centerbbox)
        chunk.adjust(char.bbox)
    pass

#to string and final adjustment
def list_of_chunk_to_str(list_of_chunks:list[Chunk]):
    Result = ""
    list_of_chunks.sort(key = lambda x:x.centerbbox[1],reverse=True)
    list_of_chunks.sort(key = lambda x:x.centerbbox[0])
    for chunk in list_of_chunks:
        Result += chunk.chunk2latex()

    Result = Result.replace("...","\\ldots")
    Result = Result.replace("\\cdot \\cdot \\cdot ","\\cdots")
    Result = Result.replace("\\neq =","\\neq")
    Result = Result.replace("\\mapsto\\rightarrow","\\mapsto")
    funcs = [
        'sin', 'cos', 'tan', 'cot', 'sec', 'csc',
        'exp', 'log',
        'det', 'diag', 'rank',
        'round', 'gcd', 'mod',
        'mean', 'std',
        'max',
        'arg', 'deg', 'dim',
        'Harr', "Jac", 'sgn',
        "ker", "len", "sup",
    ]

    funcs_with_slash = [("\\"+i,i) for i in funcs]
    for i in funcs_with_slash:
        Result = Result.replace(i[0],i[1],-1)
        Result = Result.replace(i[1],i[0],-1)
    
    return Result
