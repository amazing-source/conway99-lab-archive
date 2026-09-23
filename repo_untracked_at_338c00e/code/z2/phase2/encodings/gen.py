"""Phase-2 / encodings angle.  Orbit-level involution model (same variables and constraints (R),(D),(I),(P) as
code/z2/orbit_sat.py) with configurable cardinality encodings, optional at-most-only (P), and optional
REDUNDANT (implied) constraints:
  ten     : for every U, exactly 10 orbits W with a_UW xor b_UW = 1  (S-Gram diagonal; implied by (R)+(D))
  qgram   : for U<V: sum_W (a_UW a_VW + b_UW b_VW + a_UW b_VW + b_UW a_VW) + a_UV + b_UV = 4 - Sh_UV
            (Q-Gram identity Q_out^2 + Q_out = 12I + 4J - Sh; = sum of the two (P) constraints)
  parity  : for every V and block l: XOR_{U ni l, U != V} (a_UV xor b_UV) = 0   (Gamma-bar N_b = 0 over F2;
            implied by (I): #nbrs containing (l,0) == #nbrs containing (l,1))
  balance : for every V and block l: sum_{U ni l} sign(U,l) (a_UV - b_UV) = 0 as an integer equality
            (C^T S_out = 0; = difference of the two (I) constraints of block l), encoded as a cardinality equality
Usage:
  python gen.py --m 7 --case sib --enc totalizer --red ten,qgram --out file.cnf
  python gen.py --m 2 --enc X --red ... --count      (control: enumerate all solutions on primary vars; must be
                                                      the same number with and without redundant constraints)
  python gen.py --m 3 --solve                       (control: must be UNSAT)
"""
import argparse, itertools, sys, time
import numpy as np
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType

ENC = {"seqcounter": EncType.seqcounter, "totalizer": EncType.totalizer, "cardnetwrk": EncType.cardnetwrk,
       "mtotalizer": EncType.mtotalizer, "kmtotalizer": EncType.kmtotalizer, "sortnetwrk": EncType.sortnetwrk,
       "pairwise": EncType.pairwise, "ladder": EncType.ladder}

def build(m, case="none", enc="seqcounter", pmode="eq", red=(), enc_small=None):
    """enc: encoding for the big (P)/(qgram) constraints; enc_small: encoding for (R),(D),(I),ten,balance (default = enc)."""
    k = 2 * m
    E = ENC[enc]; Es = ENC[enc_small] if enc_small else E
    outer = [(i, j, e) for i in range(1, m + 1) for j in range(i + 1, m + 1) for e in (0, 1)]
    N = len(outer)
    rep = [frozenset([(i, 0), (j, e)]) for (i, j, e) in outer]
    trep = [frozenset([(i, 1), (j, 1 - e)]) for (i, j, e) in outer]
    pool = IDPool(); cnf = CNF()
    A = {}; B = {}
    for U in range(N):
        for V in range(U + 1, N):
            A[U, V] = A[V, U] = pool.id(("a", U, V)); B[U, V] = B[V, U] = pool.id(("b", U, V))
    nprim = pool.top
    def prod(x, y):
        p = pool.id(("p", min(x, y), max(x, y)))
        cnf.extend([[-p, x], [-p, y], [p, -x, -y]]); return p
    def card(lits, kk, mode, encoding):
        if not lits:
            assert kk == 0, "unsatisfiable constant constraint"; return
        if kk < 0 or kk > len(lits):
            cnf.append([]); return
        if mode == "eq":
            cnf.extend(CardEnc.equals(lits=lits, bound=kk, vpool=pool, encoding=encoding).clauses)
        elif mode == "atmost":
            if kk < len(lits):
                cnf.extend(CardEnc.atmost(lits=lits, bound=kk, vpool=pool, encoding=encoding).clauses)
        else:
            raise ValueError(mode)
    xor_cache = {}
    def xorv(x, y):
        """z = x xor y"""
        key = (min(x, y), max(x, y))
        if key not in xor_cache:
            z = pool.id(("x",) + key)
            cnf.extend([[-z, x, y], [-z, -x, -y], [z, -x, y], [z, x, -y]]); xor_cache[key] = z
        return xor_cache[key]
    def xor_zero(lits):
        """XOR of lits = 0, chained Tseitin"""
        if not lits: return
        acc = lits[0]
        for l in lits[1:]:
            acc = xorv(acc, l)
        cnf.append([-acc])
    inner = [(i, s) for i in range(1, m + 1) for s in (0, 1)]
    for U in range(N):
        others = [V for V in range(N) if V != U]
        card([A[U, V] for V in others] + [B[U, V] for V in others], k - 2, "eq", Es)                 # (R)
        card([prod(A[U, V], B[U, V]) for V in others], 1, "eq", Es)                                    # (D)
        for c in inner:                                                                                # (I)
            partner = (c[0], 1 - c[1]); lits = []
            for V in others:
                if c in rep[V]: lits.append(A[U, V])
                if c in trep[V]: lits.append(B[U, V])
            card(lits, 1 if (c in rep[U] or partner in rep[U]) else 2, "eq", Es)
        if "ten" in red:
            card([xorv(A[U, V], B[U, V]) for V in others], k - 4, "eq", Es)
    for U in range(N):                                                                                 # (P)
        for V in range(U + 1, N):
            Ws = [W for W in range(N) if W != U and W != V]
            same = [prod(A[U, W], A[V, W]) for W in Ws] + [prod(B[U, W], B[V, W]) for W in Ws]
            cross = [prod(A[U, W], B[V, W]) for W in Ws] + [prod(B[U, W], A[V, W]) for W in Ws]
            c1 = 2 - len(rep[U] & rep[V]); c2 = 2 - len(rep[U] & trep[V])
            card(same + [A[U, V]], c1, pmode, E)
            card(cross + [B[U, V]], c2, pmode, E)
            if "qgram" in red:
                sh = len({i for (i, s) in rep[U]} & {i for (i, s) in rep[V]})
                assert c1 + c2 == 4 - sh
                card(same + cross + [A[U, V], B[U, V]], 4 - sh, "eq", E)
    if "parity" in red or "balance" in red:
        for V in range(N):
            for l in range(1, m + 1):
                Us = [U for U in range(N) if U != V and l in {i for (i, s) in rep[U]}]
                if "parity" in red:
                    xor_zero([xorv(A[U, V], B[U, V]) for U in Us])
                if "balance" in red:
                    # sign(U,l) = +1 if (l,0) in rep[U] else -1.  sum_{U} sign(U,l) (a_UV - b_UV) = 0
                    # <=> sum_{+} a + sum_{-} b  ==  sum_{+} b + sum_{-} a  (both sides = 1 or 2 by (I))
                    # encode: sum_{+} a + sum_{-} b + sum_{+} (not b) + sum_{-} (not a) == |Us|
                    plus = [U for U in Us if (l, 0) in rep[U]]; minus = [U for U in Us if (l, 1) in rep[U]]
                    lits = [A[U, V] for U in plus] + [B[U, V] for U in minus] + [-B[U, V] for U in plus] + [-A[U, V] for U in minus]
                    card(lits, len(Us), "eq", Es)
    if case != "none":
        tgt = {"sib": (1, 2, 1), "one": (1, 3, 0), "dis": (3, 4, 0)}[case]
        D = outer.index(tgt); cnf.append([A[0, D]]); cnf.append([B[0, D]])
    return cnf, pool, outer, rep, trep, A, B, nprim

