
class Tree(object):
    """
    general tree data structure
    """
    @staticmethod
    def get_children(t):
        return t.children

    @staticmethod
    def get_label(t):
        return t.val

    def __init__(self, val="", arg_children=None):
        if not isinstance(val, str) and not isinstance(val, unicode):
            tttt =1
        assert isinstance(val, str) or isinstance(val, unicode)
        if arg_children is not None:
            for c in arg_children:
                #print c, isinstance(c, Tree)
                if c is None or not isinstance(c, Tree):
                    ttt = 1
                assert isinstance(c, Tree)  # should also be tree node
            self.children = arg_children
        else:
            self.children = []
        self.val = val
        self.info = {}
        self.parent = None

    def __str__(self):
        res = self.val+"\n"
        for child in self.children:
            child_str = str(child)
            for line in child_str.split("\n"):
                if line.strip() == "":
                    continue
                res += "\t"+line + "\n"
        return res

    def get_node_number(self):
        n = 1
        if len(self.children) == 0:
            n += 1
        else:
            for c in self.children:
                n += c.get_node_number()
        return n



    def label(self):
        return self.val

    def to_str(self, indent_level=0):
        tmp_str = "{}{}\n".format("\t"*indent_level, self.val)
        for child in self.children:
            tmp_str += child.to_str(indent_level+1)
        return tmp_str

    def to_dict(self):
        res_dict = {
            'val': self.val,
            'child': [c.to_dict() for c in self.children]
        }
        return res_dict

    def set_children(self, children):
        self.children = children
        for child in self.children:
            child.parent = self

    def add_children(self, child):
        self.children.append(child)
        child.parent = self

    def merge_child_val(self):
        return ''.join([child.val for child in self.children])

    def get_parent(self):
        return self.parent

    def get_last_child(self):
        if len(self.children) == 0:
            raise Exception("no children")
        return self.children[-1]

    def replace_last_child(self, child):
        if len(self.children) == 0:
            raise Exception("no children")
        self.children[-1] = child

    def get_all_descent(self, including_self=False):
        """

        :return:
        """
        descent_list = []
        descent_list.extend(self.children)
        for c in self.children:
            descent_list.extend(c.get_all_descent())
        #descent_list.append(self)
        return descent_list

    def get_all_path(self):
        next_exp_list, all_no_exp_list = self.get_all_path_internal()
        return all_no_exp_list

    def get_all_path_internal(self):
        """
        should return two parts, not expanding, and expanding.

        :return:
            the first part is need expand,
            the second part is not expanding and accum
        """
        if len(self.children) == 0:
            return [self.val], [self.val]

        all_exp_list, all_no_exp_list = [], []
        for child in self.children:
            exp_list, no_exp_list = child.get_all_path_internal()
            all_exp_list.extend(exp_list)
            all_no_exp_list.extend(no_exp_list)

        next_exp_list = []
        for path in all_exp_list:
            new_path = "{}_{}".format(path, self.val)
            next_exp_list.append(new_path)
            all_no_exp_list.append(new_path)

        return next_exp_list, all_no_exp_list
