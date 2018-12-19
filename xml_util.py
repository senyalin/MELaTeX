"""
https://docs.python.org/2/library/xml.dom.html#documenttype-objects
"""
BAD_vlist = [
        0, 1, 2, 3, 4, 5, 6, 7, 8,
        11, 12,
        14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
        # Two are perfectly valid characters but go wrong for different reasons.
        # 38 is '&' which gives: xmlParseEntityRef: no name.
        # 60 is '<' which gives: StartTag: invalid element namea different error.
    ]


def clean_xml(xml_path, out_path=None):
    """
    This is done on the exported XML file for the PDF structurelization
    :param xml_path:
    :return:
    """

    content = open(xml_path).read()
    char_list = []
    for c in content:
        #print c
        v = ord(c)
        #print c, v
        if not v in BAD_vlist:
            char_list.append(c)
    tmp_str = "".join(char_list)
    if out_path is None:
        out_path = xml_path
    with open(out_path, 'w') as f:
        print>>f, tmp_str
