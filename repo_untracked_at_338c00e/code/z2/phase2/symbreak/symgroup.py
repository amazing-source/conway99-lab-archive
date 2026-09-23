"""Label group 2^m x| S_m acting on the orbit-level variables (a_UV, b_UV) of orbit_sat.py.

Conventions (from orbit_sat.py): outer orbits U=(i,j,e), i<j, rep(U)={(i,0),(j,e)}, trep(U)={(i,1),(j,1-e)}.
A label {(i,s),(j,e)} (i<j) belongs to orbit (i,j,e^s); it is rep if s=0, trep if s=1  (gauge = s).
Group element g=(pi,f): inner (i,s) -> (pi[i], s^f[i]); pi a permutation of {1..m}, f in {0,1}^m.
It commutes with sigma (flip of every block).
Induced action: g.rep(U) = sigma^{eps_U} rep(gU).  With A'[gx,gy]=A[x,y]:
   a'_{gU,gV} = a_UV if eps_U==eps_V else b_UV ;  b'_{gU,gV} = b_UV if eps_U==eps_V else a_UV.
So g induces a PURE PERMUTATION Pi_g of the 1722 primary variables (no negation).
"""
import sys, itertools, random
sys.path.insert(0, r"C:\Users\RESEARCHER\Desktop\conway99-involution\code\z2")
from orbit_sat import build, lift


def outer_orbits(m):
    return [(i, j, e) for i in range(1, m + 1) for j in range(i + 1, m + 1) for e in (0, 1)]


def orbit_of_label(lab):
    (i, s), (j, e) = sorted(lab)           # i<j
    return (i, j, e ^ s), s


def act_label(g, lab):
    pi, f = g
    return frozenset((pi[i], s ^ f[i]) for (i, s) in lab)


def induced_on_orbits(g, outer):
    """returns (img, eps): img[U]=index of gU, eps[U]=gauge flip."""
    idx = {o: t for t, o in enumerate(outer)}
    img, eps = [], []
    for (i, j, e) in outer:
        rep = frozenset([(i, 0), (j, e)])
        o, s = orbit_of_label(act_label(g, rep))
        img.append(idx[o]); eps.append(s)
    return img, eps


def var_perm(g, outer, A, B):
    """dict primary var id -> image id under g (x'[Pi(v)] = x[v])."""
    img, eps = induced_on_orbits(g, outer)
    N = len(outer); P = {}
    for U in range(N):
        for V in range(U + 1, N):
            gU, gV = img[U], img[V]
            if eps[U] == eps[V]:
                P[A[U, V]] = A[gU, gV]; P[B[U, V]] = B[gU, gV]
            else:
                P[A[U, V]] = B[gU, gV]; P[B[U, V]] = A[gU, gV]
    return P


def compose(g, h):
    """(g*h)(x) = g(h(x))"""
    (pg, fg), (ph, fh) = g, h
    m = len(pg) - 1
    pi = [0] * (m + 1); f = [0] * (m + 1)
    for i in range(1, m + 1):
        pi[i] = pg[ph[i]]; f[i] = fh[i] ^ fg[ph[i]]
    return (tuple(pi), tuple(f))


def identity(m):
    return (tuple(range(m + 1)), tuple([0] * (m + 1)))


def elem(m, pi_dict=None, flips=()):
    pi = list(range(m + 1)); f = [0] * (m + 1)
    if pi_dict:
        for k, v in pi_dict.items(): pi[k] = v
    for i in flips: f[i] = 1
    return (tuple(pi), tuple(f))


def full_group(m):
    els = []
    for perm in itertools.permutations(range(1, m + 1)):
        pi = (0,) + perm
        for fl in itertools.product((0, 1), repeat=m):
            els.append((pi, (0,) + fl))
    return els


def stabiliser(els, outer, fixed_orbits):
    """elements mapping the SET of the given orbits (indices) to itself."""
    S = set(fixed_orbits); out = []
    for g in els:
        img, _ = induced_on_orbits(g, outer)
        if set(img[U] for U in S) == S: out.append(g)
    return out


