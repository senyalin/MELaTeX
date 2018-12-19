"""
implement the union find algorithm here?
"""

class UnionFind:
    def __init__(self):
        self.r2w = {}  # root 2 weight
        self.node2root = {}
        self.nodes = set()
        pass

    def add_node(self, i):
        """

        :param i:
        :return:
        """
        self.nodes.add(i)
        if i not in self.r2w:
            self.r2w[i] = 1
        if i not in self.node2root:
            self.node2root[i] = i

    def merge(self, i, j):
        """

        :param i:
        :param j:
        :return:
        """
        r_i = self.get_root(i)
        r_j = self.get_root(j)
        if r_i != r_j:
            if self.r2w[r_i] > self.r2w[r_j]:
                # put r_j as a sub tree of r_i
                self.node2root[r_j] = r_i
                self.r2w[r_i] += self.r2w[r_j]
            else:
                self.node2root[r_i] = r_j
                self.r2w[r_j] += self.r2w[r_i]

    def get_root(self, i):
        """
        # TODO, ?
        :param i:
        :return:
        """
        if i not in self.node2root:
            self.add_node(i)
        if self.node2root[i] != self.node2root[self.node2root[i]]:
            # pass compression
            self.node2root[i] = self.get_root(self.node2root[i])
        return self.node2root[i]

    def get_groups(self):
        """
        after the union find, get all connected components
        :return:
        """
        root2nodes = {}
        for n in self.nodes:
            r = self.get_root(n)
            if r not in root2nodes:
                root2nodes[r] = []
            root2nodes[r].append(n)
        return root2nodes.values()

    def get_largest_connected_node_set(self):
        gid2node_set = {}
        for node in self.nodes:
            gid = self.get_root(node)
            if gid not in gid2node_set:
                gid2node_set[gid] = set()
            gid2node_set[gid].add(node)
        largest_node_set = set()
        for gid, node_set in gid2node_set.items():
            if len(node_set) > len(largest_node_set):
                largest_node_set = node_set
        return largest_node_set



