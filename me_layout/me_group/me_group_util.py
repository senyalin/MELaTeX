def skip_single_hor(mg):
    """
    TODO, where is this function used?
    :param mg:
    :return:
    """
    from pdfxml.me_layout.me_group.hor_me_group import MEHorGroup
    if isinstance(mg, MEHorGroup) and len(mg.me_groups) == 1:
        return skip_single_hor(mg.me_groups[0])
    return mg