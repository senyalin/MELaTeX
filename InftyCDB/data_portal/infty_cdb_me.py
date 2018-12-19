"""
A possible test case, 15_019.png_1422_1449_2146_1753

The core part of this file is a class to describe the ME structure from inftyCDB.
"""
from pdfxml.InftyCDB.data_portal.data_portal_split_chars import load_chars_by_me_idx
from pdfxml.ds_graph_util import XWGraph


def build_cid2chars_pid2cidlist(chars):
    """
     as the first step of building the hierarchy

    :param chars:
    :return:
    """
    cid2chars = {}
    pid2cid_list = {}
    for c in chars:
        cid2chars[c['cid']] = c
        if not pid2cid_list.has_key(c['pid']):
            pid2cid_list[c['pid']] = []
        pid2cid_list[c['pid']].append(c['cid'])
    for c in chars:
        if not pid2cid_list.has_key(c['cid']):
            pid2cid_list[c['cid']] = []
    return cid2chars, pid2cid_list


class InftyCDBME:
    """
    Notation:
        cid, char id in the Infty CDB
        TODO,
            how is the group working?
            how are different group attached?
    """
    def __init__(self):
        """
        will it allow?
        :param chars:
        """
        self.debug = False

        # internal
        self.chars = None
        self.cid2chars = None  # get char info as dict
        self.pid2cid_list = None

        # interface
        self.hor_groups = None  # list of (list of cid, hor chain)
        self.cid2gid_rel = None  # store the group id and the relation to the parent
        self.root_g_id = None  # the group that is the root?

    def init_from_char(self, chars):
        """
        three stage,
            1. horizontal grouping
            2. iteratively identify sub-sup
            3. iteratively identify over/under

        :param chars: list of chars
        :return:
        """
        self.chars = chars
        self.cid2chars, self.pid2cid_list = build_cid2chars_pid2cidlist(chars)
        # pid2cid_list is used for reconstruct the left to right horizontal order

        if self.debug:
            for pid, cid_list in self.pid2cid_list.items():
                print pid, cid_list

        self.init_from_char_stage1()
        self.init_from_char_stage2_3()

    def build_cid2chars_pid2cidlist(chars):
        """
         as the first step of building the hierarchy

        :param chars:
        :return:
        """
        cid2chars = {}
        pid2cid_list = {}
        for c in chars:
            cid2chars[c['cid']] = c
            if not pid2cid_list.has_key(c['pid']):
                pid2cid_list[c['pid']] = []
            pid2cid_list[c['pid']].append(c['cid'])
        for c in chars:
            if not pid2cid_list.has_key(c['cid']):
                pid2cid_list[c['cid']] = []
        return cid2chars, pid2cid_list

    def init_from_char_stage1(self):
        """
        abstract it as a connected component discovery problem in graph

        fill self.hor_groups with elements

        :return:
        """
        cid_list = [char['cid'] for char in self.chars]

        # only gather the horizontal relation here
        edges = []
        for char in self.chars:
            cid = char['cid']
            pid = char['pid']
            if pid == -1:
                continue

            if pid not in cid_list:
                print pid, cid_list

                raise Exception("parent missing")

            if char['relation'] != "HORIZONTAL":
                continue
            edges.append((cid_list.index(cid), cid_list.index(pid)))

        g = XWGraph()
        g.init_by_edges(edges, len(cid_list))
        groups = g.find_connected_components()
        self.hor_groups = []
        for idx_list in groups:
            self.hor_groups.append([cid_list[idx] for idx in idx_list])
        self.init_from_char_stage1_build_order()

    def init_from_char_stage1_build_order(self):
        """
        rebuild the order from left to right for each hor_group
        this is called by the end of the stage 1

        too costly for now
        :return:
        """
        # how about just sort by the left boundary
        for i in range(len(self.hor_groups)):
            self.hor_groups[i].sort(key=lambda cid: self.cid2chars[cid]['bbox'][0])

    def init_from_char_stage2_3(self):
        """
        NOTE that, this might not be enough for refined analysis.
         The tree level dependency is too coarse.

        construct a tree of groups, based on non-horizontal relations
        for each group, identify the char that have relation with other group
        the group without relation with other group is treated as the root
        build the linkage relationship

        :return:
        """

        self.cid2gid_rel = {}
        child_gid_list = []
        for char in self.chars:
            # get the group where the char lies in
            gid = self.get_hor_group_id_for_cid(char['cid'])

            if char['relation'] != "HORIZONTAL":
                pid = char['pid']
                if pid == -1:
                    continue
                if pid not in self.cid2gid_rel:
                    self.cid2gid_rel[pid] = []
                # copy error?
                self.cid2gid_rel[pid].append((gid, char['relation']))
                child_gid_list.append(gid)

        self.root_g_id = -1
        # find the root node
        for i in range(len(self.hor_groups)):
            if i not in child_gid_list:
                self.root_g_id = i
                break

    def get_hor_group_id_for_cid(self, cid):
        """
        find the group id where the cid lies in

        :param cid: char id
        :return:
        """
        for gid, hor_group in enumerate(self.hor_groups):
            if cid in hor_group:
                return gid
        return None


def construct_hierarchy_by_me_idx(me_idx):
    """
    The original function is split into smaller parts and
        merged into the InftyCDBME class

    :param me_idx: index of ME
    :type me_idx: int
    :return: InftyCDBME
    """
    chars = load_chars_by_me_idx(me_idx)
    infty_cdb_me = InftyCDBME()
    infty_cdb_me.init_from_char(chars)
    return infty_cdb_me


if __name__ == "__main__":
    pass
    """
    me_idx = "28019703"
    me_idx = "28019974"
    #me_idx = "28020343"

    infty_cdb_me = construct_hierarchy_by_me_idx(me_idx)
    print infty_cdb_me
    infty_cdb_me.db_print_all()
    infty_cdb_me.gather_hor_groups()
    """
