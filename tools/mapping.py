
from tools.class_define import *


numbers = {
    "zero":"0",
    "one":"1",
    "two":"2",
    "three":"3",
    "four":"4",
    "five":"5",
    "six":"6",
    "seven":"7",
    "eight":"8",
    "nine":"9",
}
small_brackets = {
    "braceleft": "\\{",
    "braceright": "\\}",
    "bracketleft": "[",
    "bracketright": "]",
    "parenleft": "(",
    "parenright": ")",

    "angbracketright": "\\rangle ",
    "angbracketleft": "\\langle ",
}
medium_brackets = {
    "braceleftbig": "\\left\\{",
    "bracketleftbig": "\\left[",
    "parenleftbig": '\\left(',
    "bracerightbig": "\\right\\}",
    "bracketrightbig": "\\right]",
    "parenrightbig": '\\right)',

    "braceleftbigg": "\\left{",
    "bracketleftbigg": "\\left[",
    "parenleftbigg": '\\left(',
    "bracerightbigg": "\\right}",
    "bracketrightbigg": "\\right]",
    "parenrightbigg": '\\right)',

    "braceleftBig": "\\left\\{",
    "bracketleftBig": "\\left[",
    "parenleftBig": '\\left(',
    "bracerightBig": "\\right\\}",
    "bracketrightBig": "\\right]",
    "parenrightBig": '\\right)',

    "braceleftBig": "\\left{",
    "bracketleftBigg": "\\left[",
    "parenleftBigg": '\\left(',
    "bracerightBigg": "\\right}",
    "bracketrightBigg": "\\right]",
    "parenrightBigg": '\\right)',
}
big_brackets_top = {
    "\\bracelefttp": "\\left{",
    "\\bracketlefttp": "\\left[",
    "\\parenlefttp": '\\left(',
    "\\bracerighttp": "\\right}",
    "\\bracketrighttp": "\\right]",
    "\\parenrighttp": '\\right)',
    "\\vextendsingle": "|"
}

big_brackets_middle = {
    "\\braceleftmid": "\\left{",
    "\\bracketleftmid": "\\left[",
    "\\parenleftmid": '\\left(',
    "\\bracerightmid": "\\right}",
    "\\bracketrightmid": "\\right]",
    "\\parenrightmid": '\\right)',
    
}

big_brackets_bottom = {
    "\\braceleftbt": "\\left{",
    "\\bracketleftbt": "\\left[",
    "\\parenleftbt": '\\left(',
    "\\bracerightbt": "\\right}",
    "\\bracketrightbt": "\\right]",
    "\\parenrightbt": '\\right)',
}

big_brackets_extend = {
    "\\braceex": "",
    "\\parenleftex": "",
    "\\parenrightex": "",

}

big_bracket_element = {
    "\\left{",
    "\\left[",
    '\\left(',
    "\\right}",
    "\\right]",
    '\\right)',
}

big_bracket_left = {
    "\\left{",
    "\\left[",
    '\\left(',
}

big_operator_display = {
    "intersectiondisplay":"\\bigcap ",
    "summationdisplay":"\\sum ",
    "integraldisplay" : "\\int",
    "productdisplay" : "\\prod",
}

big_operator_inline = {
    "summationtext":"\\sum",
    "integraltext" : "\\int"
}

big_operator = big_operator_display | big_operator_inline

big_integral = {
    "integraldisplay" : "\\int",
}

