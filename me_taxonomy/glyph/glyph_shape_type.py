# based on the latex values,
# as the glyph name varies a lot

print("TODO, manually construct such table glyph_shape_type.py")

# group based on function and glyph types
# there are many that is visually similar, but their latex commands is different.

# GT_HEIGHT_STABLE means the regular shaped, such as their height could be estimated.
GT_HEIGHT_STABLE, GT_WIDTH_STABLE, GT_CENTERED, GT_NON_STABLE = range(4)

height_stable = [
    '+', "\\pm", "\\mp", "\\times", "\\rtimes", "\\ltimes",
    "\\dagger", "\\ddagger",
    "\\ominus",

    # relation expression
    "<", "\\le", "\\ll", "\\subset", "\\subseteq", "\\sqsubset", "\\sqsubseteq", "\\in", "\\prec", "\\preceq", "\\leq",
    "\\nleq", "\\nless", "\\lneq", "\\lneqq", "\\notin", "\\nsubseteq", "\\leqq",
    ">", "\\ge", "\\gg", "\\supset", "\\supseteq", "\\sqsupset", "\\sqsupseteq", "\\ni", "\\succ", "\\succeq", "\\geq",
    "\\ngeq", "\\ngtr", "\\gneq", "\\gneqq", "\\nsupseteq", "\\geqq",
    "\\neq",
    "\\parallel", "\\perp", "\\mid", "\\nmid"
    "\\nparallel",
    #"\\not",

    # dash
    "\\vdash", "\\dashv", "\\perp",

    # vertical dots
    '\\ddots', '\\iddots', '\\vdots', ';', ':', '!', '?', '%',

    # arrows vertically
    "\\uparrow", "\\Uparrow", "\\downarrow", "\\Downarrow",
    "\\updownarrow", "\\Updownarrow",
    "\\nearrow", "\\searrow", "\\swarrow", "\\nwarrow",

    # special values
    "\\infty", "\\emptyset", "\\aleph",

    #
    "\\square", "\\blacksquare", "\\Join",

    # special values
    'fl', 'ff', 'fi',
    "\\pitchfork",  # like \Psi

    "\\exists", "\\forall",
    "\\partial", "\\nabla",

    '\\top', '\\intercal', # commonly used for matrix transpose

    '@', '$',
]

# add greeks, letters, digits
import string
from pdfxml.me_taxonomy.latex.latex_glyph import greek_list
height_stable.extend(greek_list)
for c in string.letters:
    height_stable.append(c)
for c in string.digits:
    height_stable.append(c)



# for width stable character, the total height is decide by the width and the ratio
# the lower and upper bound is decided by the normalized height and the upper, lower ratio.
# character in with width stable might still be height stable
# not complete
width_stable = [
    # operations
    '\\div',

    # relation
    "-", #"\\minus",
    "=", "\\doteq", "\\cong", "\\equiv",
    "\\ncong",
    "\\sim", "\\simeq", "\\approx", "\\asymp",
    "\\nsim",
    "\\smile", "\\frown",

    "\\neg",
]


varying_size_centered = [
    "\\amalg",
    "\\sum", "\\int", "\\oint",
    "\\prod", "\\coprod",
    "\\cap", "\\cup", "\\bigcap", "\\bigcup",
    "\\sqcap", "\\sqcup", "\\bigsqcap", "\\bigsqcup",
    "\\vee", "\\wedge", "\\bigvee", "\\bigwedge",

    # division
    "\\\\", "\\setminus", "/", "\\backslash",

    # not
    "\\not\\in",
    "\\not\\equiv", "\\not<", "\\not>", "\\not=",
    "\\not\\le", "\\not\\ge", "\\not\\sim",
    "\\not\\approx", "\\not\\cong", "\\not\\parallel",

    # relation
    "\\propto", "\\bowtie", "\\models",

    # O-element
    "\\odot", "\\bigodot", "\\otimes", "\\bigotimes",
    "\\oplus", "\\uplus", "\\bigoplus", "\\biguplus",
    "\\oslash",
    "\\bigcirc"
    
    # triangles
    "\\lhd", "\\triangleleft", '\\unlhd',
    '\\rhd', "\\triangleright", '\\unrhd',

    # misc
    '\\Diamond', "\\Box", "\\wr",

    # fence
    #"\\bar",
    "|", "\\nmid",
    '||', # norm
    "(", ")", "[", "]", "{", "}",
    "\\rangle", '\\langle', "\\lceil", "\\rceil", "\\rfloor", "\\lfloor",
]

