import numpy as np
import pdfxml.me_layout.me_layout_config as me_layout_config
from pdfxml.InftyCDB.macros import \
    REL_H, REL_SUP, REL_SUB, \
    REV_REL_H, REV_REL_SUP, REV_REL_SUB, \
    REL_UPPER, REL_UNDER, rel_id2rel_str
from pdfxml.me_taxonomy.latex.latex_punct import is_punct_late_val
from pdfxml.me_taxonomy.latex.latex_rel import is_rel_latex_val
from pdfxml.me_taxonomy.latex.latex_op import is_op_latex_val


# TODO, make it common
def get_rev_rel(rel):
    """

    :param rel:
    :return:
    """
    rel2rev = {
        REL_H: REV_REL_H,
        REL_SUP: REV_REL_SUP,
        REL_SUB: REV_REL_SUB,
        REL_UPPER: REL_UNDER,
        REL_UNDER: REL_UPPER
    }
    return rel2rev[rel]


class ScriptConfig:
    """
    This is the horizontal ME layout
    """
    def __init__(self):
        """
        cid and pid are index of the me_groups
        r is index of the relation
        """
        self.cid2pid_r = {}  # map from the cid to pair of pid and r

    def __str__(self):
        tmp_str = ""
        for cid, pid_r in self.cid2pid_r.items():
            pid, r = pid_r
            if r is None:
                r_str = "HEAD"
            else:
                r_str = rel_id2rel_str[r]
            #print r, r_str
            tmp_str += "({}, {}, {})".format(
                cid, pid_r[0], r_str)
        return tmp_str

    def __hash__(self):
        triple_str_list = [str(triple) for triple in self.get_triples()]
        triple_str = ''.join(triple_str_list)
        return hash(triple_str)

    def __eq__(self, other):
        """
        http://jcalderone.livejournal.com/32837.html
        https://stackoverflow.com/questions/22736641/xor-on-two-lists-in-python

        :param other:
        :return:
        """
        if isinstance(other, ScriptConfig):
            cid_diff = set(self.cid2pid_r.keys()).symmetric_difference(other.cid2pid_r.keys())
            if len(cid_diff) > 0:
                return False
            for cid in self.cid2pid_r.keys():
                tmp_diff = set(self.cid2pid_r[cid]).symmetric_difference(other.cid2pid_r[cid])
                if len(tmp_diff) > 0:
                    return False
        return True

    def get_children(self, i):
        """

        :param i: element idx
        :return:
        """
        children = []
        for cid, (pid, r) in self.cid2pid_r.items():
            if pid == i:
                children.append(cid)
        return children

    def get_hor_chain(self, head_idx):
        """

        :param head_idx:
        :return: list of idx of hor relation with head of head_idx
        """
        hor_pid2cid = {}
        for cid, pid_r in self.cid2pid_r.items():
            pid, r = pid_r
            if r == REL_H:
                hor_pid2cid[pid] = cid
        hor_chain = [head_idx]
        while hor_chain[-1] in hor_pid2cid:
            hor_chain.append(hor_pid2cid[hor_chain[-1]])
        return hor_chain

    def get_script_cid_rel_id_num(self, parent_idx):
        """
        # of the children of scription

        :param parent_idx: parent id
        :return:
        """
        num = 0
        for cid, pid_r in self.cid2pid_r.items():
            pid, r = pid_r
            if r == REL_H:
                continue
            if pid == parent_idx:
                num += 1
        return num

    def get_first_script_cid_rel_id(self, parent_idx):
        for cid, pid_r in self.cid2pid_r.items():
            pid, r = pid_r
            if r == REL_H:
                continue
            if pid == parent_idx:
                return cid, r
        return None

    def add_triple(self, i, pi, rel):
        """

        :param i: index of the child
        :param pi: index of the parent
        :param rel: ? What's here ?
        :return:
        """
        self.cid2pid_r[i] = (pi, rel)

    def get_pid(self, i):
        """
        get the parent of the index i

        :param i:
        :return:
        """
        if i in self.cid2pid_r:
            return self.cid2pid_r[i][0]
        return None

    def get_parent_rel(self, i):
        if i in self.cid2pid_r:
            return self.cid2pid_r[i][1]
        return None

    def get_parent_stack(self, i):
        """

        :param i:
        :return:
        """
        p_stack = []
        while i != -1:
            p_stack.append(i)
            i = self.cid2pid_r[i][0]
        return p_stack

    def get_common_root(self, i, j):
        # get the parent stack for i and j
        # then pop until meet the first not same
        si = self.get_parent_stack(i)
        sj = self.get_parent_stack(j)
        p = -1
        while si and sj and si[-1] == sj[-1]:
            p = si[-1]
            del si[-1]
            del sj[-1]
        return p

    def get_triples(self):
        for cid, pid_r in self.cid2pid_r.items():
            yield (cid, pid_r[0], pid_r[1])

    def update_config(self, hole, local_config_pos):
        """

        :param config: A ScriptConfig object
        :param hole: a pair of position
        :param local_config_pos: (local_config, pos),
            local_config is another script config,
            pos is the relative position of the local relation with respect to the the left parent
        :return:
        """
        b = hole[0]
        local_config, pos = local_config_pos
        for cid, pid, r in local_config.get_triples():
            self.add_triple(cid+b, pid+b, r)
        self.add_triple(b, b-1, pos)

    def print_pair_rel_list(self):
        """

        :return:
        """
        pair_rel_list = self.get_pair_rel_list()
        for cid, pid, rel_id_list in pair_rel_list:
            rel_str_list = [rel_id2rel_str[rel_id] for rel_id in rel_id_list]
            rel_list_str = ", ".join(rel_str_list)
            print "{}, {}, [{}]".format(cid, pid, rel_list_str)

    def get_pair_rel_list_consecutive(self, debug=False, me_groups=None):
        """
        This function is based on previous function of get_pair_rel_list
        The difference is that the current version only enumerate
        the pairs of consecutive elements

        Using the logic before, there will be a problem when reducing to only consider consecutive
        In the case 28001733, X-\hat{X}, there will be no pair generated

        :param debug:
        :param me_groups:
        :return:
        """
        raise Exception("the consecutive version abandoned")

        pair_rel_list = []
        n = np.max(self.cid2pid_r.keys()) + 1
        i = 0
        while i < n:
            # i is a staring position, look for a valid next j position
            j = i+1

            if me_layout_config.OPTION_A_3_NO_OP_PUNCT_REL_PAIR_PROB:
                # if the symbol at position i is not alphanumeric, skip
                # alphanumeric is defined as not at op/rel/punct
                val_i = str(me_groups[i])
                if is_op_latex_val(val_i) or is_rel_latex_val(val_i) or is_punct_late_val(val_i):
                    i += 1 # not good, and skip one
                    continue
                # find the next position j which is alphanumeric
                while j < n:
                    val_j = str(me_groups[j])
                    if is_op_latex_val(val_j) or is_rel_latex_val(val_j) or is_punct_late_val(val_j):
                        j += 1
                    else:
                        break
                if j == n:
                    break # finished

            # get the common root of i and j
            rid = self.get_common_root(i, j)
            if debug:
                print i, j, rid
            if rid == i:
                # if i and j are of parental relationship
                rel_list = []
                tmpj = j
                while tmpj != rid:
                    rel_list.insert(0, self.get_parent_rel(tmpj))
                    tmpj = self.get_pid(tmpj)
                pair_rel_list.append( (i, j, tuple(rel_list)) )
            else:
                # prepare the list of relationship
                rel_list = []
                tmpi = i
                while tmpi != rid:
                    rel_list.append(get_rev_rel(self.get_parent_rel(tmpi)))
                    tmpi = self.get_pid(tmpi)

                tmp_rel_list = []
                tmpj = j
                while tmpj != rid:
                    tmp_rel_list.insert(0, self.get_parent_rel(tmpj))
                    tmpj = self.get_pid(tmpj)
                rel_list.extend(tmp_rel_list)
                pair_rel_list.append((i, j, tuple(rel_list)))
            i = j # update i as the j
        return pair_rel_list

    def get_node_chain(self, i, j):
        """
        get the chain of nodes that are in relationship.

        :param i:
        :param j:
        :return:
        """
        node_chain = []
        # get the common root of i and j
        rid = self.get_common_root(i, j)
        if rid == i:
            node_chain.append(j)
            tmpj = j
            while tmpj != rid:
                tmpj = self.get_pid(tmpj)
                node_chain.append(tmpj)
            node_chain.reverse()
            return tuple(node_chain)
        else:
            # prepare the list of relationship
            node_chain.append(i)
            tmpi = i
            while tmpi != rid:
                tmpi = self.get_pid(tmpi)
                node_chain.append(tmpi)

            tmp_node_chain = []
            tmpj = j
            while tmpj != rid:
                tmp_node_chain.append(tmpj)
                tmpj = self.get_pid(tmpj)
            tmp_node_chain.reverse()
            node_chain.extend(tmp_node_chain)
            return tuple(node_chain)

    def get_rel_list(self, i, j):
        """
        no constraints related, the config is from ground truth for now

        :param i: the first index
        :param j: the second index
        :return:
        """
        # get the common root of i and j
        rid = self.get_common_root(i, j)
        if rid == i:
            rel_list = []
            tmpj = j
            while tmpj != rid:
                rel_list.insert(0, self.get_parent_rel(tmpj))
                tmpj = self.get_pid(tmpj)
            return tuple(rel_list)
        else:
            # prepare the list of relationship
            rel_list = []
            tmpi = i
            while tmpi != rid:
                tmp_rel = self.get_parent_rel(tmpi)
                if tmp_rel is None:
                    rel_list.append(REL_H)
                else:
                    rel_list.append(get_rev_rel(tmp_rel))
                tmpi = self.get_pid(tmpi)

            tmp_rel_list = []
            tmpj = j
            while tmpj != rid:
                tmp_rel = self.get_parent_rel(tmpj)
                if tmp_rel is None:
                    tmp_rel_list.insert(0, REL_H)
                else:
                    tmp_rel_list.insert(0, self.get_parent_rel(tmpj))
                tmpj = self.get_pid(tmpj)
            rel_list.extend(tmp_rel_list)
            return tuple(rel_list)

    def same_level(self, i, j):
        rel_list = self.get_rel_list(i, j)
        sup_count = 0 # +1 for sup, -1 for sub
        sub_count = 0
        for rel in rel_list:
            if rel in [REL_H, REV_REL_H]:
                pass
            elif rel == REL_SUB:
                sub_count += 1
            elif rel == REV_REL_SUB:
                sub_count -= 1
            elif rel == REL_SUP:
                sup_count += 1
            elif rel == REV_REL_SUP:
                sup_count -= 1
            else:
                raise Exception("unknow relationship")
        return sup_count == 0 and sub_count == 0

    # TODO, I would also like to limit the possible range of the pair to consider
    def get_pair_rel_list(self, debug=False, me_groups=None):
        """
        find the first common parent
        return, i, j, rel_list, the sequence of relative position from i to j

        :param config: ScriptConfig type
            each configuration is represented as a tree structure, we are using parent index representation
        :param debug:
        :return:
        """

        #assert not OPTION_A_3_NO_OP_PUNCT_REL_PAIR_PROB
        # other wise the symbol informatin should also be used
        if me_layout_config.OPTION_A_3_NO_OP_PUNCT_REL_PAIR_PROB and me_groups is None:
            raise Exception("Should provide the me_groups")

        pair_rel_list = []
        n = np.max(self.cid2pid_r.keys())+1
        for i in range(n):
            for j in range(i+1, n):

                # the maximal range
                if me_layout_config.MAX_DIFF is not None:  # not None
                    if j-i > me_layout_config.MAX_DIFF:
                        continue

                baseline_symbol_i = me_groups[i].get_baseline_symbol()
                baseline_symbol_j = me_groups[j].get_baseline_symbol()
                if baseline_symbol_i is None or baseline_symbol_j is None:
                    continue

                val_i = baseline_symbol_i.latex_val
                val_j = baseline_symbol_j.latex_val

                if me_layout_config.OPTION_A_3_NO_OP_PUNCT_REL_PAIR_PROB:
                    if is_op_latex_val(val_i) or is_rel_latex_val(val_i) or is_punct_late_val(val_i):
                        continue
                    if is_op_latex_val(val_j) or is_rel_latex_val(val_j) or is_punct_late_val(val_j):
                        continue

                # get the common root of i and j
                rid = self.get_common_root(i, j)
                if debug:
                    print i, j, rid

                if rid == i:
                    rel_list = []
                    tmpj = j
                    while tmpj != rid:
                        rel_list.insert(0, self.get_parent_rel(tmpj))
                        tmpj = self.get_pid(tmpj)
                    pair_rel_list.append(
                        (i, j, tuple(rel_list)))

                else:
                    # prepare the list of relationship
                    rel_list = []
                    tmpi = i
                    while tmpi != rid:
                        rel_list.append(get_rev_rel(self.get_parent_rel(tmpi)))
                        tmpi = self.get_pid(tmpi)

                    tmp_rel_list = []
                    tmpj = j
                    while tmpj != rid:
                        tmp_rel_list.insert(0, self.get_parent_rel(tmpj))
                        tmpj = self.get_pid(tmpj)
                    rel_list.extend(tmp_rel_list)
                    pair_rel_list.append((i, j, tuple(rel_list)))

        return pair_rel_list