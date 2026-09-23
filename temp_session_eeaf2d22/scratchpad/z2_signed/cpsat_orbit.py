"""CP-SAT version of the orbit-level involution model (same constraints as orbit_sat.py).
Usage: python cpsat_orbit.py --m 7 --case none --workers 6 --time 7200
"""
import argparse, json, time
import numpy as np
from ortools.sat.python import cp_model
from orbit_sat import lift

def build_cp(m, case):
    k = 2 * m
    outer = [(i, j, e) for i in range(1, m + 1) for j in range(i + 1, m + 1) for e in (0, 1)]
    N = len(outer)
    rep = [frozenset([(i, 0), (j, e)]) for (i, j, e) in outer]
    trep = [frozenset([(i, 1), (j, 1 - e)]) for (i, j, e) in outer]
    mdl = cp_model.CpModel(); A = {}; B = {}; P = {}
    for U in range(N):
        for V in range(U + 1, N):
            A[U, V] = A[V, U] = mdl.NewBoolVar("a%d_%d" % (U, V)); B[U, V] = B[V, U] = mdl.NewBoolVar("b%d_%d" % (U, V))
    def prod(x, y):
        key = (min(x.Index(), y.Index()), max(x.Index(), y.Index()))
        if key not in P:
            p = mdl.NewBoolVar("p%d_%d" % key); mdl.AddBoolAnd([x, y]).OnlyEnforceIf(p); mdl.AddBoolOr([x.Not(), y.Not()]).OnlyEnforceIf(p.Not()); P[key] = p
        return P[key]
    inner = [(i, s) for i in range(1, m + 1) for s in (0, 1)]
    for U in range(N):
        others = [V for V in range(N) if V != U]
        mdl.Add(sum(A[U, V] + B[U, V] for V in others) == k - 2)
        mdl.Add(sum(prod(A[U, V], B[U, V]) for V in others) == 1)
        for c in inner:
            partner = (c[0], 1 - c[1]); lits = []
            for V in others:
                if c in rep[V]: lits.append(A[U, V])
                if c in trep[V]: lits.append(B[U, V])
            mdl.Add(sum(lits) == (1 if (c in rep[U] or partner in rep[U]) else 2))
    for U in range(N):
        for V in range(U + 1, N):
            Ws = [W for W in range(N) if W != U and W != V]
            mdl.Add(sum(prod(A[U, W], A[V, W]) + prod(B[U, W], B[V, W]) for W in Ws) + A[U, V] == 2 - len(rep[U] & rep[V]))
            mdl.Add(sum(prod(A[U, W], B[V, W]) + prod(B[U, W], A[V, W]) for W in Ws) + B[U, V] == 2 - len(rep[U] & trep[V]))
    if case != "none":
        tgt = {"sib": (1, 2, 1), "one": (1, 3, 0), "dis": (3, 4, 0)}[case]; D = outer.index(tgt)
        mdl.Add(A[0, D] == 1); mdl.Add(B[0, D] == 1)
    return mdl, outer, rep, trep, A, B

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--m", type=int, default=7); ap.add_argument("--case", default="none")
    ap.add_argument("--workers", type=int, default=6); ap.add_argument("--time", type=float, default=7200); ap.add_argument("--rowfix-seed", type=int, default=None)
    a = ap.parse_args(); t0 = time.time()
    mdl, outer, rep, trep, A, B = build_cp(a.m, a.case)
    if a.rowfix_seed is not None:
        import random; from row_fix import random_row
        row = random_row(outer, rep, trep, a.m, random.Random(a.rowfix_seed), None if a.case == "none" else a.case)
        for V, (x, y) in row.items(): mdl.Add(A[0, V] == x); mdl.Add(B[0, V] == y)
        print("row fixed, seed", a.rowfix_seed, flush=True)
    solver = cp_model.CpSolver(); solver.parameters.num_workers = a.workers; solver.parameters.max_time_in_seconds = a.time
    solver.parameters.log_search_progress = False
    st = solver.Solve(mdl)
    name = {cp_model.OPTIMAL: "SAT", cp_model.FEASIBLE: "SAT", cp_model.INFEASIBLE: "UNSAT", cp_model.UNKNOWN: "UNKNOWN"}.get(st, str(st))
    out = {"m": a.m, "case": a.case, "result": name, "wall": time.time() - t0, "conflicts": solver.NumConflicts(), "branches": solver.NumBranches()}
    if name == "SAT":
        model = [ (v.Index() + 1) if solver.Value(v) else -(v.Index() + 1) for v in list({id(x): x for x in list(A.values()) + list(B.values())}.values())]
        # rebuild a pysat-style model over the same variable ids used by lift: use direct construction instead
        N = len(outer); k = 2 * a.m; n = 1 + 2 * a.m + 2 * N
        idx = {}; innerv = [(i, s) for i in range(1, a.m + 1) for s in (0, 1)]
        for t, v in enumerate(innerv): idx[v] = 1 + t
        for U in range(N): idx[rep[U]] = 1 + 2 * a.m + 2 * U; idx[trep[U]] = 1 + 2 * a.m + 2 * U + 1
        M = np.zeros((n, n), dtype=np.int64)
        for v in innerv: M[0, idx[v]] = M[idx[v], 0] = 1
        for i in range(1, a.m + 1): M[idx[(i, 0)], idx[(i, 1)]] = M[idx[(i, 1)], idx[(i, 0)]] = 1
        for U in range(N):
            for lab in (rep[U], trep[U]):
                for v in lab: M[idx[lab], idx[v]] = M[idx[v], idx[lab]] = 1
        for U in range(N):
            for V in range(U + 1, N):
                av, bv = solver.Value(A[U, V]), solver.Value(B[U, V])
                u, tu, v, tv = idx[rep[U]], idx[trep[U]], idx[rep[V]], idx[trep[V]]
                M[u, v] = M[v, u] = M[tu, tv] = M[tv, tu] = av; M[u, tv] = M[tv, u] = M[tu, v] = M[v, tu] = bv
        out["lift_verified"] = bool(np.array_equal(M @ M + M - (k - 2) * np.eye(n, dtype=np.int64), 2 * np.ones((n, n), dtype=np.int64)))
        np.savetxt("SOLUTION_cpsat_%s.txt" % a.case, M, fmt="%d")
    json.dump(out, open("result_cpsat_%s.json" % a.case, "w"), indent=1); print(json.dumps(out))
