from pdfxml.me_taxonomy.latex.latex_glyph import y_list, xy_list, yz_list, xyz_list, hxy_list, hxyz_list


# TODO, move around
REL_H, REL_SUP, REL_SUB = range(3)
REV_REL_H, REV_REL_SUP, REV_REL_SUB = range(10, 13)
REL_UPPER, REL_UNDER = range(20, 22)
CONS_EXIST_HOR, CONS_HOR, SCRIPT_LEVEL_SAME, SCRIPT_LEVEL_SAME_CENTER = range(4)

rel_id2rel_str = {
    REL_H: "HORIZONTAL",
    REL_SUB: "RSUB",
    REL_SUP: "RSUP",
    REV_REL_H: "REV_HORIZONTAL",
    REV_REL_SUB: "REV_RSUB",
    REV_REL_SUP: "REV_RSUP",
    REL_UPPER: "UPPER",
    REL_UNDER: "UNDER"
}

rel_str2rel_id = {rel_str: rel_id for rel_id, rel_str in rel_id2rel_str.items()}


def rel_list2rel_list_str(rel_list):
    """
    for debugging usage

    :param rel_list:
    :return:
    """
    rel_str_list = [rel_id2rel_str[rel_id] for rel_id in rel_list]
    return "["+",".join(rel_str_list)+"]"

#########
# char shape type
#########
xy_greek_list = [
    'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta',
    'Eta', 'Theta', 'Iota', 'Kappa', "Lambda", 'Mu',
    'Nu', 'Xi', 'Omicron', "Pi", 'Rho', 'Sigma',
    'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega',
    "lambda"
]
y_greek_list = [
    'alpha', 'epsilon', 'iota', 'kappa',
    'nu', 'omicron', "pi",
    'sigma', 'tau', 'upsilon', 'omega',
]

xyz_greek_list = ['beta', 'zeta', 'xi']
xy_greek_list.extend( ['delta', 'theta', "lambda"] )  # lower case Greek symbols
yz_greek_list = [
    'gamma', 'eta', 'mu',  'rho', 'phi', 'chi', 'psi',
    'varphi',
]


# TODO, phi and varph
# varying width
vw_list = [
    'fractionalLine'
]

# varying height
vh_list = [
]

# varying size
vs_list = [
    'int', 'sum', 'prod', 'coprod',
    'bigwedge',
]

# binary operator
o_list = [
    'minus', 'plus', 'times', 'slash', 'backslash', 'pm', 'div', 'sqrt',

    'rightarrow', 'Rightarrow', 'Leftrightarrow', 'hookrightarrow',
    'downarrow', 'leftarrow',
    'mapsto',

    'ni', 'notin', 'in', 'subset', 'cup', 'cap', 'subseteq', 'supset', 'supseteq',
    'subsetnoteqq', 'supsetnoteqq', 'notsubset', 'nsubseteq',
    'bigcup', 'bigcap', 'bigoplus',

    'oplus', 'otimes', 'cdot', 'circ', 'rtimes',
    'nmid', # TODO, not quite sure about the meaning

    'wedge', 'vee',

    # latex version
    '-', '+', '*',
    "/", # division

    # below are unary operators
    'neg',
    'forall', 'exists',
    'partial', 'nabla',
]

decorator_list = [
    'perp', 'ast', 'star'
]

# relation
r_list = [
    'equal', 'geqq', 'leqq', 'less', 'leq', 'geq', 'greater','notequal',
    'equiv', 'notequiv',
    'cong', 'sim', 'simeq', 'approx',
    'preceq', 'prec', 'succ', 'succeq',
    'gg', 'll',
    '=', '>', '<'
]

# fence list
f_list = [
    'LeftPar', 'RightPar',
    'BigLeftPar', 'BigRightPar',
    'MiddleLeftPar', 'MiddleRightPar',
    'langle', 'rangle',
    'lfloor', 'rfloor',
    'lceil', 'rceil',

    # latex version
    '(', ')'
]

# digit
d_list =[
    'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',

    # latex version
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
]

# accent
a_list = [
    'hat', 'tilde', 'overline', 'check', 'vec',
    'underline', 'underbrace',
]

# punctuation
p_list = [
    'colon', 'semicolon',
    'comma', 'period',
    'bullet',
    'exclamation',
    'cdots', 'ldots', 'cdot', 'dot',
    ':', ';', ',', '.',
    'square', # end of a proof
    'hyphen', 'longHyphen', # TODO, using this list in the punct
]

# misc.
m_list = [
    'emptyset', 'infty', 'sharp',
    'smile', # in 28012476, just this symbol
    'fi', 'ff', 'fl',
    'aleph', 'eacute', 'Scheck', # euro symbols
]

