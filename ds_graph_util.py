"""
Operation of Graph Data structure
"""


class XWGraph:
    def __init__(self):
        self.n = -1
        self.edges = []
        self.group = None

    def init_by_edges(self, edges, n):
        """

        :param edges:
        :param n: pass this parameter becaues the edge might not cover all nodes
        :return:
        """
        self.edges = edges
        """
        
        # init the n
        for s, t in edges:
            self.n = max(s, self.n)
            self.n = max(t, self.n)
        self.n += 1
        """
        self.n = n

    def get_group_idx(self, node_idx):
        """

        :param node_idx:
        :return:
        """
        tmp_idx = node_idx
        while tmp_idx != self.group[tmp_idx]:
            tmp_idx = self.group[tmp_idx]
        return tmp_idx

    def find_connected_components(self):
        """

        :return: list of (list of index as a group)
        :rtype: list[list[int]]
        """
        # in the beginning, each node is assigned
        self.group = range(self.n)
        for s, t in self.edges:
            group_s = self.get_group_idx(s)
            group_t = self.get_group_idx(t)
            if group_s != group_t:
                self.group[group_s] = group_t

        group2node_list = {}
        for node_idx in range(self.n):
            gid = self.get_group_idx(node_idx)
            if gid not in group2node_list:
                group2node_list[gid] = []
            group2node_list[gid].append(node_idx)

        return group2node_list.values()
