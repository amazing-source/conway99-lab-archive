"""Order-3 FPF branch, tau=6: filters on the graph F of adjacencies between the six triangular orbits.

Input: the 156 six-vertex graphs from notes/third_party/c3_suivi_generalisation/cases.json (third-party census,
independently replayed there).  For each F we compute
  (1) G0 = 6I + 6J - 5F - F^2  (= B B^T, B the binary 6x27 incidence to independent orbits)  [third-party status]
  (2) interlacing filter: lambda_2(2I+F) <= 3  (Q has spectrum 14, 3^18, (-4)^14; Cauchy interlacing on a 6x6 principal block)
  (3) refined Gram filters: 6I + F - (6/11)J >= 0 and I - F + (1/3)J >= 0 (principal blocks of the PSD matrices Q+4I-(6/11)J, 3I-Q+J/3)
  (4) exact binary factorisation: is there a multiset of 27 columns s in {0,1}^6 with sum s s^T = G0 ?  (CP-SAT ILP, witness re-verified in integers)
Outputs JSON next to this file.
"""
import json, sys, itertools, time
from pathlib import Path
import numpy as np
from fractions import Fraction
import sympy as sp
from ortools.sat.python import cp_model

HERE = Path(__file__).resolve().parent
CASES = Path(r"C:\Users\RESEARCHER\Desktop\conway99-involution\notes\third_party\c3_suivi_generalisation\cases.json")
data = json.loads(CASES.read_text(encoding="utf-8"))
cases = data["cases"]
assert len(cases) == 156

PAIRS = list(itertools.combinations(range(6), 2))  # same convention as the third-party verifier (adjacency(mask))

def adj_mask(mask):
    F = np.zeros((6, 6), dtype=int)
    for k, (i, j) in enumerate(PAIRS):
        if mask & (1 << k):
            F[i, j] = F[j, i] = 1
    return F

def adj(edges):
    F = np.zeros((6, 6), dtype=int)
    for a, b in edges:
        F[a, b] = F[b, a] = 1
    return F

I6 = np.eye(6, dtype=int); J6 = np.ones((6, 6), dtype=int)
supports = [np.array(s, dtype=int) for s in itertools.product([0, 1], repeat=6)]

def psd_exact(M):  # M sympy rational symmetric 6x6: PSD iff every principal minor is >= 0 (exact rationals)
    M = sp.Matrix(M); n = M.shape[0]
    for r in range(1, n + 1):
        for idx in itertools.combinations(range(n), r):
            if M.extract(list(idx), list(idx)).det() < 0:
                return False
    return True

def binary_factorisation(G0, ncols=27, timeout=60.0):
    m = cp_model.CpModel()
    n = [m.NewIntVar(0, ncols, f"n{i}") for i in range(64)]
    m.Add(sum(n) == ncols)
    for i in range(6):
        for j in range(i, 6):
            m.Add(sum(n[k] for k, s in enumerate(supports) if s[i] and s[j]) == int(G0[i, j]))
    solver = cp_model.CpSolver(); solver.parameters.max_time_in_seconds = timeout; solver.parameters.num_workers = 1
    st = solver.Solve(m)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        counts = {k: solver.Value(n[k]) for k in range(64) if solver.Value(n[k])}
        # exact re-verification
        acc = np.zeros((6, 6), dtype=int)
        for k, c in counts.items():
            acc += c * np.outer(supports[k], supports[k])
        assert (acc == G0).all() and sum(counts.values()) == ncols
        return "SAT", {format(k, "06b"): c for k, c in counts.items()}
    if st == cp_model.INFEASIBLE:
        return "UNSAT", None
    return "UNKNOWN", None

out = []
t0 = time.time()
for c in cases:
    F = adj_mask(c["mask"])
    if "edges" in c:
        assert (F == adj(c["edges"])).all(), c["mask"]
    G0 = 6 * I6 + 6 * J6 - 5 * F - F @ F
    lam = np.sort(np.linalg.eigvalsh(F.astype(float)))[::-1]
    interlace = bool(lam[1] <= 1 + 1e-9)
    Fs = sp.Matrix(F.tolist())
    Js = sp.ones(6, 6); Is = sp.eye(6)
    refined_plus = psd_exact(6 * Is + Fs - sp.Rational(6, 11) * Js)
    refined_minus = psd_exact(Is - Fs + sp.Rational(1, 3) * Js)
    rec = {"mask": c["mask"], "edges": [[int(a), int(b)] for a, b in zip(*np.nonzero(np.triu(F)))], "third_party_status": c["status"],
           "lambda2_F": float(lam[1]), "interlacing_ok": interlace,
           "block_Q_plus4_ok": bool(refined_plus), "block_3_minus_Q_ok": bool(refined_minus)}
    if c["status"] == "psd":
        res, wit = binary_factorisation(G0)
        rec["binary_factorisation"] = res; rec["witness_counts"] = wit
    out.append(rec)

summary = {
    "n_cases": len(out),
    "interlacing_ok": sum(r["interlacing_ok"] for r in out),
    "block_3_minus_Q_ok": sum(r["block_3_minus_Q_ok"] for r in out),
    "block_Q_plus4_ok": sum(r["block_Q_plus4_ok"] for r in out),
    "psd_cases": sum(r["third_party_status"] == "psd" for r in out),
    "psd_and_interlacing": sum(r["interlacing_ok"] for r in out if r["third_party_status"] == "psd"),
    "psd_and_block_3_minus_Q": sum(r["block_3_minus_Q_ok"] for r in out if r["third_party_status"] == "psd"),
    "binary_factorisation": {k: sum(1 for r in out if r.get("binary_factorisation") == k) for k in ("SAT", "UNSAT", "UNKNOWN")},
    "binary_SAT_masks": [r["mask"] for r in out if r.get("binary_factorisation") == "SAT"],
    "binary_SAT_and_block_3_minus_Q": sum(1 for r in out if r.get("binary_factorisation") == "SAT" and r["block_3_minus_Q_ok"]),
    "binary_SAT_degree_sequences": sorted(set(tuple(int(x) for x in sorted(adj_mask(r["mask"]).sum(1).tolist())) for r in out if r.get("binary_factorisation") == "SAT")),
    "seconds": round(time.time() - t0, 1),
}
(HERE / "tau6_triangle_motif_filters.json").write_text(json.dumps({"summary": summary, "cases": out}, indent=1), encoding="utf-8")
print(json.dumps(summary, indent=1))
