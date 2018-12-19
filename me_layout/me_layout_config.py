"""
Will affect results
 1. What constraints to add?
 1.1 HOR constraint
 1.2 HOR exist constraint
 1.3 MEGroup Script level same
 1.4 Symbol script level same

 2. The script configuration model, currently only allow for hor/sup/sub, but also require not sup/sub at the same time.

 3. whether the operators, relation symbols, punctuation be included in the pairs.
    they are less likely to contribute to the probability assessment, due to their irregular shape

 4. when attach the local configuration of the hole to the parent
    not add both sup & sub,
    rather, add based on the comparison of the center difference

Will affect speed only
 Z1. whether common pairs among different config is removed, child parent relation chain
 2.
"""


# the reason it works in the past is because we have many rules for it.
# TODO, the option A3 is not good, need more refined probability analysis.
#OPTION_A_3_NO_OP_PUNCT_REL_PAIR_PROB = True
OPTION_A_3_NO_OP_PUNCT_REL_PAIR_PROB = False

OPTION_Z1_REMOVE_COMMON_CPRC = False  # not improving the performance.
MAX_DIFF = None  # it will affect the results, at least on the test case.
OPTION_A_4_LOCAL_CONFIG_BY_CENTER = True

# the following is special for the simulation based density estimation
default_sample_num = 50

# Below are the new ones

enable_op_constraint = False
enable_center_line_constraints = True  # during the enumeration of layout configuration

enable_boundary_by_centerline_for_ss = True  # enable the boundary detection of both super/sub structure
center_band_threshold = 0.1

horizontal_consecutive_width_ratio = 2  # the spacing should not be larger than twice the size of the hoziontal

disable_hr_nvcd_for_non_regular = True
#disable_hr_nvcd_for_non_regular = False
# because the non-regular char might be with different aspect ratio, if centered, still good.
# the HR is valid if both are regular
# the NVCD is valid if the base is regular and the next is centered.

# TODO, except for varying size,
# the wide symbols should estimate the height by the width
# the tall or square symbol should use the height to adjust.


