"""Experiment: fix the whole row of the reference orbit U0=(1,2,0) (the H-neighbourhood of u0) to a random valid
assignment and measure CaDiCaL's time to decide the remaining instance.
Usage: python row_fix.py --seed 1 --time 600 [--dtype sib|one|dis]
"""
import argparse, json, random, threading, time
from pysat.formula import CNF
from pysat.solvers import Solver
from orbit_sat import build, lift
import numpy as np

def random_row(outer, rep, trep, m, rng, dtype=None):
    """Random valid (a,b)-row for U0: counters per inner vertex, exactly one (1,1), sum 12."""
    N = len(outer); U0 = 0
    inner = [(i, s) for i in range(1, m + 1) for s in (0, 1)]
    tgt = {c: (1 if (c in rep[U0] or (c[0], 1 - c[1]) in rep[U0]) else 2) for c in inner}
    order = [V for V in range(1, N)]
    rng.shuffle(order)
    dtarget = None
    if dtype:
        dtarget = outer.index({"sib": (1, 2, 1), "one": (1, 3, 0), "dis": (3, 4, 0)}[dtype])
    cnt = {c: 0 for c in inner}; row = {}
    def rec(k, tot, two):
        if tot > 12 or two > 1: return False
        if k == len(order):
            return tot == 12 and two == 1 and all(cnt[c] == tgt[c] for c in inner)
        V = order[k]
        opts = [(0, 0), (1, 0), (0, 1), (1, 1)]
        rng.shuffle(opts)
        if dtarget is not None:
            opts = [(1, 1)] if V == dtarget else [o for o in opts if o != (1, 1)]
        for (a, b) in opts:
            add = []
            if a: add += list(rep[V])
            if b: add += list(trep[V])
            if any(cnt[c] + add.count(c) > tgt[c] for c in set(add)): continue
            for c in add: cnt[c] += 1
            row[V] = (a, b)
            if rec(k + 1, tot + a + b, two + (a and b)): return True
            for c in add: cnt[c] -= 1
            del row[V]
        return False
    assert rec(0, 0, 0)
    return row

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=1); ap.add_argument("--time", type=float, default=600)
    ap.add_argument("--dtype", default=None); ap.add_argument("--solver", default="cadical195")
    a = ap.parse_args(); rng = random.Random(a.seed)
    t0 = time.time()
    cnf, pool, outer, rep, trep, A, B = build(7, "none")
    row = random_row(outer, rep, trep, 7, rng, a.dtype)
    units = []
    for V, (x, y) in row.items():
        units.append(A[0, V] if x else -A[0, V]); units.append(B[0, V] if y else -B[0, V])
    dv = [V for V, (x, y) in row.items() if x and y][0]
    print("seed", a.seed, "double orbit:", outer[dv], "row built t=%.1fs" % (time.time() - t0), flush=True)
    with Solver(name=a.solver, bootstrap_with=cnf.clauses + [[u] for u in units], use_timer=True) as s:
        timer = threading.Timer(a.time, lambda: s.interrupt()); timer.start()
        res = s.solve_limited(expect_interrupt=True); timer.cancel()
        out = {"seed": a.seed, "dtype": a.dtype, "double": outer[dv], "result": {True: "SAT", False: "UNSAT", None: "UNKNOWN"}[res], "wall": time.time() - t0}
        if res:
            M, ok = lift(7, outer, rep, trep, A, B, s.get_model()); out["lift_verified"] = bool(ok)
            np.savetxt("SOLUTION_rowfix_seed%d.txt" % a.seed, M, fmt="%d")
    json.dump(out, open("rowfix_seed%d.json" % a.seed, "w")); print(json.dumps(out))