# TODO list
t_list = [
    'vert',

    # TODO, speciall processing, mostly as the SUP of the left symbol.
    #'prime', 'doubleprime',
    # vertical oriented

    'ContinuedFraction',
    'SingleEndQuartation',
    'Scedil',

    'varpitchfork',
]

glyph_type_map = {
    "y_list": y_list,
    "y_greek_list": y_greek_list,
    "xy_list": xy_list,
    "xy_greek_list": xy_greek_list,
    "yz_list": yz_list,
    "yz_greek_list": yz_greek_list,
    "xyz_list": xyz_list,
    "xyz_greek_list": xyz_greek_list,
    "hxy_list": hxy_list,
    "hxyz_list": hxyz_list,
    "vw_list": vw_list,
    "vh_list": vh_list,
    "vs_list": vs_list,
    "o_list": o_list,
    "r_list": r_list,
    "f_list": f_list,
    "d_list": d_list,
    "a_list": a_list,
    "p_list": p_list,
    "t_list": t_list,
    'decorator_list': decorator_list
}

fraction_name_list = ["fractionalLine", "ContinuedFraction"]

# they are not used, but only to keep record here.
no_parent_me_idx_list = [
    # the parental relationship, annotation error
    # the solution is just find the one without parent and assign as -1 for the parent and the relation as top
    28016971,
    28017232,
    28017286,
    28017378,
    28017413,
    28017471,
    28017473,
    28017555,
    28017556,
    28017674,
    28017804,
    28017825,
    28017914,
    28017920,
    28017936,
    28017950,
    28017993, 28017995, 28018027, 28018028, 28018030, 28018032, 28018035, 28018038, 28018041, 28018052, 28018054,
    28018057, 28018060, 28018062, 28018064, 28018542, 28018564, 28018793, 28018947, 28019259, 28019401, 28019495,
    28019608, 28019687, 28019933, 28020316, 28020578, 28000083, 28001079, 28001081, 28001083, 28001085, 28001088,
    28001092, 28001912, 28002837, 28003218, 28003771, 28003782, 28003804, 28003887, 28003901, 28003916, 28004054,
    28004067, 28004304, 28004475, 28004476, 28004791, 28005149, 28005354, 28005622, 28005647, 28005657, 28005857,
    28005863, 28005883, 28005892, 28005906, 28005935, 28006005, 28006055, 28006286, 28006391, 28006526, 28006605,
    28007009, 28007088, 28007174, 28007204, 28007382, 28007482, 28007783, 28008004, 28008312, 28008593, 28008687,
    28009117, 28009418, 28009752, 28010214, 28010892, 28010898, 28011177, 28011813, 28011829, 28011834, 28011856,
    28011887, 28011932, 28012154, 28012223, 28012239, 28012354, 28012357, 28012374, 28012586, 28012606, 28012699,
    28012806, 28012895, 28012915, 28012934, 28012942, 28013005, 28013010, 28013134, 28013272, 28013337, 28013408,
    28013722, 28013893, 28014199, 28014477, 28014694, 28014711, 28014809, 28014919, 28015296, 28015490, 28015894, 28016365
]

skip_me_idx_list = [
    28017662, 28017664, # might be the mis labeling of the overline and the fractionalline
    28006261, # more chars under the underbrace, to be done later

    # fence with empty
    28000087,
    28000096,
    28000245,
    28000423,
    28000429,
    28016715,

    28007076,  # not sure the semantic
    28010516,
    28010517,
    28020612,  # the f is overlapping too much with the fence

    # hat with empty
    28000494,

    # under of word
    #28009688,

    # inconsistency
    28002861,  # the radical symbol does not include the radical line in this case.
    28002861,  # the sqrt symbol and path are extra

    # TODO, very hard cases
    28001911,

    28013072,  # symbol error? slash to |
    28015166,  # guess error at checking free vertbar
    28020564,  # guess that mis label the overline as fraction.
    #28020612,  # very strange, should work
    28020242,  # the accent processing might be to strict, some char go over the accent.
    28000497,  # 1. empty accent, 2. paired vert bar not for fencing



    # vertical bar fence issue
    28018425,  # vertical bar as eval at, but two vertical bar match as a pair.

    # missing element
    28014694,  # 498411 not marked as math

    # TODO, long chain could not resolve
    28020296,
    28020379,
    28020384,
    28020514,
    28009851,  # 1M

    28011343,  # still too long even after the attempt to split? also there are many upper relationship for the arrow operator
]

# seem to fixed the issue for now
#skip_me_idx_list.extend(no_parent_me_idx_list)