centered_could_not_estimate_height = [
    '\\cdot', '\\ast',  '\\cdots',

    '\\star', '\\bigstar', "\\natural", "\\sharp",
    "\\circ", "\\bullet", '\\diamond', "\\copyright", "\\smiley", "\\cancer",

    # arrow could not be estimated because the width might vary

    "\\leftarrow", "\\Leftarrow", "\\gets", "\\mapsto", "\\hookleftarrow", "\\longleftarrow", "\\Longleftarrow",
    "\\longmapsto", "\\leadsto",
    "\\rightarrow", "\\Rightarrow", "\\to", "\\longrightarrow", "\\Longrightarrow", "\\hookrightarrow",
    "\\leftrightarrow", "\\Leftrightarrow", "\\rightleftharpoons", "\\longleftrightarrow", "\\Longleftrightarrow",

    "\\frac",
]

non_stable = [
    # sqrt
    '\\sqrt',

    # triangles
    '\\bigtriangleup',
    "\\bigtriangledown", "\\triangledown",

    "\\bumpeq", "\\lnsim",

    # punctuation
    "\\prime", "'", "''", "\\dprime",
    "\\degree",
    ",", ".", '\\dots', "\\ldots",

    # strange arrow
    "\\leftharpoonup", "\\leftharpoondown", "\\rightharpoonup", "\\rightharpoondown",

    # accent
]
from pdfxml.me_taxonomy.math_resources import accent_name_list, under_name_list
non_stable.extend(["\\"+accent_name for accent_name in accent_name_list])
non_stable.extend(['\\'+under_name for under_name in under_name_list])


glyph_category_list = [
    "height_stable", "width_stable", "varying_size_centered",
    "centered_could_not_estimate_height", "non_stable"
]


glyph_category2gt_type = {
    "height_stable": GT_HEIGHT_STABLE,
    "width_stable": GT_WIDTH_STABLE,
    "varying_size_centered": GT_CENTERED,
    "centered_could_not_estimate_height": GT_CENTERED,
    "non_stable": GT_NON_STABLE
}


glyph_category2char_list = {
    "height_stable": height_stable,
    "width_stable": width_stable,
    "varying_size_centered": varying_size_centered,
    "centered_could_not_estimate_height": centered_could_not_estimate_height,
    "non_stable": non_stable,  # just irregular
}


latex_val2gt = None
def get_latex_val2gt():
    global latex_val2gt
    if latex_val2gt is None:
        # prepare it
        latex_val2gt = {}
        for gt_str, char_list in glyph_category2char_list.items():
            for c in char_list:
                latex_val2gt[c] = glyph_category2gt_type[gt_str]
    return latex_val2gt


def get_gt_type_by_latex_val(latex_val):
    l2g = get_latex_val2gt()
    if latex_val.startswith("\\not"):
        return l2g["\\not\\in"]

    if latex_val.startswith("\\mathcal"):
        latex_val = latex_val[latex_val.index("{")+1:latex_val.index("}")]

    if latex_val not in l2g:
        # TODO: \not, similar with \backslash
        raise Exception("unknown latex command {}".format(latex_val))

    return l2g[latex_val]


def check_conflict():
    """
    one symbols could not be placed into multiple
    :return:
    """
    #glyph_category2char_list

    pass


def export_latex_table():
    """
    regular shaped,
     - xy
     - y
     - yz
     - xyz
     - depends, for example f vs \italic{f}

    irregular shaped,
     - varying size, but centered.
     -

    :return:
    """

    # TODO, they are not printable using the existing normal package.
    ignore_latex_list = [

    ]

    #def latex
    def val2latex(c):
        if c == "\\\\":
            return "\\backslash"
        if c == "\\sqrt":
            return "\\sqrt{}"
        if c in ["{", "}"]:
            return "\\"+c
        if c[1:] in accent_name_list or c[1:] in under_name_list:
            return c+"{}"
        return c

    from pdfxml.path_util import PROJECT_FOLDER
    out_path = "{}/dissertation/templates/meca/me_layout/gen/glyph_table.tex".format(PROJECT_FOLDER)
    with open(out_path, 'w') as f:
        for gc in glyph_category_list:
            #for gc, char_list in glyph_category2char_list.items():
            char_list = glyph_category2char_list[gc]
            tmp_char_list = []
            for c in char_list:
                if c in greek_list:
                    continue
                if len(c) == 1 and (c in string.letters or c in string.digits):
                    continue
                tmp_char_list.append(c)
            char_list = tmp_char_list
            val_list = "\n".join(["${}$".format(val2latex(c)) for c in char_list])

            print "{} & {} \\\\".format(gc.replace("_", "\\_"), val_list)
            print>>f, "{} & {} \\\\".format(gc.replace("_", "\\_"), val_list)
            if gc == "height_stable":
                print "{} & {} \\\\".format("", "Greek, Alphabets, Digits")
                print>>f, "{} & {} \\\\".format("", "Greek, Alphabets, Digits")
        pass


if __name__ == "__main__":
    check_conflict()
    export_latex_table()