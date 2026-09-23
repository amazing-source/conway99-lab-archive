"""Joint row-by-row DFS for the involution case of Conway-99 (unique fixed vertex x, involution = flip of
every matched pair). Unknown: the outer graph H on 84 labels, sigma-invariant. Search over the 42 sigma-orbits
U of outer labels; for an unordered orbit pair {U,V} the symmetric entry is the pair (a,b)=(A[u,v],A[u,sv])
encoded v in {0:(0,0),1:(1,0),2:(0,1),3:(1,1)}; Q=a+b, S=a-b.
Exact necessary constraints used (all derived from A^2+A-12I=2J with the forced inner structure):
  Q-row: sum_V Q[U,V] = 12 and exactly one V with Q=2 (u ~ v and u ~ sv), u !~ su.
  Q-block: for block l: sum_{V on l} Q[U,V] = 2 if l in blocks(U) else 4.
  S-block: for block l: sum_V S[U,V]*c_l(V) = 0.
  Q-Gram (U!=V): sum_W Q[U,W]Q[V,W] = 4 - Q[U,V] - Sh[U,V]   (Sh = number of shared blocks).
  S-Gram (U!=V): sum_W S[U,W]S[V,W] = -S[U,V] - G[U,V]        (G = C C^T).
A completed 42x42 table is then lifted to the 99x99 matrix and verified with the integer identity.
"""
import argparse, json, sys, time
import numpy as np

M = 7
outer = [(i, j, e) for i in range(1, M + 1) for j in range(i + 1, M + 1) for e in (0, 1)]
N = len(outer)
def csign(V, l):
    i, j, e = V
    return 1 if l == i else ((-1 if e else 1) if l == j else 0)
C = [[csign(V, l) for l in range(1, M + 1)] for V in outer]
BL = [[l for l in range(M) if C[a][l]] for a in range(N)]
G = [[sum(C[a][l] * C[b][l] for l in range(M)) for b in range(N)] for a in range(N)]
SH = [[len(set(BL[a]) & set(BL[b])) for b in range(N)] for a in range(N)]
QV = [0, 1, 1, 2]; SV = [0, 1, -1, 0]

def lift(T):
    """Build the 99x99 adjacency from the orbit table T (values 0..3) and check the srg identity."""
    inner = [(i, s) for i in range(1, M + 1) for s in (0, 1)]
    labels = []
    for (i, j, e) in outer:
        labels.append(frozenset([(i, 0), (j, e)])); labels.append(frozenset([(i, 1), (j, 1 - e)]))  # rep, sigma(rep)
    idx = {}
    n = 1 + 2 * M + 2 * N
    A = np.zeros((n, n), dtype=np.int64)
    for k, v in enumerate(inner): idx[v] = 1 + k
    for k, lab in enumerate(labels): idx[lab] = 1 + 2 * M + k
    for v in inner: A[0, idx[v]] = A[idx[v], 0] = 1
    for i in range(1, M + 1): A[idx[(i, 0)], idx[(i, 1)]] = A[idx[(i, 1)], idx[(i, 0)]] = 1
    for lab in labels:
        for v in lab: A[idx[lab], idx[v]] = A[idx[v], idx[lab]] = 1
    for U in range(N):
        for V in range(N):
            if U == V: continue
            a, b = (T[U][V] & 1), (T[U][V] >> 1)
            u, su, v, sv = labels[2 * U], labels[2 * U + 1], labels[2 * V], labels[2 * V + 1]
            A[idx[u], idx[v]] = A[idx[su], idx[sv]] = a
            A[idx[u], idx[sv]] = A[idx[su], idx[v]] = b
    ok = np.array_equal(A @ A + A - 12 * np.eye(n, dtype=np.int64), 2 * np.ones((n, n), dtype=np.int64)) and np.array_equal(A, A.T) and not np.any(np.diag(A))
    return A, ok

