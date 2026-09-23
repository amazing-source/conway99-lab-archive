"""Q-only relaxation = Behbahani's orbit-matrix problem for p = 2, phi = 1 fixed point (thesis ch. 3, eq. (25)-(27)),
specialised to the rigid involution structure of srg(99,14,1,2) (k = 2m general).

Variables: for unordered outer-orbit pairs {U,V}: Q_UV = a_UV + b_UV in {0,1,2}, encoded by bits
   x1 = [Q>=1], x2 = [Q=2]  (x2 -> x1).
Constraints (all exact consequences of A^2+A-(k-2)I=2J; cf. joint_dfs.py docstring):
   (R)  sum_V Q_UV = k-2
   (D)  exactly one V with Q_UV = 2            (perfect matching D on the outer orbits)
   (Ib) block sums: sum_{V on block l} Q_UV = 2 if l in blocks(U) else 4
   (QG) Q-Gram, U != V: sum_W Q_UW Q_VW = 4 - Q_UV - Sh_UV   (Sh = number of shared blocks)
No sign (S) information is used: this is a relaxation of the joint model. UNSAT here would decide the branch;
SAT gives an orbit matrix (a candidate for the sign-lift), UNKNOWN is not evidence.
Usage: python q_only_cpsat.py --m 7 --case sib|one|dis|none --time 600 --workers 2 [--seed 0] [--log file]
"""
import argparse, json, sys, time
from ortools.sat.python import cp_model


def build(m, case="none"):
    k = 2 * m
    outer = [(i, j, e) for i in range(1, m + 1) for j in range(i + 1, m + 1) for e in (0, 1)]
    N = len(outer)
    BL = [set((i, j)) for (i, j, e) in outer]
    SH = [[len(BL[a] & BL[b]) for b in range(N)] for a in range(N)]
    mdl = cp_model.CpModel()
    X1 = {}; X2 = {}
    for U in range(N):
        for V in range(U + 1, N):
            x1 = mdl.NewBoolVar("x1_%d_%d" % (U, V)); x2 = mdl.NewBoolVar("x2_%d_%d" % (U, V))
            mdl.AddImplication(x2, x1)
            X1[U, V] = X1[V, U] = x1; X2[U, V] = X2[V, U] = x2
    P = {}
    def prod(x, y):
        key = (min(x.Index(), y.Index()), max(x.Index(), y.Index()))
        if key not in P:
            p = mdl.NewBoolVar("p%d_%d" % key)
            mdl.AddBoolAnd([x, y]).OnlyEnforceIf(p); mdl.AddBoolOr([x.Not(), y.Not()]).OnlyEnforceIf(p.Not()); P[key] = p
        return P[key]
    def Q(U, V):  # linear expression for Q_UV = x1 + x2
        return X1[U, V] + X2[U, V]
    for U in range(N):
        others = [V for V in range(N) if V != U]
        mdl.Add(sum(Q(U, V) for V in others) == k - 2)                              # (R)
        mdl.Add(sum(X2[U, V] for V in others) == 1)                                  # (D)
        for l in range(1, m + 1):                                                    # (Ib)
            onl = [V for V in others if l in BL[V]]
            mdl.Add(sum(Q(U, V) for V in onl) == (2 if l in BL[U] else 4))
    for U in range(N):                                                               # (QG)
        for V in range(U + 1, N):
            Ws = [W for W in range(N) if W != U and W != V]
            terms = []
            for W in Ws:
                # Q_UW * Q_VW = (x1+x2)(y1+y2) expanded into products of bits
                terms += [prod(X1[U, W], X1[V, W]), prod(X1[U, W], X2[V, W]), prod(X2[U, W], X1[V, W]), prod(X2[U, W], X2[V, W])]
            mdl.Add(sum(terms) + Q(U, V) == 4 - SH[U][V])
    if case != "none":
        tgt = {"sib": (1, 2, 1), "one": (1, 3, 0), "dis": (3, 4, 0)}[case]
        D = outer.index(tgt); mdl.Add(X2[0, D] == 1)
    return mdl, outer, X1, X2


def verify_orbit_matrix(m, outer, Qm):
    """Exact integer check of the quotient identity Q_out^2 + Q_out = (k-2) I + 4 J - Sh (k = 2m)."""
    import numpy as np
    k = 2 * m; N = len(outer)
    BL = [set((i, j)) for (i, j, e) in outer]
    Sh = np.array([[len(BL[a] & BL[b]) for b in range(N)] for a in range(N)], dtype=np.int64)
    Qn = np.array(Qm, dtype=np.int64)
    lhs = Qn @ Qn + Qn
    rhs = (k - 2) * np.eye(N, dtype=np.int64) + 4 * np.ones((N, N), dtype=np.int64) - Sh
    return bool(np.array_equal(lhs, rhs))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, default=7); ap.add_argument("--case", default="none")
    ap.add_argument("--time", type=float, default=600); ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--log", default=None)
    a = ap.parse_args(); t0 = time.time()
    mdl, outer, X1, X2 = build(a.m, a.case)
    N = len(outer)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = a.workers; solver.parameters.max_time_in_seconds = a.time
    solver.parameters.random_seed = a.seed
    solver.parameters.log_search_progress = a.log is not None
    if a.log:
        logf = open(a.log, "w")
        solver.parameters.log_to_stdout = False
        solver.log_callback = lambda s: (logf.write(s + "\n"), logf.flush())
    st = solver.Solve(mdl)
    name = {cp_model.OPTIMAL: "SAT", cp_model.FEASIBLE: "SAT", cp_model.INFEASIBLE: "UNSAT", cp_model.UNKNOWN: "UNKNOWN"}.get(st, str(st))
    out = {"model": "Q-only (Behbahani p=2 orbit matrix, rigid involution)", "m": a.m, "case": a.case, "workers": a.workers,
           "seed": a.seed, "result": name, "wall_s": round(time.time() - t0, 1), "conflicts": solver.NumConflicts(),
           "branches": solver.NumBranches(), "bools": len(mdl.Proto().variables), "constraints": len(mdl.Proto().constraints)}
    if name == "SAT":
        Qm = [[0] * N for _ in range(N)]
        for U in range(N):
            for V in range(N):
                if U != V: Qm[U][V] = solver.Value(X1[U, V]) + solver.Value(X2[U, V])
        out["orbit_matrix_verified"] = verify_orbit_matrix(a.m, outer, Qm)
        out["orbit_matrix"] = Qm
        dpairs = sorted(set(tuple(sorted((U, V))) for U in range(N) for V in range(N) if U != V and Qm[U][V] == 2))
        BL = [set((i, j)) for (i, j, e) in outer]
        types = {"sib": 0, "one": 0, "dis": 0}
        for (U, V) in dpairs:
            s = len(BL[U] & BL[V]); types[{2: "sib", 1: "one", 0: "dis"}[s]] += 1
        out["D_pair_types"] = types
    fn = "result_qonly_m%d_%s_seed%d.json" % (a.m, a.case, a.seed)
    json.dump(out, open(fn, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "orbit_matrix"}))
