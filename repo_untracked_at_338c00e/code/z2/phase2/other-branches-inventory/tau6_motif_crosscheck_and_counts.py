"""(1) Cross-check the 18 UNSAT binary factorisations with SCIP (OR-Tools pywraplp), an engine independent of CP-SAT.
(2) For each binary-feasible motif F, count the distinct multisets of 27 binary columns with sum s s^T = G0
    (CP-SAT enumerate_all_solutions, cap 200000 solutions / 60 s per motif, 1 worker)."""
import json, itertools, time
from pathlib import Path
import numpy as np
from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp

HERE = Path(__file__).resolve().parent
prev = json.loads((HERE / "tau6_triangle_motif_filters.json").read_text(encoding="utf-8"))["cases"]
PAIRS = list(itertools.combinations(range(6), 2))
supports = [np.array(s, dtype=int) for s in itertools.product([0, 1], repeat=6)]
I6 = np.eye(6, dtype=int); J6 = np.ones((6, 6), dtype=int)

def adj_mask(mask):
    F = np.zeros((6, 6), dtype=int)
    for k, (i, j) in enumerate(PAIRS):
        if mask & (1 << k): F[i, j] = F[j, i] = 1
    return F

def scip_check(G0):
    s = pywraplp.Solver.CreateSolver("SCIP")
    if s is None: return "NO_SCIP"
    n = [s.IntVar(0, 27, f"n{i}") for i in range(64)]
    s.Add(sum(n) == 27)
    for i in range(6):
        for j in range(i, 6):
            s.Add(sum(n[k] for k, sp in enumerate(supports) if sp[i] and sp[j]) == int(G0[i, j]))
    s.SetTimeLimit(60000)
    st = s.Solve()
    return {pywraplp.Solver.OPTIMAL: "SAT", pywraplp.Solver.FEASIBLE: "SAT", pywraplp.Solver.INFEASIBLE: "UNSAT"}.get(st, f"OTHER_{st}")

class Counter(cp_model.CpSolverSolutionCallback):
    def __init__(self, cap): super().__init__(); self.n = 0; self.cap = cap
    def on_solution_callback(self):
        self.n += 1
        if self.n >= self.cap: self.StopSearch()

def count_B(G0, cap=200000, tlim=60.0):
    m = cp_model.CpModel()
    n = [m.NewIntVar(0, 27, f"n{i}") for i in range(64)]
    m.Add(sum(n) == 27)
    for i in range(6):
        for j in range(i, 6):
            m.Add(sum(n[k] for k, sp in enumerate(supports) if sp[i] and sp[j]) == int(G0[i, j]))
    solver = cp_model.CpSolver(); solver.parameters.enumerate_all_solutions = True
    solver.parameters.num_workers = 1; solver.parameters.max_time_in_seconds = tlim
    cb = Counter(cap); st = solver.Solve(m, cb)
    complete = (st == cp_model.OPTIMAL) and cb.n < cap
    return cb.n, complete, solver.StatusName(st)

res = {"scip_crosscheck": {}, "B_counts": {}}
t0 = time.time()
for r in prev:
    if "binary_factorisation" not in r: continue
    F = adj_mask(r["mask"]); G0 = 6 * I6 + 6 * J6 - 5 * F - F @ F
    if r["binary_factorisation"] == "UNSAT":
        res["scip_crosscheck"][r["mask"]] = scip_check(G0)
    else:
        n, complete, st = count_B(G0)
        res["B_counts"][r["mask"]] = {"edges": r["edges"], "n_multisets": n, "complete": complete, "status": st}
res["seconds"] = round(time.time() - t0, 1)
res["scip_summary"] = {k: sum(1 for v in res["scip_crosscheck"].values() if v == k) for k in set(res["scip_crosscheck"].values())}
(HERE / "tau6_motif_crosscheck_and_counts.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps({"scip_summary": res["scip_summary"], "seconds": res["seconds"]}))
for k, v in res["B_counts"].items():
    print(k, v["edges"], "B multisets:", v["n_multisets"], "complete" if v["complete"] else "CAPPED/TIMEOUT", v["status"])
