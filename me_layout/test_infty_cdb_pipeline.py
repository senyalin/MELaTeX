from pdfxml.InftyCDB.macros import rel_str2rel_id
from pdfxml.me_layout.pss_exp.pss_exception import LeftRelationException


def get_cpr_from_me_elems(me_elems):
    """
    This is for evluation purpose, also highly related to the format of the InftyCDB data

    :param me_elems:
    :return:
    """
    print "move this function into a better common unil position"
    cpr_list = []
    for me_elem in me_elems:
        rel_str = me_elem["relation"]

        if rel_str == "TOP":
            # NOTE, why top is ignored here? indicate the first element
            continue

        if me_elem["relation"] in ["LSUP", "LSUB"]:
            raise LeftRelationException()
        cpr_list.append((
            me_elem["cid"],
            me_elem["pid"],
            rel_str2rel_id[me_elem["relation"]]
        ))
    return cpr_list


def run_debug():
    # TODO , result pretty messy
    # TODO, move them as a common test bed
    me_idx = 28000472  # $(\overline{\partial}\rho(z)+w\mathrm{d}\overline{w})\wedge f(z)=0$
    me_idx = 28000239  # $\overline{\partial}_{b}K_{b}+K_{b}\overline{\partial}_{b}=I-P_{b}-S_{b}$,
    me_idx = 28000720  # $P_{m}^{\alpha,\beta}=P_{m}^{\alpha,\beta}(1-2|a|^{2}),$ looks good , split into small problems
    me_idx = 28000762  # $k_{\alpha}^{q}(\zeta,z)=\mathcal{O}(|\zeta-z|^{-2n+1})$  config gen OK, check prob later
    me_idx = 28000595  # $f(z)=-\overline{\partial}\rho(z)\wedge a(z)+b(z)$.

    me_idx = 28000877  # $F(\alpha+n-q,q+1,\alpha+1,|a|^{2})$, to pre-calculate all probability
    me_idx = 28000720  # $P_{m}^{\alpha,\beta}=P_{m}^{\alpha,\beta}(1-2|a|^{2}),$ looks good , split into small problems
    me_idx = 28000506  # $\tilde{f}=\tilde{f_{1}}+\tilde{f}_{2}$ hat

    # there are 20769 possible configs?
    me_idx = 28000720  # $P_{m}^{\alpha,\beta}=P_{m}^{\alpha,\beta}(1-2|a|^{2}),$ looks good , split into small problems

    me_idx = 28000506  # $\tilde{f}=\tilde{f_{1}}+\tilde{f}_{2}$ hat
    me_idx = 28000844  # $(H_{\alpha}^{\prime}f,\phi)_{\alpha}=$
    me_idx = 28000716  # $P_{n-q-1}^{\alpha,-n}$ sub_sup

    # round of analysis on some
    me_idx = 28005929  # passed after add digit to xy shape group
    me_idx = 28005921
    me_idx = 28005972
    me_idx = 28000204  # annotation error in InftyCDB
    me_idx = 28001483  # $v_{\lambda}$. bug of lambda part, 28002123

    # still buggy
    me_idx = 28010904  # $M_{r}^{\mathrm{o}}$ o as upper of M, very rare
    me_idx = 28018640  # $(0\leq p\leq m-i-1,0\leq q\leq i)$
    me_idx = 28000201  # although there is annotation error, still wrong
    me_idx = 28014891  # $L ^ {+}$, 28018451

    me_idx = 28005700
    me_idx = 28018640

    # run_exp_by_me_idx(me_idx, debug=True)
    # batch_run_exp()
    me_idx = 28008972  # $\alpha_{\sigma^{s},(n+|\sigma^{s}|)}=(-a)^{n}\gamma_{\sigma^{s}}$.
    me_idx = 28000767  # B_{\alpha}

    me_idx = 28017137

    #run_exp_by_me_idx(me_idx, debug=True)


if __name__ == "__main__":
    run_debug()
