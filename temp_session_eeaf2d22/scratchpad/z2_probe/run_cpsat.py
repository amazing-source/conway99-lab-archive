"""Run OR-Tools CP-SAT on the k=14, sigma-invariant + no-self-adjacent instance
(task 3 (ii) target), with a hard wall-clock time limit and num_workers capped
by the CPU budget given by the coordinator (default 4, NOT 8 - machine is shared).
"""
import argparse
import time
import json
import numpy as np
from ortools.sat.python import cp_model
from model import Instance, build_cpsat, decode_cpsat, check_srg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--timeout', type=float, default=1200.0)
    ap.add_argument('--no-self-adjacent', action='store_true', default=True)
    ap.add_argument('--tag', default='cpsat_run')
    args = ap.parse_args()

    print("[%s] building instance k=14 sigma=True no_self_adjacent=%s ..." % (args.tag, args.no_self_adjacent))
    t0 = time.time()
    inst = Instance(14, use_sigma=True, no_self_adjacent=args.no_self_adjacent)
    t1 = time.time()
    print("[%s] instance built in %.1fs (num_outer=%d, distinct H-vars=%d)"
          % (args.tag, t1 - t0, inst.num_outer, len(set(inst._pair_var.values()))))

    model, hvars = build_cpsat(inst)
    t2 = time.time()
    print("[%s] cp-sat model built in %.1fs: bool_vars(H)=%d" % (args.tag, t2 - t1, len(hvars)))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.timeout
    solver.parameters.num_workers = args.workers
    solver.parameters.log_search_progress = True

    t3 = time.time()
    status = solver.Solve(model)
    elapsed = time.time() - t3
    status_name = solver.StatusName(status)
    print("[%s] STATUS=%s elapsed=%.1fs" % (args.tag, status_name, elapsed))
    print("[%s] NumConflicts=%d NumBranches=%d WallTime=%.1f" %
          (args.tag, solver.NumConflicts(), solver.NumBranches(), solver.WallTime()))

    out = {
        "tag": args.tag,
        "k": 14,
        "use_sigma": True,
        "no_self_adjacent": args.no_self_adjacent,
        "workers": args.workers,
        "timeout_sec": args.timeout,
        "build_time_sec": t2 - t0,
        "status": status_name,
        "elapsed_sec": elapsed,
        "num_conflicts": solver.NumConflicts(),
        "num_branches": solver.NumBranches(),
        "wall_time": solver.WallTime(),
    }

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        A = decode_cpsat(inst, solver, hvars)
        ok, msg = check_srg(A, 14)
        out["decode_check_ok"] = ok
        out["decode_check_msg"] = msg
        print("[%s] decode+check: ok=%s msg=%s" % (args.tag, ok, msg))
        if ok:
            adj_path = "adjacency_%s.txt" % args.tag
            np.savetxt(adj_path, A, fmt="%d")
            out["adjacency_path"] = adj_path
            print("[%s] SAVED adjacency matrix to %s" % (args.tag, adj_path))
        else:
            print("[%s] WARNING: CP-SAT returned %s but independent check FAILED - not saving, treat as bug"
                  % (args.tag, status_name))

    with open("result_%s.json" % args.tag, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("[%s] wrote result_%s.json" % (args.tag, args.tag))


if __name__ == '__main__':
    main()
