"""Fix some (or all) of the seven independent s=1 matchings M_c, c=(i,0), as unit clauses on top of the
validated orbit-level CNF (code/z2/orbit_sat.py, m=7) and run CaDiCaL 1.9.5 (pysat) with a wall-clock cap.
Also measures how many of the 1722 primary bits are decided by unit propagation alone (Minisat22.propagate).

Usage examples
  python fix_matchings.py --allsib --time 600                 # all 21 block pairs 'sibling' (every M_c block-internal)
  python fix_matchings.py --blocks 1,2,3,4,5,6,7 --seed 3     # random C1-consistent 7-tuple
  python fix_matchings.py --blocks 1 --type 6 --time 600      # only M_(1,0) fixed, of cycle type (6,)
  python fix_matchings.py --time 300                          # baseline, nothing fixed
Outputs a JSON line to results.jsonl in this directory.
"""
import argparse, json, os, random, sys, time, threading
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", ".."))
from structure import INNER, LABELS, Lc, sig, sigl, bit, perfect_matchings, matching_type, random_matching, s1_edges_from, c1_violations
import orbit_sat
from pysat.solvers import Solver

def matching_units(matchings, A, B):
    """Unit literals fixing the given matchings (dict c -> list of 6 label pairs)."""
    units = []
    for c, Mc in matchings.items():
        L = Lc(c); Ms = set(Mc)
        import itertools
        for w1, w2 in itertools.combinations(L, 2):
            kind, U, V = bit(w1, w2)
            var = A[U, V] if kind == 'a' else B[U, V]
            units.append(var if frozenset((w1, w2)) in Ms else -var)
    return units

def block_internal(c):
    return [frozenset((frozenset((c, d)), frozenset((c, sig(d))))) for d in INNER if d[0] != c[0] and d[1] == 0]

def pick_type(c, typ, rng):
    cands = [m for m in perfect_matchings(Lc(c)) if matching_type(c, m) == typ]
    return rng.choice(cands)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blocks", default="")
    ap.add_argument("--type", default="")         # e.g. "6" or "3,2,1" applied to every fixed block
    ap.add_argument("--allsib", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--case", default="none")
    ap.add_argument("--time", type=float, default=600)
    ap.add_argument("--tag", default="")
    ap.add_argument("--noprop", action="store_true")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    blocks = [int(x) for x in a.blocks.split(",") if x]
    if a.allsib: blocks = list(range(1, 8))
    typ = tuple(int(x) for x in a.type.split(",")) if a.type else None
    # choose matchings
    while True:
        matchings = {}
        for i in blocks:
            c = (i, 0)
            if a.allsib: matchings[c] = block_internal(c)
            elif typ: matchings[c] = pick_type(c, typ, rng)
            else: matchings[c] = random_matching(c, rng)
        if not matchings or c1_violations(s1_edges_from(matchings)) == 0: break
    types = {str(c): matching_type(c, m) for c, m in matchings.items()}
    t0 = time.time()
    cnf, pool, outer, rep, trep, A, B = orbit_sat.build(7, a.case)
    units = matching_units(matchings, A, B)
    nfix = len(units); npos = sum(1 for u in units if u > 0)
    print("fixed bits: %d (ones: %d) types=%s build=%.1fs" % (nfix, npos, types, time.time() - t0), flush=True)
    primary = sorted(set(A.values()) | set(B.values()))
    # --- unit propagation measure (Minisat22 has propagate())
    prop_fixed = None
    if not a.noprop:
        with Solver(name="minisat22", bootstrap_with=cnf.clauses) as ms:
            ok, lits = ms.propagate(assumptions=units)
            if not ok:
                prop_fixed = "CONFLICT"
            else:
                S = set(abs(l) for l in lits)
                prop_fixed = sum(1 for v in primary if v in S)
        print("unit propagation from the fixed bits decides %s of %d primary bits (%.1fs)" % (prop_fixed, len(primary), time.time() - t0), flush=True)
    # --- CaDiCaL with wall cap
    res = None; stats = {}
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
        for u in units: s.add_clause([u])
        timer = threading.Timer(a.time, lambda: s.interrupt()); timer.start()
        t1 = time.time()
        res = s.solve_limited(expect_interrupt=True)
        timer.cancel()
        wall = time.time() - t1
        stats = s.accum_stats()
        if res is True:
            model = s.get_model()
            Mx, ok = orbit_sat.lift(7, outer, rep, trep, A, B, model)
            print("SAT!  lift verifies srg identity:", ok, flush=True)
            import numpy as np
            np.savetxt(os.path.join(HERE, "SOLUTION_%s.txt" % (a.tag or "x")), Mx, fmt="%d")
            stats["lift_ok"] = bool(ok)
    out = {"tag": a.tag, "blocks": blocks, "allsib": a.allsib, "type": typ, "seed": a.seed, "case": a.case,
           "fixed_bits": nfix, "prop_fixed_primary": prop_fixed, "types": {k: list(v) for k, v in types.items()},
           "result": {True: "SAT", False: "UNSAT", None: "UNKNOWN"}[res], "wall": round(wall, 1), "stats": stats}
    print(json.dumps(out), flush=True)
    with open(os.path.join(HERE, "results.jsonl"), "a") as f: f.write(json.dumps(out) + "\n")

if __name__ == "__main__":
    main()
