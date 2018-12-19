from pdfxml.InftyCDB.macros import CONS_EXIST_HOR, CONS_HOR, SCRIPT_LEVEL_SAME, SCRIPT_LEVEL_SAME_CENTER

constrain_id2name = {
    CONS_EXIST_HOR: "CONS_EXIST_HOR",
    CONS_HOR: "CONS_HOR",
    SCRIPT_LEVEL_SAME: "SCRIPT_LEVEL_SAME"
}


def affect_item2str(affect_item):
    """
    convert an affected item represented by index into the string representation

    :param affect_item: dict , but the affected item could be an id or a range
    :return:
    """
    # {'range': [l, r], 'type': CONS_EXIST_HOR}
    if affect_item['type'] == CONS_EXIST_HOR:
        return "ExistHor:[{}, {}]".format(affect_item['range'][0], affect_item['range'][1])
    elif affect_item['type'] == CONS_HOR:
        return "MustHor:[{}, {}]".format(affect_item['range'][0], affect_item['range'][1])
    elif affect_item['type'] == SCRIPT_LEVEL_SAME:
        return "ScriptLevelSame: {}".format(affect_item['id'])
    else:
        raise Exception("affected item")


#############
# data structures
#############
class ConfigConstraint:
    def __init__(self, idx, gt):
        """
        idx is about the position of the element that to constraint with

        all the constraints will be stored in the affect list

        :param idx:
        :param gt: the glyph type of the current char
        """
        self.id = idx
        self.type = gt
        self.affect_list = []

    def __str__(self):
        """
        TODO, map the type from integer marcos to the string description

        :return:
        """
        return "char at {} with glyph type {}: {}".format(
            self.id,
            self.type,
            self.affect_list)

    def __repr__(self):
        return self.__str__()

    def add_hor_constraint(self, l, r):
        """

        :param l: left boundary inclusive
        :param r: right boundary inclusive
        :return:
        """
        self.affect_list.append({'range': [l, r], 'type': CONS_HOR})

    def add_hor_exist_constraint(self, l, r):
        self.affect_list.append({'range': [l, r], 'type': CONS_EXIST_HOR})

    def add_same_script_level_constraint(self, j):
        self.affect_list.append({'id': j, 'type': SCRIPT_LEVEL_SAME})

    def add_same_script_level_center_constraint(self, j):
        self.affect_list.append({'id': j, 'type': SCRIPT_LEVEL_SAME_CENTER})

