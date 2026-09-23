"""Q-relaxation (ordinary orbit matrix) of the involution model: Q_out (42x42, entries 0/1/2, zero diagonal) with
q1_UV = [Q_UV>=1], q2_UV = [Q_UV=2] (q2 -> q1).  Implied by the (a,b) model via q1 = a|b, q2 = a&b:
 row sum 12; exactly one 2 per row (D matching); block counts: sum over V meeting block l of Q_UV = 2 if l in U else 4;
 Gram: for U != V: sum_W Q_UW Q_VW + Q_UV = 4 - Sh_UV  (Q_out^2 + Q_out = 12I + 4J - Nb Nb^T).
Usage: python genq.py --m 7 --case sib --out cnf/sibQ.cnf ; --m 2 --solve (must be SAT) ; --enum N (enumerate up to N
solutions with blocking clauses on q-vars, printing the time of each)."""
import argparse, time, json
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
def build(m, case="none", enc=EncType.seqcounter):
    k = 2 * m
    outer = [(i, j, e) for i in range(1, m + 1) for j in range(i + 1, m + 1) for e in (0, 1)]
    N = len(outer); pool = IDPool(); cnf = CNF(); Q1 = {}; Q2 = {}
    for U in range(N):
        for V in range(U + 1, N):
            Q1[U, V] = Q1[V, U] = pool.id(("q1", U, V)); Q2[U, V] = Q2[V, U] = pool.id(("q2", U, V))
            cnf.append([-Q2[U, V], Q1[U, V]])
    nprim = pool.top
    def prod(x, y):
        p = pool.id(("p", min(x, y), max(x, y))); cnf.extend([[-p, x], [-p, y], [p, -x, -y]]); return p
    def eq(lits, kk):
        if not lits: assert kk == 0; return
        if kk < 0 or kk > len(lits): cnf.append([]); return
        cnf.extend(CardEnc.equals(lits=lits, bound=kk, vpool=pool, encoding=enc).clauses)
    blocks = [set(o[:2]) for o in outer]
    for U in range(N):
        others = [V for V in range(N) if V != U]
        eq([Q1[U, V] for V in others] + [Q2[U, V] for V in others], k - 2)
        eq([Q2[U, V] for V in others], 1)
        for l in range(1, m + 1):
            lits = [Q1[U, V] for V in others if l in blocks[V]] + [Q2[U, V] for V in others if l in blocks[V]]
            eq(lits, 2 if l in blocks[U] else 4)
    for U in range(N):
        for V in range(U + 1, N):
            Ws = [W for W in range(N) if W != U and W != V]
            lits = []
            for W in Ws:
                lits += [prod(Q1[U, W], Q1[V, W]), prod(Q1[U, W], Q2[V, W]), prod(Q2[U, W], Q1[V, W]), prod(Q2[U, W], Q2[V, W])]
            sh = len(blocks[U] & blocks[V])
            eq(lits + [Q1[U, V], Q2[U, V]], 4 - sh)
    if case != "none":
        tgt = {"sib": (1, 2, 1), "one": (1, 3, 0), "dis": (3, 4, 0)}[case]
        D = outer.index(tgt); cnf.append([Q2[0, D]])
    return cnf, pool, outer, Q1, Q2, nprim
def decode(outer, Q1, Q2, model):
    import numpy as np
    N = len(outer); val = set(l for l in model if l > 0); Q = np.zeros((N, N), dtype=int)
    for U in range(N):
        for V in range(U + 1, N):
            Q[U, V] = Q[V, U] = (1 if Q1[U, V] in val else 0) + (1 if Q2[U, V] in val else 0)
    return Q
def check(outer, Q, m):
    import numpy as np
    N = len(outer); Nb = np.zeros((N, m), dtype=int)
    for U, (i, j, e) in enumerate(outer): Nb[U, i - 1] = Nb[U, j - 1] = 1
    lhs = Q @ Q + Q; rhs = (2 * m - 2) * np.eye(N, dtype=int) + 4 * np.ones((N, N), dtype=int) - Nb @ Nb.T
    return bool(np.array_equal(lhs, rhs)) and bool(np.all(Q.sum(1) == 2 * m - 2)) and bool(np.all((Q == 2).sum(1) == 1))
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--m", type=int, default=7); ap.add_argument("--case", default="none")
    ap.add_argument("--out"); ap.add_argument("--solve", action="store_true"); ap.add_argument("--enum", type=int, default=0)
    a = ap.parse_args(); t0 = time.time()
    cnf, pool, outer, Q1, Q2, nprim = build(a.m, a.case)
    print("Q-relax m=%d case=%s vars=%d clauses=%d build=%.1fs" % (a.m, a.case, pool.top, len(cnf.clauses), time.time() - t0), flush=True)
    if a.out: cnf.to_file(a.out); print("written", a.out)
    if a.solve or a.enum:
        from pysat.solvers import Solver
        import numpy as np
        with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
            n = 0
            while s.solve():
                mdl = s.get_model(); Q = decode(outer, Q1, Q2, mdl); n += 1
                print("solution %d at %.1fs verified=%s" % (n, time.time() - t0, check(outer, Q, a.m)), flush=True)
                if a.enum: np.savetxt("Qsol_m%d_%s_%d.txt" % (a.m, a.case, n), Q, fmt="%d")
                if n >= max(1, a.enum): break
                s.add_clause([-l for l in mdl if abs(l) <= nprim])
            if n == 0: print("UNSAT at %.1fs" % (time.time() - t0))