def search(node_cap, time_cap, verbose=True):
    T = [[0] * N for _ in range(N)]
    st = {"nodes": 0, "rows_max": 0, "row_events": [0] * (N + 1)}
    t0 = time.time(); sol = [None]
    def fill_row(r):
        if r == N:
            sol[0] = [row[:] for row in T]; return True
        cols = list(range(r + 1, N)); nc = len(cols)
        # fixed contributions from j<r
        qs = sum(QV[T[r][j]] for j in range(r)); two = sum(1 for j in range(r) if T[r][j] == 3)
        qb = [sum(QV[T[r][j]] for j in range(r) if C[j][l]) for l in range(M)]
        sb = [sum(SV[T[r][j]] * C[j][l] for j in range(r)) for l in range(M)]
        qd = [sum(QV[T[r][j]] * QV[T[rp][j]] for j in range(r)) for rp in range(r)]
        sd = [sum(SV[T[r][j]] * SV[T[rp][j]] for j in range(r)) for rp in range(r)]
        qt = [4 - QV[T[r][rp]] - SH[r][rp] for rp in range(r)]
        stt = [-SV[T[r][rp]] - G[r][rp] for rp in range(r)]
        qbt = [2 if l in BL[r] else 4 for l in range(M)]
        # suffix capacities
        remb = [[0] * (nc + 1) for _ in range(M)]
        remq = [[0] * (nc + 1) for _ in range(r)]   # remaining columns where row rp has Q>0 (weight by Q)
        for p in range(nc - 1, -1, -1):
            c = cols[p]
            for l in range(M): remb[l][p] = remb[l][p + 1] + (1 if C[c][l] else 0)
            for rp in range(r): remq[rp][p] = remq[rp][p + 1] + QV[T[rp][c]]
        def rec(p, qs, two):
            st["nodes"] += 1
            if st["nodes"] > node_cap or ((st["nodes"] & 0xFFFF) == 0 and time.time() - t0 > time_cap): return "cap"
            R = nc - p
            if qs > 12 or two > 1 or qs + 2 * R < 12: return False
            for l in range(M):
                if qb[l] > qbt[l] or qb[l] + 2 * remb[l][p] < qbt[l]: return False
                if abs(sb[l]) > remb[l][p]: return False
            for rp in range(r):
                if qd[rp] > qt[rp] or qd[rp] + 2 * remq[rp][p] < qt[rp]: return False
                if abs(sd[rp] - stt[rp]) > remq[rp][p]: return False
            if p == nc:
                if qs != 12 or two != 1: return False
                for l in range(M):
                    if qb[l] != qbt[l] or sb[l] != 0: return False
                for rp in range(r):
                    if qd[rp] != qt[rp] or sd[rp] != stt[rp]: return False
                # forward check on future rows (partial feasibility from fixed entries)
                for f in range(r + 1, N):
                    fq = sum(QV[T[f][j]] for j in range(r + 1)); ftwo = sum(1 for j in range(r + 1) if T[f][j] == 3)
                    if fq > 12 or ftwo > 1: return False
                    free = N - 1 - (r + 1)
                    for l in range(M):
                        tq = 2 if l in BL[f] else 4
                        pq = sum(QV[T[f][j]] for j in range(r + 1) if C[j][l]); ps = sum(SV[T[f][j]] * C[j][l] for j in range(r + 1))
                        capl = sum(1 for j in range(r + 1, N) if j != f and C[j][l])
                        if pq > tq or pq + 2 * capl < tq or abs(ps) > capl: return False
                st["row_events"][r + 1] += 1
                if r + 1 > st["rows_max"]:
                    st["rows_max"] = r + 1
                    if verbose: print("  rows completed: %d  nodes %d  t=%.1fs" % (r + 1, st["nodes"], time.time() - t0), flush=True)
                return fill_row(r + 1)
            c = cols[p]
            for v in (0, 1, 2, 3):
                q, s = QV[v], SV[v]
                T[r][c] = v; T[c][r] = v
                if q:
                    for l in BL[c]: qb[l] += q; sb[l] += s * C[c][l]
                    for rp in range(r): qd[rp] += q * QV[T[rp][c]]; sd[rp] += s * SV[T[rp][c]]
                res = rec(p + 1, qs + q, two + (v == 3))
                if q:
                    for l in BL[c]: qb[l] -= q; sb[l] -= s * C[c][l]
                    for rp in range(r): qd[rp] -= q * QV[T[rp][c]]; sd[rp] -= s * SV[T[rp][c]]
                T[r][c] = 0; T[c][r] = 0
                if res: return res
            return False
        return rec(0, qs, two)
    res = fill_row(0)
    st["time"] = time.time() - t0
    st["result"] = "SOLUTION" if sol[0] else ("CAP" if res == "cap" else "EXHAUSTED_NO_SOLUTION")
    return sol[0], st

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--nodes", type=int, default=5_000_000); ap.add_argument("--time", type=float, default=600)
    a = ap.parse_args()
    sol, st = search(a.nodes, a.time)
    print(json.dumps(st))
    if sol:
        A, ok = lift(sol); print("LIFT VERIFY srg(99,14,1,2):", ok)
        np.savetxt("involution_adjacency.txt", A, fmt="%d"); json.dump(sol, open("involution_orbit_table.json", "w"))
