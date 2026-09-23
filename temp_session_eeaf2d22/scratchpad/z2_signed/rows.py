"""Enumerate all candidate orbit-rows for the reference outer orbit U0=(1,2,0):
vectors over the 42 outer orbits with entries v in {0,1,2,3} (Q=[0,1,1,2], S=[0,1,-1,0]) satisfying
  sum Q = 12, exactly one entry with Q=2, entry at U0 itself = 0,
  Q-block sums: 2 on blocks 1,2 and 4 on blocks 3..7,
  S-balance: sum_V S[V]*c_l(V) = 0 for every block l.
Saves rows as a uint8 numpy array (n_rows x 42) in rows_U0.npy and prints the count.
"""
import numpy as np, time
from joint_dfs import outer, N, C, BL, M, QV, SV
U0 = 0
t0 = time.time()
# enumerate Q-patterns first (degree-constrained), block by block using DFS over positions
target = [2 if l in BL[U0] else 4 for l in range(M)]
pos = [p for p in range(N) if p != U0]
rem = [[0] * (len(pos) + 1) for _ in range(M)]
for k in range(len(pos) - 1, -1, -1):
    for l in range(M): rem[l][k] = rem[l][k + 1] + (1 if C[pos[k]][l] else 0)
qpatterns = []
q = [0] * N; bs = [0] * M
def rec(k, tot, two):
    if tot > 12 or two > 1: return
    for l in range(M):
        if bs[l] > target[l] or bs[l] + 2 * rem[l][k] < target[l]: return
    if k == len(pos):
        if tot == 12 and two == 1 and all(bs[l] == target[l] for l in range(M)): qpatterns.append(q[:])
        return
    p = pos[k]
    for val in (0, 1, 2):
        q[p] = val
        for l in BL[p]: bs[l] += val
        rec(k + 1, tot + val, two + (val == 2))
        for l in BL[p]: bs[l] -= val
        q[p] = 0
rec(0, 0, 0)
print("Q-patterns:", len(qpatterns), "t=%.1fs" % (time.time() - t0), flush=True)
# now signs: for each Q-pattern, positions with Q=1 get S=+1 (v=1) or S=-1 (v=2); need per-block signed balance
rows = []
for qp in qpatterns:
    ones = [p for p in range(N) if qp[p] == 1]
    # per block l, the entries on block l with Q=1 must have signed sum 0 (weights c_l)
    # small DFS over the 10 sign choices with block partial sums
    v = [0] * N
    for p in range(N):
        if qp[p] == 2: v[p] = 3
    sb = [0] * M
    remc = [[0] * (len(ones) + 1) for _ in range(M)]
    for k in range(len(ones) - 1, -1, -1):
        for l in range(M): remc[l][k] = remc[l][k + 1] + (1 if C[ones[k]][l] else 0)
    def srec(k):
        for l in range(M):
            if abs(sb[l]) > remc[l][k]: return
        if k == len(ones):
            rows.append(bytes(v)); return
        p = ones[k]
        for s, code in ((1, 1), (-1, 2)):
            v[p] = code
            for l in BL[p]: sb[l] += s * C[p][l]
            srec(k + 1)
            for l in BL[p]: sb[l] -= s * C[p][l]
        v[p] = 0
    srec(0)
arr = np.frombuffer(b"".join(rows), dtype=np.uint8).reshape(-1, N)
np.save("rows_U0.npy", arr)
print("candidate rows for U0:", arr.shape[0], "t=%.1fs" % (time.time() - t0))
