from subprocess import check_output


def get_output(cmd_list):
    #cmd_list = ["latexmlmath", "--cmml=-", '{}'.format(latex_str)]
    res = check_output(cmd_list)
    return res
