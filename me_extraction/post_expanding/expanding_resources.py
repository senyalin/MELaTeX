
# all in latex value
expand_left_right_list = [
    '\\propto', '=', "\\ne", "\\approx", '\\sim',
    "=:", ":=", "\\equiv", "\\Leftrightarrow", '\\triangleq',
    '\\doteq', '\\cong', "\\leftrightarrow", '\\iff',
    '>', '<', '\\ll', '\\gg', '\\le', '\\ge',
    '\\leqq', '\\geqq', '\\prec', '\\succ',
    '\\triangleleft', '\\triangleright',
    '\\Rightarrow', '\\rightarrow',

    '\\supset', '\\subseteq', '\\subset', '\\supseteq',
    '\\supset', '\\Subset', '\\setminus',
    '\\in', '\\ni', '\\notin', '\\cup', '\\cap',

    '\\mid', '\\nmid',

    '\\or', '\\land',

    '\\to', '\\mapsto',
    '\\leftarrow', '<:', '<.',
    '\\vdash', '\\vDash',

    # OP
    '+', '\\pm', '\\mp', '\\times', '\\cdot','\\div',
    '\\oplus', '\\otimes', '\\ominus',
    '\\circ',
    '\\ltimes', '\\rtimes', '\\bowtie',
]


expand_left_sym_list = [
    '\\rangle'
]  # should have a left operand


expand_right_sym_list = [
    #'-', removed due to the confusion with hyphen
    '\\sqrt',
    '\\neg', '\\forall', '\\exists',
    '\\sum', '\\prod', '\\int', '\\oint', '\\coprod',
    '\\langle',
    '\\partial', '\\nabla',
]  # should have a right operand
