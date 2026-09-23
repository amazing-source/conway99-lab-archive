"""Run CaDiCaL (via pysat) on the k=14 instance with a hard wall-clock timeout,
using Solver.interrupt() from a watchdog thread. Reports SAT/UNSAT/UNKNOWN,
elapsed time, and solver statistics (conflicts, decisions, ...).
If SAT: decode, verify with the independent integer checker, and save
adjacency.txt (only if the check passes).
"""
import argparse
import sys
import threading
import time
import json
import numpy as np
from pysat.solvers import Solver
from model import Instance, check_srg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-self-adjacent', action='store_true')
    ap.add_argument('--timeout', type=float, default=1200.0)
    ap.add_argument('--solver', default='cadical195')
    ap.add_argument('--tag', default='run')
    args = ap.parse_args()

    print("[%s] building instance k=14 sigma=True no_self_adjacent=%s ..." % (args.tag, args.no_self_adjacent))
    t_build0 = time.time()
    inst = Instance(14, use_sigma=True, no_self_adjacent=args.no_self_adjacent)
    t_build1 = time.time()
    nvars = inst.vpool.top
    nclauses = len(inst.clauses)
    print("[%s] built: vars=%d clauses=%d build_time=%.1fs" % (args.tag, nvars, nclauses, t_build1 - t_build0))
    sys.stdout.flush()

    t_load0 = time.time()
    s = Solver(name=args.solver, bootstrap_with=inst.clauses, use_timer=True)
    t_load1 = time.time()
    print("[%s] loaded into %s in %.1fs" % (args.tag, args.solver, t_load1 - t_load0))
    sys.stdout.flush()

    result = {}

    def worker():
        result['sat'] = s.solve()

    th = threading.Thread(target=worker)
    t0 = time.time()
    th.start()
    th.join(timeout=args.timeout)
    timed_out = th.is_alive()
    if timed_out:
        print("[%s] TIMEOUT after %.0fs -> interrupting solver" % (args.tag, args.timeout))
        s.interrupt()
        th.join(timeout=60)
    elapsed = time.time() - t0

    status = result.get('sat', None)
    if timed_out and status is None:
        status_str = "UNKNOWN (timeout)"
    elif status is True:
        status_str = "SAT"
    elif status is False:
        status_str = "UNSAT"
    else:
        status_str = "UNKNOWN"

    try:
        stats = s.accum_stats()
    except Exception as e:
        stats = {"error": str(e)}

    print("[%s] STATUS=%s elapsed=%.1fs stats=%s" % (args.tag, status_str, elapsed, stats))

    out = {
        "tag": args.tag,
        "k": 14,
        "use_sigma": True,
        "no_self_adjacent": args.no_self_adjacent,
        "solver": args.solver,
        "vars": nvars,
        "clauses": nclauses,
        "build_time_sec": t_build1 - t_build0,
        "status": status_str,
        "elapsed_sec": elapsed,
        "timeout_sec": args.timeout,
        "stats": stats,
    }

    if status is True:
        model = s.get_model()
        A = inst.decode(model)
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
            print("[%s] WARNING: solver returned SAT but independent check FAILED - not saving, treat as bug" % args.tag)

    s.delete()

    with open("result_%s.json" % args.tag, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("[%s] wrote result_%s.json" % (args.tag, args.tag))


if __name__ == '__main__':
    main()
