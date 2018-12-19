
def xw_format_string(template, args):
    #print args

    tmp_list = []
    for arg in args:
        if isinstance(arg, str):
            arg = arg.decode('utf-8', 'ignore').encode('utf-8', 'ignore')
            tmp_list.append(arg)
        elif isinstance(arg, unicode):
            arg = arg.encode('utf-8', 'ignore')
            tmp_list.append(arg)
        else:
            tmp_list.append(arg)
    return template.format(*tmp_list)


def xw_join_string(delimeter, str_list):
    tmp_list = []
    for s in str_list:
        if isinstance(s, str):
            s = s.decode('utf-8', 'ignore').encode('utf-8', 'ignore')
            tmp_list.append(s)
        elif isinstance(s, unicode):
            s = s.encode('utf-8', 'ignore')
            tmp_list.append(s)
        else:
            tmp_list.append(str(s))
    return delimeter.join(tmp_list)


def xw_indent_string(content, indent_num=1):
    res = ""
    the_indent_str = ''.join(["\t"]*indent_num)
    for line in content.split("\n"):
        res += the_indent_str+line+"\n"
    return res



if __name__ == "__main__":
    print xw_format_string("{} {}", [1, 2])