big_brackets_old = {

    # brace
    "braceleftBig": "\\{",
    "bracerightBig": "\\}",
    "bracehtipupleft": "\\{",
    "bracehtipupright": "\\}",
    "bracehtipdownleft": "\\{",
    "bracehtipdownright": "\\}",
    "braceleftbt": "\\{",
    "bracerightbt": "\\}",
    "braceleftbigg": "\\{",
    "braceleftBigg": "\\{",
    "bracerightbigg": "\\}",
    "bracerightBigg": "\\}",
    "braceleftbig": "\\{",
    "bracerightbig": "\\}",
    "bracelefttbt": "\\{",
    "bracerighttbt": "\\}",
    "braceleftmid": "\\{",
    "bracerightmid": "\\}",
    "bracelefttp": "\\{",
    "bracerighttp": "\\}",

    # square bracket
    "bracketleftbt": "[",
    "bracketrightbt": "]",
    "bracketleftex": "[",
    "bracketrightex": "]",
    "bracketlefttp": "[",
    "bracketrighttp": "]",
    'bracketrightBig': ']',
    'bracketleftBig': '[',
    'bracketleftbigg': '[',
    'bracketrightbigg': ']',
    'bracketleftbig': "[",
    'bracketrightbig': "]",
    'bracketleftbg': "[",
    'bracketrightbg': "]",
    'largellbracket': '[',
    'largerrbracket': ']',
    'llbracket': '[',
    'rrbracket': ']',
    'bracketleftBigg': '[',
    'bracketrightBigg': ']',

    # parenthesis
    "parenleftbig": "(",
    "parenrightbig": ")",
    
    "parenleftbigg": "(",
    "parenrightbigg": ")",
    "parenlefttp": '(',
    "parenrighttp": ')',
    'parenleftBig': "(",
    'parenrightBig': ")",
    "LeftPar": "(",
    "RightPar": ")",
    "parenrightBigg": ")",
    "parenleftBigg": "(",
    "BigRightPar": ")",
    "BigLeftPar": "(",
    "MiddleRightPar": "}",
    "MiddleLeftPar": "{",
    "parenleftex": "(",
    "parenrightex": ")",
    "parenleftbt": "(",
    "parenrightbt": ")",

}
topping = {
    "circumflex" : "\\hat",
    "macron": "\\bar",
    "dotaccent": "\\dot",
    "vector": "\\vec ",
    "\\tilde": "\\tilde",
}
punct_name = {
    "minusplus": "\\mp ",
    "lscript": "\\ell ",
    "arrowdblboth": "\\Leftrightarrow ",
    
    "logicaland" : "\\wedge ",
    "approxequal": "\\approx ",
    "dieresis": "\\ddot ",
    "vee": "\\logicalor ",
    "slash": "/",
    "circleplus": "\\oplus ",
    "reflexsubset": "\\subseteq ",

    "partialdiff": "\\partial ",
    
    "openbullet": "\\circ ",
    "triangleinv": "\\triangledown ",
    "planckover2pi1": "\\hbar ",
    "backslash": "\\setminus ",
    "at": "@",
    "question": "?",
    "ampersand": "&",
    "periodcentered": "\\cdot ",
    "period": '.',
    "colon": ":",
    "semicolon": ";",
    "comma": ",",
    "percent": "%",
    "sharp": "\\#",
    "exclamdown" : "!",
    "epsilon1" : "\\epsilon ",
    "phi1" : "\\varphi ",
    "...":"ldots",
    "asteriskmath" : "*",
}

arithmic = {
    "radicalBigg":"\\radical",
    "radicalBig":"\\radical",
    "triangleleftequal":"\\unlhd",
    "less":"<",
    "greater":">",
    "plusminus":"\\pm ",
    "circlemultiply": "\\otimes ",
    "greatermuch" : "\\gg ",
    "similarequal" : "\\simeq ",
    "greaterorsimilar" : "\\gtrsim ",
    "lessorsimilar" : "\\lesssim ",
    "negationslash":"\\neq ",
    "infinity":"\\infty ",
    "multiply": "\\times ",
    "element": "\\in ",
    "lessequal": "\\leq ",
    "greaterequal": "\\geq ",
    "intersection": "\\cap ",
    "union": "\\cup ",
    "bar": "|",
    "equal": "=",
    "minus": "-",
    "plus": "+",
    "circledot":"\\odot ",
    "arrowright":"\\rightarrow ",
    "similar":"\\sim ",
    "perpendicular":"\\perp ",
    "equivalence":"\\equiv ",
    "lessmuch":"\\ll ",
    "universal": "\\forall",
    "square": "\\Box ",
}

radical = {
    "\\radical",
    "\\radicalbig",
}

special_operator = {
    
}

keywords = {
    # "dim" : "\\dim{",
}

big_element = big_bracket_element | set((big_operator | big_integral).values())

def first_mapping(char:str)->str:
    mapping = numbers | small_brackets | medium_brackets | punct_name | arithmic | big_operator | big_integral | topping
    if char in mapping.keys():
        if char == "\\radicalBigg":
            pass
        return mapping[char]
    elif len(char)>1 or char in "{}":
        return "\\"+char
    else:
        return char

def is_big_symbol(char:Char)->bool:
    big_brackets = big_brackets_top | big_brackets_middle | big_brackets_bottom | big_brackets_extend
    if char.char in big_brackets.keys():
        return True
    else:
        False
