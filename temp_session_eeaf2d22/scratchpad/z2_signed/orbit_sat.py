"""Orbit-level exact SAT model for a Conway-99 graph (srg(99,14,1,2), general k even) with an involution t
fixing exactly one vertex x. Forced structure: t flips every matched pair of N(x); outer labels {(i,s),(j,e)}
(i<j blocks); t acts on labels by flipping both coordinates. Orbits U=(i,j,e) with representative
u={(i,0),(j,e)} and t(u)={(i,1),(j,1-e)}. Variables for U<V: a[U,V]=A[u,v], b[U,V]=A[u,t v] (symmetric in U,V).
Exact constraints (equivalent to A^2+A-(k-2)I=2J given the forced part, cf. joint_dfs.py docstring):
 (R) sum_V a+b = k-2 ; (D) exactly one V with a=b=1 ; (I) per inner vertex c: #neighbours of u containing c
     = 1 if c in u or partner(c) in u else 2 ; (P) for U!=V: sum_W(a_UW a_VW + b_UW b_VW) + a_UV = 2-|u∩v| and
     sum_W(a_UW b_VW + b_UW a_VW) + b_UV = 2-|u∩tv|.
Usage: python orbit_sat.py --m 7 --case sib|one|dis|none --out file.cnf   (case fixes the double orbit of U0)
       python orbit_sat.py --m 2 --solve   (control k=4, must be SAT and lift to srg(9,4,1,2))
"""
import argparse, itertools, json, sys, time
import numpy as np
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType

def build(m, case="none"):
    k = 2 * m
    outer = [(i, j, e) for i in range(1, m + 1) for j in range(i + 1, m + 1) for e in (0, 1)]
    N = len(outer)
    rep = [frozenset([(i, 0), (j, e)]) for (i, j, e) in outer]
    trep = [frozenset([(i, 1), (j, 1 - e)]) for (i, j, e) in outer]
    pool = IDPool(); cnf = CNF()
    A = {}; B = {}
    for U in range(N):
        for V in range(U + 1, N):
            A[U, V] = A[V, U] = pool.id(("a", U, V)); B[U, V] = B[V, U] = pool.id(("b", U, V))
    def prod(x, y):
        p = pool.id(("p", min(x, y), max(x, y)))
        cnf.extend([[-p, x], [-p, y], [p, -x, -y]]); return p
    def eq(lits, kk):
        if not lits:
            assert kk == 0, "unsatisfiable constant constraint"; return
        if kk < 0 or kk > len(lits):
            cnf.append([]); return
        cnf.extend(CardEnc.equals(lits=lits, bound=kk, vpool=pool, encoding=EncType.seqcounter).clauses)
    inner = [(i, s) for i in range(1, m + 1) for s in (0, 1)]
    for U in range(N):
        others = [V for V in range(N) if V != U]
        eq([A[U, V] for V in others] + [B[U, V] for V in others], k - 2)                      # (R)
        eq([prod(A[U, V], B[U, V]) for V in others], 1)                                         # (D)
        for c in inner:                                                                         # (I)
            partner = (c[0], 1 - c[1]); lits = []
            for V in others:
                if c in rep[V]: lits.append(A[U, V])
                if c in trep[V]: lits.append(B[U, V])
            eq(lits, 1 if (c in rep[U] or partner in rep[U]) else 2)
    for U in range(N):                                                                          # (P)
        for V in range(U + 1, N):
            Ws = [W for W in range(N) if W != U and W != V]
            same = [prod(A[U, W], A[V, W]) for W in Ws] + [prod(B[U, W], B[V, W]) for W in Ws]
            cross = [prod(A[U, W], B[V, W]) for W in Ws] + [prod(B[U, W], A[V, W]) for W in Ws]
            eq(same + [A[U, V]], 2 - len(rep[U] & rep[V]))
            eq(cross + [B[U, V]], 2 - len(rep[U] & trep[V]))
    # symmetry case split on the double orbit of U0=(1,2,0): sibling (1,2,1), one-shared (1,3,0), disjoint (3,4,0)
    if case != "none":
        tgt = {"sib": (1, 2, 1), "one": (1, 3, 0), "dis": (3, 4, 0)}[case]
        D = outer.index(tgt); cnf.append([A[0, D]]); cnf.append([B[0, D]])
    return cnf, pool, outer, rep, trep, A, B

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
    ap = argparse.ArgumentParser(); ap.add_argument("--m", type=int, default=7); ap.add_argument("--case", default="none")
    ap.add_argument("--out", default=None); ap.add_argument("--solve", action="store_true"); ap.add_argument("--time", type=float, default=0)
    a = ap.parse_args()
    t0 = time.time(); cnf, pool, outer, rep, trep, A, B = build(a.m, a.case)
    print("m=%d case=%s vars=%d clauses=%d build=%.1fs" % (a.m, a.case, pool.top, len(cnf.clauses), time.time() - t0), flush=True)
    if a.out: cnf.to_file(a.out); print("written", a.out)
    if a.solve:
        from pysat.solvers import Solver
        with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
            res = s.solve(); print("result:", res, "time=%.1fs" % (time.time() - t0))
            if res:
                M, ok = lift(a.m, outer, rep, trep, A, B, s.get_model()); print("LIFT VERIFY srg identity:", ok)
                np.savetxt("orbit_sat_solution_m%d.txt" % a.m, M, fmt="%d")
