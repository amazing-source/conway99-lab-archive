"""
Rooted-reduction SAT/CP-SAT model for putative srg(n,k,1,2) graphs
(Thakkar-Severini rooted reduction), built GENERICALLY from first principles:
for every unordered pair of vertices we compute, by brute enumeration over
all other vertices, the FORCED (constant) part of the common-neighbour count
and the list of Boolean-variable terms (linear, or quadratic AND-of-two-vars)
that must make up the rest. This is not hand-derived per case: the same
routine handles x-inner, x-outer, inner-inner, inner-outer and outer-outer
pairs uniformly, so bugs in case analysis cannot silently hide.

Vertex ids:
  0                      -> root x
  1 .. 2m                -> inner vertices, inner_id(i,s) = 1 + 2*i + s,  i in [0,m), s in {0,1}
  2m+1 .. 2m+L           -> outer vertices (L = 4*C(m,2)), one per label {(i,s),(j,t)}, i<j

Only outer-outer adjacency is unknown: Boolean variable H_{u,v} for unordered
pairs of outer vertices u<v (after optional identification under the
involution sigma).
"""
from pysat.formula import IDPool
from pysat.card import CardEnc, EncType

CARD_ENC = EncType.seqcounter


def m_of_k(k):
    assert k % 2 == 0
    return k // 2


def n_of_k(k):
    return k * (k - 2) // 2 + k + 1


