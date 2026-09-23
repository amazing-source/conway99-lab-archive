"""Row-by-row DFS for the outer signed quotient S_out (42x42, entries {0,+1,-1}, zero diagonal)
of a hypothetical Conway-99 graph with an involution (unique fixed vertex).
Constraints (exact, derived from S*S + S = 12 I on the 49x49 signed quotient):
  (W) every row has exactly 10 nonzero entries;
  (B) C^T S_out = 0: for every block l, sum_V s[U,V]*c_l(V) = 0;
  (G) for U != V: <s_U, s_V> = -s[U,V] - G[U,V], G = C C^T (inner Gram, fixed).
Rows are filled in index order; entries s[r][j] for j<r are fixed by symmetry.
Usage: python sout_dfs.py --nodes 3000000 [--seed-row FILE]
"""
import argparse, itertools, json, sys, time

M = 7
outer = [(i, j, e) for i in range(1, M + 1) for j in range(i + 1, M + 1) for e in (0, 1)]
N = len(outer)  # 42
def csign(V, l):
    i, j, e = V
    return 1 if l == i else ((-1 if e else 1) if l == j else 0)
C = [[csign(V, l) for l in range(1, M + 1)] for V in outer]
G = [[sum(C[a][l] * C[b][l] for l in range(M)) for b in range(N)] for a in range(N)]
blocks = [[l for l in range(M) if C[a][l]] for a in range(N)]

def search(node_cap, time_cap, first_row=None, verbose=True):
    S = [[0] * N for _ in range(N)]          # s[r][c]; only c>r assigned during search
    stats = {"nodes": 0, "rows_completed_max": 0, "row_complete_events": [0] * N, "cap": None}
    t0 = time.time()
    sol = None

    def fill_row(r):
        nonlocal sol
        if r == N:
            sol = [row[:] for row in S]; return True
        cols = list(range(r + 1, N))
        # fixed part from j<r
        w = sum(abs(S[r][j]) for j in range(r))
        b = [sum(S[r][j] * C[j][l] for j in range(r)) for l in range(M)]
        dot = [sum(S[r][j] * S[rp][j] for j in range(r)) for rp in range(r)]
        tgt = [-S[rp][r] - G[r][rp] for rp in range(r)]
        # remaining capacities as suffix counts
        nc = len(cols)
        remb = [[0] * (nc + 1) for _ in range(M)]
        remd = [[0] * (nc + 1) for _ in range(r)]
        for p in range(nc - 1, -1, -1):
            c = cols[p]
            for l in range(M): remb[l][p] = remb[l][p + 1] + (1 if C[c][l] else 0)
            for rp in range(r): remd[rp][p] = remd[rp][p + 1] + (1 if S[rp][c] else 0)
        def rec(p, w):
            stats["nodes"] += 1
            if stats["nodes"] > node_cap or (stats["nodes"] & 0xFFFF) == 0 and time.time() - t0 > time_cap:
                stats["cap"] = "hit"; return "cap"
            R = nc - p
            if w > 10 or w + R < 10: return False
            for l in range(M):
                if abs(b[l]) > remb[l][p]: return False
            for rp in range(r):
                if abs(dot[rp] - tgt[rp]) > remd[rp][p]: return False
            if p == nc:
                if w != 10: return False
                for l in range(M):
                    if b[l]: return False
                for rp in range(r):
                    if dot[rp] != tgt[rp]: return False
                stats["row_complete_events"][r] += 1
                if r + 1 > stats["rows_completed_max"]:
                    stats["rows_completed_max"] = r + 1
                    if verbose: print("  rows completed:", r + 1, "nodes", stats["nodes"], "t=%.1fs" % (time.time() - t0), flush=True)
                res = fill_row(r + 1)
                return res
            c = cols[p]
            vals = (0, 1, -1) if not (first_row and r == 0) else (first_row[c],)
            for v in vals:
                S[r][c] = v; S[c][r] = v
                if v:
                    for l in blocks[c]: b[l] += v * C[c][l]
                    for rp in range(r): dot[rp] += v * S[rp][c]
                res = rec(p + 1, w + abs(v))
                if v:
                    for l in blocks[c]: b[l] -= v * C[c][l]
                    for rp in range(r): dot[rp] -= v * S[rp][c]
                S[r][c] = 0; S[c][r] = 0
                if res: return res
            return False
        return rec(0, w)
    res = fill_row(0)
    stats["time"] = time.time() - t0; stats["result"] = ("SOLUTION" if sol else ("CAP" if res == "cap" else "EXHAUSTED_NO_SOLUTION"))
    return sol, stats

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--nodes", type=int, default=2_000_000); ap.add_argument("--time", type=float, default=600)
    ap.add_argument("--first-row", type=str, default=None, help="JSON list of 42 ints for row 0")
    a = ap.parse_args()
    fr = json.loads(a.first_row) if a.first_row else None
    sol, st = search(a.nodes, a.time, fr)
    print(json.dumps({k: v for k, v in st.items()}, indent=0))
    if sol:
        import numpy as np
        Sm = np.array(sol); Cm = np.array(C); ok = np.array_equal(Sm @ Sm + Sm, 12 * np.eye(N, dtype=int) - Cm @ Cm.T) and np.all(Cm.T @ Sm == 0)
        print("VERIFY S_out^2+S_out = 12I - CC^T and C^T S_out = 0:", ok)
        np.savetxt("sout_solution.txt", Sm, fmt="%d")
