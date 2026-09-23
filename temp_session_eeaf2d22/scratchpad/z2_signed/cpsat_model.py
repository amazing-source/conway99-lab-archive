"""Generic CP-SAT builder/solver for the Z2-quotient signed matrix problem.

Usage: python cpsat_model.py --m M --k K [--relax-diag] [--time-limit SECS]
                              [--workers N] [--out OUTFILE] [--enumerate]
"""
import argparse
import json
import sys
import time

from ortools.sat.python import cp_model

from common import build_orbits, cross_const, build_full_matrix, verify


def build_model(m, k, relax_diag=False):
    inner, outer = build_orbits(m)
    M = len(outer)
    model = cp_model.CpModel()

    # off-diagonal unknown vars s[{U,V}] in {-1,0,1}
    s = {}
    for a in range(M):
        for b in range(a + 1, M):
            U, V = outer[a], outer[b]
            s[frozenset((U, V))] = model.NewIntVar(-1, 1, f's_{a}_{b}')

    # diagonal: constant 0, or variable in {-1,0} if relaxed
    d = {}
    for a, U in enumerate(outer):
        if relax_diag:
            d[U] = model.NewIntVar(-1, 0, f'd_{a}')
        else:
            d[U] = 0

    def sVar(U, V):
        if U == V:
            return d[U]
        return s[frozenset((U, V))]

    n_mult = 0
    n_lin = 0
    for a in range(M):
        for b in range(a, M):
            U, V = outer[a], outer[b]
            C = cross_const(U, V, m)
            total_const = 0
            total_lin = []
            for w, W in enumerate(outer):
                pu = sVar(U, W)
                pv = sVar(W, V)
                if isinstance(pu, int) and isinstance(pv, int):
                    total_const += pu * pv
                elif isinstance(pu, int):
                    if pu != 0:
                        total_lin.append(pu * pv)
                        n_lin += 1
                elif isinstance(pv, int):
                    if pv != 0:
                        total_lin.append(pv * pu)
                        n_lin += 1
                else:
                    aux = model.NewIntVar(-1, 1, f'p_{a}_{b}_{w}')
                    model.AddMultiplicationEquality(aux, [pu, pv])
                    total_lin.append(aux)
                    n_mult += 1
            # add S[U,V] term itself
            diagUV = sVar(U, V)
            if isinstance(diagUV, int):
                total_const += diagUV
            else:
                total_lin.append(diagUV)

            rhs_target = (k - 2) if U == V else 0
            rhs = rhs_target - total_const - C
            if total_lin:
                model.Add(sum(total_lin) == rhs)
            else:
                # no variables at all -- pure identity check on fixed structure
                if rhs != 0:
                    raise RuntimeError(
                        f"Infeasible constant mismatch at U={U} V={V}: need 0=={rhs}"
                    )
    return model, inner, outer, s, d, {'n_mult': n_mult, 'n_lin': n_lin}


def solve(m, k, relax_diag=False, time_limit=60.0, workers=8, enumerate_all=False,
          log_search=False):
    t0 = time.time()
    model, inner, outer, s, d, stats = build_model(m, k, relax_diag=relax_diag)
    build_time = time.time() - t0

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    # enumerate_all_solutions requires a single-worker deterministic search in CP-SAT;
    # parallel portfolio workers can otherwise re-report the same solution.
    solver.parameters.num_search_workers = 1 if enumerate_all else workers
    solver.parameters.log_search_progress = log_search

    solutions = []
    if enumerate_all:
        class Collector(cp_model.CpSolverSolutionCallback):
            def __init__(self, s, d, outer):
                super().__init__()
                self.s = s
                self.d = d
                self.outer = outer
                self.count = 0

            def on_solution_callback(self):
                self.count += 1
                offdiag = {key: self.Value(v) for key, v in self.s.items()}
                diag = {U: (self.Value(v) if not isinstance(v, int) else v)
                        for U, v in self.d.items()}
                solutions.append((offdiag, diag))

        model.AddDecisionStrategy([v for v in s.values()], cp_model.CHOOSE_FIRST,
                                   cp_model.SELECT_MIN_VALUE)
        collector = Collector(s, d, outer)
        solver.parameters.enumerate_all_solutions = True
        status = solver.Solve(model, collector)
    else:
        status = solver.Solve(model)

    result = {
        'm': m, 'k': k, 'relax_diag': relax_diag,
        'status': solver.StatusName(status),
        'wall_time': solver.WallTime(),
        'build_time': build_time,
        'num_conflicts': solver.NumConflicts(),
        'num_branches': solver.NumBranches(),
        'n_mult_constraints': stats['n_mult'],
        'n_outer': len(outer),
        'n_inner': len(inner),
        'N_total': len(inner) + len(outer),
    }

    sol = None
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        offdiag = {key: solver.Value(v) for key, v in s.items()}
        diag = {U: (solver.Value(v) if not isinstance(v, int) else v) for U, v in d.items()}
        sol = (offdiag, diag)

    return result, sol, solutions, (inner, outer)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--m', type=int, required=True)
    ap.add_argument('--k', type=int, required=True)
    ap.add_argument('--relax-diag', action='store_true')
    ap.add_argument('--time-limit', type=float, default=60.0)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--enumerate', action='store_true')
    ap.add_argument('--out', type=str, default=None)
    ap.add_argument('--log', action='store_true')
    args = ap.parse_args()

    result, sol, solutions, (inner, outer) = solve(
        args.m, args.k, relax_diag=args.relax_diag, time_limit=args.time_limit,
        workers=args.workers, enumerate_all=args.enumerate, log_search=args.log)

    print(json.dumps(result, indent=2))

    if args.enumerate:
        print(f"Total solutions enumerated: {len(solutions)}")
        for idx, (offdiag, diag) in enumerate(solutions):
            S, _ = build_full_matrix(args.m, outer, diag, offdiag)
            ok, lhs = verify(S, args.k)
            print(f"--- solution {idx} verify_ok={ok} ---")
            print(S)
    elif sol is not None:
        offdiag, diag = sol
        S, idx = build_full_matrix(args.m, outer, diag, offdiag)
        ok, lhs = verify(S, args.k)
        print(f"verify_ok={ok}")
        if args.out:
            with open(args.out, 'w') as f:
                f.write(f"# m={args.m} k={args.k} relax_diag={args.relax_diag} status={result['status']} verify_ok={ok}\n")
                f.write(f"# order: {inner + outer}\n")
                for row in S:
                    f.write(' '.join(str(int(x)) for x in row) + "\n")
            print(f"Saved matrix to {args.out}")
    else:
        print("No solution to verify (status=%s)" % result['status'])


if __name__ == '__main__':
    main()
