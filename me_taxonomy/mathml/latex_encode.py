import string
from pdfxml.me_taxonomy.latex.latex_punct import is_punct_late_val


special_latex2mathml = {
    '\\partial': "&PartialD;",
    '\\colon': ':',
    '\\slash': '/',
    '\\mapsto': '&map;',
    'fl': '&fllig;',
    'ff': '&fflig;',
    'fi': '&filig;',
    '\\cdots': '...',  # NOTE, TODO, marked as mtext

    '\\varpitchfork': '&pitchfork;',
    '\\overline': '&macr;',
    '\\rightarrow': '&rarr;',  # TODO, not sure whether its correct

    '\\ast': '*',

    '=': 'eq',
    '\\ne': 'neq',
    '>': 'gt',
    '<': 'lt',
    '\\geq': 'geq',
    '\\leq': 'leq',
    '\\equiv': 'equivalent',
    '\\approx': 'approx',

    '\\in': "in",
    "\\ni": "notin",
}


same_val_list = [
    '=', '+', '-', '*', '/', '>', '<', '|', '(', ')', '[', ']', '{', '}', '!',
]


def latex_val2mathml_encode(latex_val):
    if latex_val in special_latex2mathml:
        return special_latex2mathml[latex_val]
    if latex_val.startswith("\\"):
        return "&"+latex_val[1:]+";"
    if latex_val in same_val_list:
        return latex_val
    if is_punct_late_val(latex_val):
        return latex_val
    if latex_val.isdigit():
        return latex_val
    if latex_val in string.uppercase or latex_val in string.lowercase:
        return latex_val
    raise Exception("unknown latex symbol {}".format(latex_val))
