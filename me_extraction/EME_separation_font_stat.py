"""
The probability of a "word" (non seperable) is the product of each char
"""
debug = True

def create_me_font_condprob(font_stat_dict):
    """
    create the conditional probability, with add one to avoid zero probability?
    What if there is zero probability? log will not work
    """
    res_dict = font_stat_dict
    font_names = res_dict['me_font2count'].keys()
    font_names.extend(res_dict['nme_font2count'].keys())
    font_names = set(font_names)

    add_delta = 1e-4
    fn2me_cp = {}
    for font_name in font_names:
        me_c = res_dict['me_font2count'][font_name] if res_dict['me_font2count'].has_key(font_name) else 0
        nme_c = res_dict['nme_font2count'][font_name] if res_dict['nme_font2count'].has_key(font_name) else 0
        me_c += add_delta
        nme_c += add_delta
        fn2me_cp[font_name] = me_c / (me_c+nme_c)

    return fn2me_cp


if __name__ == '__main__':
    pass
