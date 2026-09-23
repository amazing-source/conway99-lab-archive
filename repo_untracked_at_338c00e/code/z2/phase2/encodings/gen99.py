"""Direct 99-vertex (sigma-identified) CNF from code/z2/probe99/model.py, with u !~ sigma(u) forced and the
same case split on D(U0) as orbit_sat.py (sib: u0={(1,0),(2,0)} adjacent to {(1,0),(2,1)} and {(1,1),(2,0)}).
Usage: python gen99.py --k 14 --case sib --out cnf/sib_direct99.cnf ; --k 4 --count (control: must give the
same solutions as validate_k4 = srg(9,4,1,2))."""
import argparse, sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "probe99"))
from model import Instance, check_srg
from pysat.formula import CNF
ap = argparse.ArgumentParser(); ap.add_argument("--k", type=int, default=14); ap.add_argument("--case", default="none")
ap.add_argument("--out", default=None); ap.add_argument("--count", action="store_true"); a = ap.parse_args()
t0 = time.time(); inst = Instance(a.k, use_sigma=True, no_self_adjacent=True)
clauses = list(inst.clauses)
if a.case != "none":
    tgt = {"sib": ((0, 0), (1, 1)), "one": ((0, 0), (2, 0)), "dis": ((2, 0), (3, 0))}[a.case]
    lab = {inst.label_of[o]: o for o in inst.outer_ids}
    u0 = lab[frozenset((inst.inner_id[(0, 0)], inst.inner_id[(1, 0)]))]
    v = lab[frozenset((inst.inner_id[tgt[0]], inst.inner_id[tgt[1]]))]
    sv = inst.sigma_outer[v]
    clauses.append([inst.hvar(u0, v)]); clauses.append([inst.hvar(u0, sv)])
nl = sum(len(c) for c in clauses)
print("k=%d case=%s vars=%d clauses=%d literals=%d build=%.1fs" % (a.k, a.case, inst.vpool.top, len(clauses), nl, time.time() - t0), flush=True)
if a.out:
    cnf = CNF(from_clauses=clauses); cnf.to_file(a.out); print("written", a.out)
if a.count:
    from pysat.solvers import Solver
    hv = sorted(set(inst._pair_var.values())); n = 0; ok = 0
    with Solver(name="cadical195", bootstrap_with=clauses) as s:
        while s.solve():
            m = s.get_model(); n += 1
            good, msg = check_srg(inst.decode(m), a.k); ok += good
            s.add_clause([-l for l in m if abs(l) in set(hv)])
    print("COUNT solutions=%d verified=%d" % (n, ok))
