"""Fallback plain DFS/backtracking search (row by row, with orthogonality
pruning) for the outer-outer block s[U,V] in {-1,0,1}, default diagonal (0).

Variable order: for r = 0..M-1, for c = r+1..M-1: assign s[r][c] (mirrored).
When row r completes (c reaches M-1), we check:
  - diagonal identity: sum_c s[r][c]^2 (c != r, incl. mirrored earlier cols) == k-4
  - for every r' < r: dot(row_r, row_r') == -C[r,r'] - s[r,r']
Partial pruning while filling row r:
  - running sum of squares vs remaining slots (must be able to hit target exactly)
  - running dot product with each completed row r' vs remaining slots (must be
    able to hit the required exact target)

Time/­node capped; reports how far it got (nodes, max depth reached, cap hit).
"""
import argparse
import json
import time

from common import build_orbits, cross_const


def run_dfs(m, k, time_limit=1200.0, node_cap=None):
    inner, outer = build_orbits(m)
    M = len(outer)
    C = [[cross_const(outer[a], outer[b], m) for b in range(M)] for a in range(M)]
    d = [0] * M  # default diagonal
    diag_target = (k - 4) - 0  # sum_{c!=r} s[r][c]^2 == k-4 (d_r=0)

    # matrix of assigned values; None = unset. diagonal fixed to d[r].
    S = [[None] * M for _ in range(M)]
    for r in range(M):
        S[r][r] = d[r]

    total_vars = M * (M - 1) // 2
    order = [(r, c) for r in range(M) for c in range(r + 1, M)]

    t0 = time.time()
    stats = {'nodes': 0, 'max_depth': 0, 'completed_rows_best': 0,
             'time_cap_hit': False, 'node_cap_hit': False}

    solution_holder = {}

    def row_complete_check(r):
        # diagonal check
        sq = sum(S[r][c] * S[r][c] for c in range(M) if c != r)
        if sq != diag_target:
            return False
        # pairwise with earlier completed rows
        for rp in range(r):
            dot = sum(S[r][c] * S[rp][c] for c in range(M))
            target = -C[r][rp] - S[r][rp]
            if dot != target:
                return False
        return True

    def partial_ok(r, c_last):
        # sum of squares bound for row r using entries c=0..c_last (mirrors + new)
        assigned = [S[r][c] for c in range(M) if c != r and S[r][c] is not None]
        sq = sum(v * v for v in assigned)
        remaining = (M - 1) - len(assigned)
        if sq > diag_target or sq + remaining < diag_target:
            return False
        # dot-product bound against completed earlier rows using assigned cols so far
        for rp in range(r):
            # s[r][rp] was fixed earlier (when row rp completed, since rp < r),
            # so this is always known by the time row r is being built.
            partial_dot = 0
            unknown = 0
            for c in range(M):
                if c == r:
                    continue
                if S[r][c] is not None:
                    partial_dot += S[r][c] * S[rp][c]
                else:
                    unknown += 1
            target = -C[r][rp] - S[r][rp]
            if partial_dot > target + unknown or partial_dot < target - unknown:
                return False
        return True

    def dfs(idx, depth):
        stats['nodes'] += 1
        stats['max_depth'] = max(stats['max_depth'], depth)
        if time.time() - t0 > time_limit:
            stats['time_cap_hit'] = True
            return False
        if node_cap and stats['nodes'] > node_cap:
            stats['node_cap_hit'] = True
            return False
        if idx == total_vars:
            solution_holder['S'] = [row[:] for row in S]
            return True
        r, c = order[idx]
        for val in (0, 1, -1):
            S[r][c] = val
            S[c][r] = val
            ok = partial_ok(r, c)
            if ok:
                if c == M - 1:
                    ok = row_complete_check(r)
                if ok:
                    stats['completed_rows_best'] = max(stats['completed_rows_best'], r + (1 if c == M - 1 else 0))
                    if dfs(idx + 1, depth + 1):
                        return True
                    if stats['time_cap_hit'] or stats['node_cap_hit']:
                        return False
            S[r][c] = None
            S[c][r] = None
        return False

    found = dfs(0, 0)
    elapsed = time.time() - t0
    result = {
        'm': m, 'k': k, 'found_solution': found,
        'elapsed_sec': elapsed, 'total_vars': total_vars,
        **stats,
    }
    return result, solution_holder.get('S'), outer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--m', type=int, required=True)
    ap.add_argument('--k', type=int, required=True)
    ap.add_argument('--time-limit', type=float, default=1200.0)
    ap.add_argument('--node-cap', type=int, default=None)
    ap.add_argument('--out', type=str, default=None)
    args = ap.parse_args()

    result, S, outer = run_dfs(args.m, args.k, time_limit=args.time_limit, node_cap=args.node_cap)
    print(json.dumps(result, indent=2))
    if S is not None and args.out:
        from common import build_full_matrix, verify
        import numpy as np
        # rebuild full matrix using S (outer-outer) and default diag/offdiag dict form
        diag = {outer[i]: 0 for i in range(len(outer))}
        offdiag = {}
        for a in range(len(outer)):
            for b in range(a + 1, len(outer)):
                offdiag[frozenset((outer[a], outer[b]))] = S[a][b]
        Sfull, idx = build_full_matrix(args.m, outer, diag, offdiag)
        ok, lhs = verify(Sfull, args.k)
        print("verify_ok=", ok)
        with open(args.out, 'w') as f:
            f.write(f"# DFS solution m={args.m} k={args.k} verify_ok={ok}\n")
            for row in Sfull:
                f.write(' '.join(str(int(x)) for x in row) + "\n")


if __name__ == '__main__':
    main()