def case_group(m, case):
    """symmetry group of the case-split CNF: set-stabiliser of {U0, D} (or full group for 'none')."""
    outer = outer_orbits(m)
    if case == "none":
        return full_group(m)
    tgt = {"sib": (1, 2, 1), "one": (1, 3, 0), "dis": (3, 4, 0)}[case]
    return stabiliser(full_group(m), outer, [0, outer.index(tgt)])


def generators_full(m):
    """generators of 2^m x| S_m: flip of block 1, transposition (1 2), m-cycle."""
    gens = [elem(m, flips=(1,)), elem(m, {1: 2, 2: 1})]
    if m > 2: gens.append(elem(m, {i: (i % m) + 1 for i in range(1, m + 1)}))
    return gens


# ------------------------------------------------------------------ semantic constraints (for invariance checks)
def semantic_constraints(m, A, B, outer):
    """list of (frozenset(terms), bound); term = ('v',id) or ('p',id1,id2) for products. Mirrors orbit_sat.build."""
    k = 2 * m; N = len(outer)
    rep = [frozenset([(i, 0), (j, e)]) for (i, j, e) in outer]
    trep = [frozenset([(i, 1), (j, 1 - e)]) for (i, j, e) in outer]
    inner = [(i, s) for i in range(1, m + 1) for s in (0, 1)]
    def v(x): return ('v', x)
    def p(x, y): return ('p', min(x, y), max(x, y))
    cons = []
    for U in range(N):
        others = [V for V in range(N) if V != U]
        cons.append(('R', frozenset([v(A[U, V]) for V in others] + [v(B[U, V]) for V in others]), k - 2))
        cons.append(('D', frozenset([p(A[U, V], B[U, V]) for V in others]), 1))
        for c in inner:
            partner = (c[0], 1 - c[1]); lits = []
            for V in others:
                if c in rep[V]: lits.append(v(A[U, V]))
                if c in trep[V]: lits.append(v(B[U, V]))
            cons.append(('I', frozenset(lits), 1 if (c in rep[U] or partner in rep[U]) else 2))
    for U in range(N):
        for V in range(U + 1, N):
            Ws = [W for W in range(N) if W != U and W != V]
            same = [p(A[U, W], A[V, W]) for W in Ws] + [p(B[U, W], B[V, W]) for W in Ws]
            cross = [p(A[U, W], B[V, W]) for W in Ws] + [p(B[U, W], A[V, W]) for W in Ws]
            cons.append(('P', frozenset(same + [v(A[U, V])]), 2 - len(rep[U] & rep[V])))
            cons.append(('P', frozenset(cross + [v(B[U, V])]), 2 - len(rep[U] & trep[V])))
    return cons


def map_constraint(con, P):
    typ, terms, bound = con
    out = []
    for t in terms:
        if t[0] == 'v': out.append(('v', P[t[1]]))
        else:
            x, y = P[t[1]], P[t[2]]; out.append(('p', min(x, y), max(x, y)))
    return (typ, frozenset(out), bound)


# ------------------------------------------------------------------ lex-leader encoding
def lex_leader_clauses(P, order, top, prefix=None):
    """Clauses for x <=_lex Pi(x) with Pi(x)_i = x_{P[i]}, over variables in 'order' (list of ids).
    Aloul-Sakallah-Markov compact chain encoding; fixed points skipped; 'prefix' truncates to the first
    prefix positions of the support (still sound). Returns (clauses, new_top)."""
    sup = [x for x in order if P[x] != x]
    if prefix is not None: sup = sup[:prefix]
    cls = []; e_prev = None
    for idx, x in enumerate(sup):
        y = P[x]
        # e_prev -> (x <= y)  i.e.  (-e_prev v -x v y)
        cls.append(([-e_prev] if e_prev is not None else []) + [-x, y])
        if idx == len(sup) - 1: break
        top += 1; e = top
        # e <-> e_prev & (x == y)
        base = [e_prev] if e_prev is not None else []
        cls.append([-e, -x, y]); cls.append([-e, x, -y])
        if e_prev is not None: cls.append([-e, e_prev])
        cls.append([e] + [-v for v in base] + [x, y])      # e_prev & x=0 & y=0 -> e   (wait: needs both eq cases)
        cls.append([e] + [-v for v in base] + [-x, -y])    # e_prev & x=1 & y=1 -> e
        e_prev = e
    return cls, top