def lift(m, outer, rep, trep, A, B, model):
    k = 2 * m; N = len(outer); n = 1 + 2 * m + 2 * N
    val = set(l for l in model if l > 0)
    inner = [(i, s) for i in range(1, m + 1) for s in (0, 1)]
    idx = {}
    for t, v in enumerate(inner): idx[v] = 1 + t
    for U in range(N): idx[rep[U]] = 1 + 2 * m + 2 * U; idx[trep[U]] = 1 + 2 * m + 2 * U + 1
    M = np.zeros((n, n), dtype=np.int64)
    for v in inner: M[0, idx[v]] = M[idx[v], 0] = 1
    for i in range(1, m + 1): M[idx[(i, 0)], idx[(i, 1)]] = M[idx[(i, 1)], idx[(i, 0)]] = 1
    for U in range(N):
        for lab in (rep[U], trep[U]):
            for v in lab: M[idx[lab], idx[v]] = M[idx[v], idx[lab]] = 1
    for U in range(N):
        for V in range(U + 1, N):
            a = 1 if A[U, V] in val else 0; b = 1 if B[U, V] in val else 0
            u, tu, v, tv = idx[rep[U]], idx[trep[U]], idx[rep[V]], idx[trep[V]]
            M[u, v] = M[v, u] = M[tu, tv] = M[tv, tu] = a
            M[u, tv] = M[tv, u] = M[tu, v] = M[v, tu] = b
    ok = np.array_equal(M @ M + M - (k - 2) * np.eye(n, dtype=np.int64), 2 * np.ones((n, n), dtype=np.int64))
    return M, ok

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, default=7); ap.add_argument("--case", default="none")
    ap.add_argument("--enc", default="seqcounter"); ap.add_argument("--enc-small", default=None)
    ap.add_argument("--pmode", default="eq"); ap.add_argument("--red", default="")
    ap.add_argument("--out", default=None); ap.add_argument("--solve", action="store_true"); ap.add_argument("--count", action="store_true")
    a = ap.parse_args()
    red = tuple(r for r in a.red.split(",") if r)
    t0 = time.time(); cnf, pool, outer, rep, trep, A, B, nprim = build(a.m, a.case, a.enc, a.pmode, red, a.enc_small)
    nlits = sum(len(c) for c in cnf.clauses)
    print("m=%d case=%s enc=%s small=%s pmode=%s red=%s vars=%d clauses=%d literals=%d build=%.1fs" % (
        a.m, a.case, a.enc, a.enc_small, a.pmode, ",".join(red), pool.top, len(cnf.clauses), nlits, time.time() - t0), flush=True)
    if a.out: cnf.to_file(a.out); print("written", a.out)
    if a.solve or a.count:
        from pysat.solvers import Solver
        with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
            if a.count:
                n = 0; bad = 0
                while s.solve():
                    mdl = s.get_model(); n += 1
                    M, ok = lift(a.m, outer, rep, trep, A, B, mdl)
                    if not ok: bad += 1
                    s.add_clause([-l for l in mdl if abs(l) <= nprim])
                print("COUNT solutions(primary)=%d lift_failures=%d time=%.1fs" % (n, bad, time.time() - t0))
            else:
                res = s.solve(); print("result:", res, "time=%.1fs" % (time.time() - t0))
                if res:
                    M, ok = lift(a.m, outer, rep, trep, A, B, s.get_model()); print("LIFT VERIFY srg identity:", ok)
