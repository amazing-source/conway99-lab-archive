"""Run CaDiCaL (via pysat) on an orbit-level CNF with a wall-clock limit; verify any model by lifting.
Usage: python run_orbit.py --cnf k14_sib.cnf --case sib --time 14400
"""
import argparse, json, threading, time, sys
import numpy as np
from pysat.formula import CNF
from pysat.solvers import Solver
from orbit_sat import build, lift

ap = argparse.ArgumentParser(); ap.add_argument("--cnf"); ap.add_argument("--case"); ap.add_argument("--time", type=float, default=14400)
ap.add_argument("--solver", default="cadical195")
a = ap.parse_args()
t0 = time.time()
cnf = CNF(from_file=a.cnf)
out = {"case": a.case, "cnf": a.cnf, "solver": a.solver, "time_limit": a.time}
with Solver(name=a.solver, bootstrap_with=cnf.clauses, use_timer=True) as s:
    timer = threading.Timer(a.time, lambda: s.interrupt()); timer.start()
    res = s.solve_limited(expect_interrupt=True)
    timer.cancel()
    out["result"] = {True: "SAT", False: "UNSAT", None: "UNKNOWN_TIMEOUT"}[res]
    out["wall"] = time.time() - t0
    try:
        out["stats"] = s.accum_stats()
    except Exception:
        pass
    if res:
        _, _, outer, rep, trep, A, B = build(7, a.case)
        M, ok = lift(7, outer, rep, trep, A, B, s.get_model())
        out["lift_verified"] = bool(ok)
        np.savetxt("SOLUTION_%s.txt" % a.case, M, fmt="%d")
json.dump(out, open("result_%s.json" % a.case, "w"), indent=1)
print(json.dumps(out))