class Instance:
    def __init__(self, k, use_sigma=False, no_self_adjacent=False, card_enc=CARD_ENC):
        self.k = k
        self.m = m_of_k(k)
        self.n = n_of_k(k)
        self.use_sigma = use_sigma
        self.no_self_adjacent = no_self_adjacent
        self.card_enc = card_enc

        m = self.m
        # inner vertex ids
        self.inner_id = {}   # (i,s) -> id
        self.inner_of = {}   # id -> (i,s)
        for i in range(m):
            for s in (0, 1):
                vid = 1 + 2 * i + s
                self.inner_id[(i, s)] = vid
                self.inner_of[vid] = (i, s)
        self.first_outer = 1 + 2 * m

        # outer vertices: one per label {(i,s),(j,t)}, i<j
        self.labels = []      # list of frozenset({inner_id_p, inner_id_q})
        for i in range(m):
            for j in range(i + 1, m):
                for s in (0, 1):
                    for t in (0, 1):
                        p = self.inner_id[(i, s)]
                        q = self.inner_id[(j, t)]
                        self.labels.append(frozenset((p, q)))
        self.num_outer = len(self.labels)
        assert self.num_outer == 4 * (m * (m - 1) // 2)
        self.outer_ids = list(range(self.first_outer, self.first_outer + self.num_outer))
        self.label_of = {self.outer_ids[idx]: self.labels[idx] for idx in range(self.num_outer)}
        self.outer_index = {oid: idx for idx, oid in enumerate(self.outer_ids)}

        # sigma automorphism: fixes x, swaps (i,0)<->(i,1) in every block
        def sigma_inner(p):
            (i, s) = self.inner_of[p]
            return self.inner_id[(i, 1 - s)]

        def sigma_label(lab):
            p, q = tuple(lab)
            return frozenset((sigma_inner(p), sigma_inner(q)))

        label_to_oid = {self.label_of[oid]: oid for oid in self.outer_ids}
        self.sigma_outer = {}
        for oid in self.outer_ids:
            self.sigma_outer[oid] = label_to_oid[sigma_label(self.label_of[oid])]
        # sanity: sigma is a fixed-point-free involution on outer ids
        for oid in self.outer_ids:
            assert self.sigma_outer[self.sigma_outer[oid]] == oid
            assert self.sigma_outer[oid] != oid

        self.vpool = IDPool()
        self._pair_var = {}     # canonical (a,b) a<b outer -> var id
        self._var_pairs = {}    # var id -> list of (a,b) represented (1 or 2 entries)
        self.self_adjacent_vars = set()

        for idx_a in range(self.num_outer):
            for idx_b in range(idx_a + 1, self.num_outer):
                a = self.outer_ids[idx_a]
                b = self.outer_ids[idx_b]
                self._get_var(a, b)

        self.clauses = []
        self.forced_facts = []   # (a,b,forced,target) for pairs with no variable terms - sanity log
        self._build()

    # ---------- variable management (with optional sigma identification) ----------
    def _canon_pair(self, a, b):
        if a > b:
            a, b = b, a
        if not self.use_sigma:
            return (a, b)
        sa, sb = self.sigma_outer[a], self.sigma_outer[b]
        if sa > sb:
            sa, sb = sb, sa
        return min((a, b), (sa, sb))

    def _get_var(self, a, b):
        key = self._canon_pair(a, b)
        if key not in self._pair_var:
            v = self.vpool.id(('H',) + key)
            self._pair_var[key] = v
            self._var_pairs[v] = [key]
            if self.use_sigma:
                sa, sb = self.sigma_outer[key[0]], self.sigma_outer[key[1]]
                skey = (sa, sb) if sa < sb else (sb, sa)
                if skey == key:
                    self.self_adjacent_vars.add(v)
                else:
                    self._var_pairs[v].append(skey)
        return self._pair_var[key]

    def hvar(self, a, b):
        """Return signed-lit-ready variable id for outer pair (a,b), a!=b."""
        return self._get_var(a, b)

    # ---------- fixed adjacency (defined whenever NOT both endpoints outer) ----------
    def is_outer(self, v):
        return v >= self.first_outer

    def adj_fixed(self, a, b):
        """Adjacency of a,b assuming NOT (both outer). Returns 0 or 1."""
        assert not (self.is_outer(a) and self.is_outer(b))
        if a == 0 or b == 0:
            other = b if a == 0 else a
            return 1 if (0 < other < self.first_outer) else 0
        a_inner = a < self.first_outer
        b_inner = b < self.first_outer
        if a_inner and b_inner:
            (i, s) = self.inner_of[a]
            (j, t) = self.inner_of[b]
            return 1 if (i == j and s != t) else 0
        # one inner, one outer
        inner_v = a if a_inner else b
        outer_v = b if a_inner else a
        return 1 if inner_v in self.label_of[outer_v] else 0

    def _get_adj_term(self, a, c):
        """Return ('const', 0/1) or ('var', varid) for adjacency(a,c)."""
        if self.is_outer(a) and self.is_outer(c):
            return ('var', self.hvar(a, c))
        return ('const', self.adj_fixed(a, c))

    def analyze_pair(self, a, b):
        """Brute-force, generic decomposition of common-neighbour count of a,b."""
        forced = 0
        linear = []
        quad = []
        for w in range(self.n):
            if w == a or w == b:
                continue
            fa = self._get_adj_term(a, w)
            fb = self._get_adj_term(w, b)
            if fa[0] == 'const' and fb[0] == 'const':
                forced += fa[1] * fb[1]
            elif fa[0] == 'const' and fb[0] == 'var':
                if fa[1] == 1:
                    linear.append(fb[1])
            elif fa[0] == 'var' and fb[0] == 'const':
                if fb[1] == 1:
                    linear.append(fa[1])
            else:
                quad.append((fa[1], fb[1]))
        return forced, linear, quad

    # ---------- model construction ----------
    def _new_and_gate(self, v1, v2):
        z = self.vpool.id(('AND', v1, v2, len(self.clauses)))
        self.clauses.append([-z, v1])
        self.clauses.append([-z, v2])
        self.clauses.append([z, -v1, -v2])
        return z

    def _card_equals(self, lits, bound, guard=None):
        """Add clauses for sum(lits) == bound, optionally guarded (i.e. only enforced
        when the literal `guard` is true -- clauses get -guard appended)."""
        if bound < 0 or bound > len(lits):
            if guard is None:
                raise ValueError("infeasible constant cardinality constraint")
            self.clauses.append([-guard])
            return
        if len(lits) == 0:
            # bound must be 0 here (checked above); nothing to do
            return
        top = self.vpool.top
        cnf = CardEnc.equals(lits=lits, bound=bound, top_id=top, encoding=self.card_enc)
        for cl in cnf.clauses:
            if guard is not None:
                cl = list(cl) + [-guard]
            self.clauses.append(cl)
        if cnf.nv > self.vpool.top:
            self.vpool.top = cnf.nv

    def _build(self):
        n = self.n
        k = self.k
        # done_pairs avoids re-processing an outer-outer pair whose variable was
        # already fully constrained via a sigma-equivalent representative pair.
        done_outer_pairs = set()

        for a in range(n):
            for b in range(a + 1, n):
                a_out = self.is_outer(a)
                b_out = self.is_outer(b)
                if a_out and b_out:
                    key = self._canon_pair(a, b)
                    if key in done_outer_pairs:
                        continue
                    done_outer_pairs.add(key)
                    forced, linear, quad = self.analyze_pair(a, b)
                    assert not linear, "unexpected linear term in outer-outer pair"
                    c = self.hvar(a, b)
                    s = forced
                    z_lits = [self._new_and_gate(v1, v2) for (v1, v2) in quad]
                    target_pos = 1 - s   # if H_ab = 1
                    target_neg = 2 - s   # if H_ab = 0
                    self._card_equals(z_lits, target_pos, guard=c)
                    self._card_equals(z_lits, target_neg, guard=-c)
                else:
                    forced, linear, quad = self.analyze_pair(a, b)
                    assert not quad, "unexpected quadratic term in non-outer-outer pair"
                    target = 1 if self.adj_fixed(a, b) == 1 else 2
                    needed = target - forced
                    if not linear:
                        if needed != 0:
                            raise RuntimeError("model bug: constant mismatch pair %d,%d: forced=%d target=%d" % (a, b, forced, target))
                        self.forced_facts.append((a, b, forced, target))
                        continue
                    self._card_equals(linear, needed)

        # explicit degree-k constraint for every outer vertex (x, inner are automatic)
        for w in self.outer_ids:
            lits = [self.hvar(w, u) for u in self.outer_ids if u != w]
            self._card_equals(lits, k - 2)

        if self.no_self_adjacent:
            for v in self.self_adjacent_vars:
                self.clauses.append([-v])

    # ---------- decoding & checking ----------
    def decode(self, model):
        """model: iterable of ints (pysat model, signed literals) or dict var->bool.
        Returns full n x n adjacency matrix (numpy int64)."""
        import numpy as np
        if not isinstance(model, dict):
            truth = {}
            for lit in model:
                truth[abs(lit)] = lit > 0
        else:
            truth = model
        A = np.zeros((self.n, self.n), dtype=np.int64)
        for a in range(self.n):
            for b in range(a + 1, self.n):
                if self.is_outer(a) and self.is_outer(b):
                    v = self.hvar(a, b)
                    val = 1 if truth.get(v, False) else 0
                else:
                    val = self.adj_fixed(a, b)
                A[a, b] = val
                A[b, a] = val
        return A

    def outer_H_matrix(self, model):
        import numpy as np
        L = self.num_outer
        Hm = np.zeros((L, L), dtype=np.int64)
        if not isinstance(model, dict):
            truth = {}
            for lit in model:
                truth[abs(lit)] = lit > 0
        else:
            truth = model
        for ia in range(L):
            for ib in range(ia + 1, L):
                a = self.outer_ids[ia]
                b = self.outer_ids[ib]
                v = self.hvar(a, b)
                val = 1 if truth.get(v, False) else 0
                Hm[ia, ib] = val
                Hm[ib, ia] = val
        return Hm


def check_srg(A, k):
    """Independent integer check: A^2 + A - (k-2) I == 2 J  (exact int64 arithmetic)."""
    import numpy as np
    n = A.shape[0]
    assert A.shape == (n, n)
    assert np.array_equal(A, A.T), "not symmetric"
    assert np.all(np.diag(A) == 0), "nonzero diagonal"
    assert set(np.unique(A).tolist()).issubset({0, 1}), "not 0/1 matrix"
    deg = A.sum(axis=1)
    if not np.all(deg == k):
        return False, "degree mismatch: %s != {%d}" % (sorted(set(deg.tolist())), k)
    A2 = A.astype(np.int64) @ A.astype(np.int64)
    I = np.eye(n, dtype=np.int64)
    J = np.ones((n, n), dtype=np.int64)
    lhs = A2 + A - (k - 2) * I
    rhs = 2 * J
    if not np.array_equal(lhs, rhs):
        diff = np.argwhere(lhs != rhs)
        return False, "identity fails at %d entries, e.g. %s" % (len(diff), diff[:5].tolist())
    return True, "ok"


# ---------------- CP-SAT model ----------------
def build_cpsat(inst):
    from ortools.sat.python import cp_model
    model = cp_model.CpModel()
    hvars = {}
    for key, v in inst._pair_var.items():
        if v not in hvars:
            hvars[v] = model.NewBoolVar('H_%d' % v)

    def bv(v):
        return hvars[v]

    n = inst.n
    done_outer_pairs = set()
    for a in range(n):
        for b in range(a + 1, n):
            a_out = inst.is_outer(a)
            b_out = inst.is_outer(b)
            if a_out and b_out:
                key = inst._canon_pair(a, b)
                if key in done_outer_pairs:
                    continue
                done_outer_pairs.add(key)
                forced, linear, quad = inst.analyze_pair(a, b)
                c = bv(inst.hvar(a, b))
                s = forced
                zs = []
                for (v1, v2) in quad:
                    z = model.NewBoolVar('z_%d_%d_%d_%d' % (a, b, v1, v2))
                    model.AddMultiplicationEquality(z, [bv(v1), bv(v2)])
                    zs.append(z)
                target_pos = 1 - s
                target_neg = 2 - s
                if 0 <= target_pos <= len(zs):
                    model.Add(sum(zs) == target_pos).OnlyEnforceIf(c)
                else:
                    model.Add(c == 0)
                if 0 <= target_neg <= len(zs):
                    model.Add(sum(zs) == target_neg).OnlyEnforceIf(c.Not())
                else:
                    model.Add(c == 1)
            else:
                forced, linear, quad = inst.analyze_pair(a, b)
                target = 1 if inst.adj_fixed(a, b) == 1 else 2
                needed = target - forced
                if not linear:
                    if needed != 0:
                        raise RuntimeError("model bug (cpsat constant mismatch)")
                    continue
                model.Add(sum(bv(v) for v in linear) == needed)

    for w in inst.outer_ids:
        lits = [bv(inst.hvar(w, u)) for u in inst.outer_ids if u != w]
        model.Add(sum(lits) == inst.k - 2)

    if inst.no_self_adjacent:
        for v in inst.self_adjacent_vars:
            model.Add(bv(v) == 0)

    return model, hvars


def decode_cpsat(inst, solver, hvars):
    truth = {v: (solver.Value(bv) == 1) for v, bv in hvars.items()}
    return inst.decode(truth)
