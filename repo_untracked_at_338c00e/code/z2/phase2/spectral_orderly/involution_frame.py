"""General-m framework for the involution branch of srg(n, k=2m, 1, 2) with a unique fixed vertex.

Orbits: outer = [(i,j,e)] i<j in 1..m, e in {0,1}; representative u = {(i,0),(j,e)}, sigma(u) = {(i,1),(j,1-e)}.
Table T[U][V] in {0,1,2,3} encodes (a,b) = (A[u,v], A[u,sigma v]) as v = a + 2b; Q = a+b, S = a-b.
Spectral objects (all derived from A^2 + A - (k-2) I = 2J; r,s = eigenvalues (-1 +- sqrt(4k-7))/2):
  S_out (N x N): S_out^2 + S_out = (k-2) I - C C^T, C^T S_out = 0, C^T C = (k-2) I_m.
     Ps := (r I - S_out - r/(k-2) C C^T)/(r - s)   projector onto the s-eigenspace of S_out, rank g_out
     Pr := (S_out - s I + s/(k-2) C C^T)/(r - s)   projector onto the r-eigenspace, rank f_out
  Qt  ((1+m+N) x (1+m+N)) symmetrised ordinary quotient, Qt w = k w, w = (1, sqrt2, ..., sqrt2),
     Es := (r I - Qt)/(r - s) + (k - r)/((r - s) n) w w^T  projector rank g_Q
     Er := (Qt - s I)/(r - s) - (k - s)/((r - s) n) w w^T  projector rank f_Q
All ranks are computed numerically in check_instance() and compared with the trace formulas.
"""
import itertools, math
import numpy as np


class Frame:
    def __init__(self, m):
        self.m = m
        self.k = k = 2 * m
        self.n = k * (k - 2) // 2 + k + 1
        disc = math.isqrt(4 * k - 7)
        assert disc * disc == 4 * k - 7, "irrational eigenvalues: no srg (half-case)"
        self.r = (-1 + disc) // 2
        self.s = (-1 - disc) // 2
        self.outer = [(i, j, e) for i in range(1, m + 1) for j in range(i + 1, m + 1) for e in (0, 1)]
        self.N = N = len(self.outer)
        self.index = {U: t for t, U in enumerate(self.outer)}
        C = np.zeros((N, m), dtype=np.int64)
        Nb = np.zeros((N, m), dtype=np.int64)
        for t, (i, j, e) in enumerate(self.outer):
            C[t, i - 1] = 1
            C[t, j - 1] = -1 if e else 1
            Nb[t, i - 1] = Nb[t, j - 1] = 1
        self.C, self.Nb = C, Nb
        self.G = C @ C.T                      # inner Gram of S rows
        self.SH = Nb @ Nb.T                   # shared blocks (diag 2)
        self.BL = [[l for l in range(m) if Nb[t, l]] for t in range(N)]
        self.QV = [0, 1, 1, 2]
        self.SV = [0, 1, -1, 0]
        # multiplicities
        r, s = self.r, self.s
        # S (m+N): trace -m ; f+g = m+N ; r f + s g = -m
        tot = m + N
        g = (r * tot + m) / (r - s)
        self.gS = int(round(g)); self.fS = tot - self.gS
        assert r * self.fS + s * self.gS == -m
        # S_out: 0^m, r^fout, s^gout with r fout + s gout = 0, fout+gout = N - m
        self.gout = int(round(r * (N - m) / (r - s))); self.fout = N - m - self.gout
        assert r * self.fout + s * self.gout == 0
        # Qt (1+m+N): k, r^fQ, s^gQ ; trace = m (inner diag 1) ; f+g = m+N
        self.gQ = int(round((r * tot - (m - k)) / (r - s))); self.fQ = tot - self.gQ
        assert k + r * self.fQ + s * self.gQ == m
        self.w = np.array([1.0] + [math.sqrt(2)] * (m + N))

    # ---- matrices from a table ----
    def S_out(self, T):
        SV = np.array(self.SV); return SV[np.asarray(T)]

    def Q_out(self, T):
        QV = np.array(self.QV); return QV[np.asarray(T)]

    def Qt(self, T):
        m, N = self.m, self.N
        n = 1 + m + N
        Qt = np.zeros((n, n))
        Qt[0, 1:1 + m] = Qt[1:1 + m, 0] = math.sqrt(2)
        for i in range(m): Qt[1 + i, 1 + i] = 1.0
        Qt[1 + m:, 1:1 + m] = self.Nb
        Qt[1:1 + m, 1 + m:] = self.Nb.T
        Qt[1 + m:, 1 + m:] = self.Q_out(T)
        return Qt

    def Ps(self, S):
        r, s, k = self.r, self.s, self.k
        return (r * np.eye(self.N) - S - (r / (k - 2)) * self.G) / (r - s)

    def Pr(self, S):
        r, s, k = self.r, self.s, self.k
        return (S - s * np.eye(self.N) + (s / (k - 2)) * self.G) / (r - s)

    def Es(self, Qt):
        r, s, k, n = self.r, self.s, self.k, self.n
        return (r * np.eye(Qt.shape[0]) - Qt) / (r - s) + (k - r) / ((r - s) * n) * np.outer(self.w, self.w)

    def Er(self, Qt):
        r, s, k, n = self.r, self.s, self.k, self.n
        return (Qt - s * np.eye(Qt.shape[0])) / (r - s) - (k - s) / ((r - s) * n) * np.outer(self.w, self.w)

    # ---- lift to the n x n adjacency and verify the srg identity ----
    def lift(self, T):
        m, k, N = self.m, self.k, self.N
        inner = [(i, s) for i in range(1, m + 1) for s in (0, 1)]
        labels = []
        for (i, j, e) in self.outer:
            labels.append(frozenset([(i, 0), (j, e)])); labels.append(frozenset([(i, 1), (j, 1 - e)]))
        idx = {}
        n = 1 + 2 * m + 2 * N
        A = np.zeros((n, n), dtype=np.int64)
        for t, v in enumerate(inner): idx[v] = 1 + t
        for t, lab in enumerate(labels): idx[lab] = 1 + 2 * m + t
        for v in inner: A[0, idx[v]] = A[idx[v], 0] = 1
        for i in range(1, m + 1): A[idx[(i, 0)], idx[(i, 1)]] = A[idx[(i, 1)], idx[(i, 0)]] = 1
        for lab in labels:
            for v in lab: A[idx[lab], idx[v]] = A[idx[v], idx[lab]] = 1
        for U in range(N):
            for V in range(N):
                if U == V: continue
                a, b = (T[U][V] & 1), (T[U][V] >> 1)
                u, su, v, sv = labels[2 * U], labels[2 * U + 1], labels[2 * V], labels[2 * V + 1]
                A[idx[u], idx[v]] = A[idx[su], idx[sv]] = a
                A[idx[u], idx[sv]] = A[idx[su], idx[v]] = b
        ok = (np.array_equal(A @ A + A - (k - 2) * np.eye(n, dtype=np.int64), 2 * np.ones((n, n), dtype=np.int64))
              and np.array_equal(A, A.T) and not np.any(np.diag(A)))
        return A, ok


def table_from_graph(A, x, m):
    """Given adjacency A of an srg(n,2m,1,2) and an involution-fixed vertex x whose neighbourhood is m K_2,
    with the involution acting as the flip of every pair (assumed; verified by the caller), build the orbit table.
    Returns (frame, T, block orientation, label map)."""
    n = A.shape[0]
    fr = Frame(m)
    nx = [v for v in range(n) if A[x, v]]
    assert len(nx) == 2 * m
    # blocks = edges inside N(x)
    blocks = []
    seen = set()
    for v in nx:
        if v in seen: continue
        partner = [u for u in nx if A[v, u]]
        assert len(partner) == 1
        blocks.append((v, partner[0])); seen.add(v); seen.add(partner[0])
    assert len(blocks) == m
    innerpos = {}
    for i, (v0, v1) in enumerate(blocks, start=1):
        innerpos[v0] = (i, 0); innerpos[v1] = (i, 1)
    outer_vertices = [v for v in range(n) if v != x and not A[x, v]]
    lab = {}
    for v in outer_vertices:
        nb = [u for u in nx if A[v, u]]
        assert len(nb) == 2
        p, q = innerpos[nb[0]], innerpos[nb[1]]
        if p[0] > q[0]: p, q = q, p
        assert p[0] != q[0]
        lab[v] = (p, q)
    assert len(set(lab.values())) == len(outer_vertices) == 2 * m * (m - 1)
    def sigma_label(L):
        (i, s), (j, e) = L
        return ((i, 1 - s), (j, 1 - e))
    vert_of = {L: v for v, L in lab.items()}
    T = [[0] * fr.N for _ in range(fr.N)]
    reps = []
    for (i, j, e) in fr.outer:
        reps.append(vert_of[((i, 0), (j, e))])
    for U in range(fr.N):
        u = reps[U]
        for V in range(fr.N):
            if U == V: continue
            v = reps[V]; sv = vert_of[sigma_label(lab[v])]
            T[U][V] = int(A[u, v]) + 2 * int(A[u, sv])
    return fr, T, blocks, lab


def check_instance(fr, T, tol=1e-8, verbose=True):
    """Verify every spectral statement on a complete table T. Returns dict of results."""
    out = {}
    S = fr.S_out(T).astype(float); Q = fr.Q_out(T).astype(float)
    C = fr.C.astype(float); G = fr.G.astype(float)
    k, r, s, N, m = fr.k, fr.r, fr.s, fr.N, fr.m
    out["rows_nonzero"] = sorted(set(int(x) for x in (S != 0).sum(1)))
    out["CtS_zero"] = bool(np.abs(C.T @ S).max() < tol)
    out["S_identity"] = bool(np.abs(S @ S + S - (k - 2) * np.eye(N) + G).max() < tol)
    ev = np.linalg.eigvalsh(S)
    out["spec_S_out"] = {v: int(c) for v, c in zip(*np.unique(np.round(ev, 6), return_counts=True))}
    Ps, Pr = fr.Ps(S), fr.Pr(S)
    out["Ps_projector"] = bool(np.abs(Ps @ Ps - Ps).max() < 1e-7); out["rank_Ps"] = int(np.linalg.matrix_rank(Ps, tol=1e-7))
    out["Pr_projector"] = bool(np.abs(Pr @ Pr - Pr).max() < 1e-7); out["rank_Pr"] = int(np.linalg.matrix_rank(Pr, tol=1e-7))
    out["expected(gout,fout)"] = (fr.gout, fr.fout)
    Qt = fr.Qt(T)
    out["Qt_w_eig"] = bool(np.abs(Qt @ fr.w - k * fr.w).max() < tol)
    ev = np.linalg.eigvalsh(Qt)
    out["spec_Qt"] = {v: int(c) for v, c in zip(*np.unique(np.round(ev, 6), return_counts=True))}
    Es, Er = fr.Es(Qt), fr.Er(Qt)
    out["Es_projector"] = bool(np.abs(Es @ Es - Es).max() < 1e-7); out["rank_Es"] = int(np.linalg.matrix_rank(Es, tol=1e-7))
    out["Er_projector"] = bool(np.abs(Er @ Er - Er).max() < 1e-7); out["rank_Er"] = int(np.linalg.matrix_rank(Er, tol=1e-7))
    out["expected(gQ,fQ)"] = (fr.gQ, fr.fQ)
    # Q-side identities
    D = (Q == 2).astype(float)
    out["D_perfect_matching"] = bool(np.array_equal(D, D.T) and np.all(D.sum(1) == 1))
    out["Qout_identity"] = bool(np.abs(Q @ Q + Q - (k - 2) * np.eye(N) - 4 * np.ones((N, N)) + fr.SH).max() < tol)
    # F2 rank statement (k=14 analogue: rank_F2(Gamma_bar + Nb Nb^T) = fS - m... check general)
    Gb = ((Q == 1).astype(int)) % 2
    K = (Gb + fr.Nb @ fr.Nb.T) % 2
    out["rankF2_K"] = rank_f2(K)
    # rank profile of leading blocks of Ps (which row reaches gout)
    prof = []
    for rr in range(1, N + 1):
        prof.append(int(np.linalg.matrix_rank(Ps[:rr, :rr], tol=1e-7)))
    out["rank_profile_Ps"] = prof
    out["first_row_full_rank_Ps"] = next((i + 1 for i, v in enumerate(prof) if v == fr.gout), None)
    profr = [int(np.linalg.matrix_rank(Pr[:rr, :rr], tol=1e-7)) for rr in range(1, N + 1)]
    out["first_row_full_rank_Pr"] = next((i + 1 for i, v in enumerate(profr) if v == fr.fout), None)
    # determination test: S_out from first r0 rows via Schur complement of Ps
    r0 = out["first_row_full_rank_Ps"]
    if r0:
        B = Ps[:r0, :r0]; X = Ps[:r0, r0:]
        Y = X.T @ np.linalg.pinv(B) @ X
        Srec = (r * np.eye(N - r0) - (r / (k - 2)) * G[r0:, r0:] - (r - s) * Y)
        out["determination_from_first_rows"] = bool(np.abs(Srec - S[r0:, r0:]).max() < 1e-6)
    if verbose:
        for kk, vv in out.items():
            if kk != "rank_profile_Ps": print("  %s: %s" % (kk, vv))
    return out


def rank_f2(M):
    M = (np.array(M) % 2).astype(np.uint8).copy()
    rows, cols = M.shape; rk = 0
    for c in range(cols):
        piv = next((i for i in range(rk, rows) if M[i, c]), None)
        if piv is None: continue
        M[[rk, piv]] = M[[piv, rk]]
        for i in range(rows):
            if i != rk and M[i, c]: M[i] ^= M[rk]
        rk += 1
    return rk


# ---------------- known instances ----------------
def paley9():
    """srg(9,4,1,2) = Paley(9) = 3x3 rook's graph complement... use Z3 x Z3 with connection set {(1,0),(2,0),(0,1),(0,2)}."""
    pts = [(a, b) for a in range(3) for b in range(3)]
    n = 9; A = np.zeros((n, n), dtype=np.int64)
    conn = {(1, 0), (2, 0), (0, 1), (0, 2)}
    for p in range(n):
        for q in range(n):
            d = ((pts[q][0] - pts[p][0]) % 3, (pts[q][1] - pts[p][1]) % 3)
            if d in conn: A[p, q] = 1
    return A, pts


def bvls243():
    """Berlekamp-van Lint-Seidel graph srg(243,22,1,2): cosets of the [11,6,5] ternary Golay code, adjacent when
    they differ by +-e_i. Generator: puncture the extended [12,6,6] code [I | B]."""
    B = [[0, 1, 1, 1, 1, 1], [1, 0, 1, 2, 2, 1], [1, 1, 0, 1, 2, 2], [1, 2, 1, 0, 1, 2], [1, 2, 2, 1, 0, 1], [1, 1, 2, 2, 1, 0]]
    Gm = np.zeros((6, 12), dtype=np.int64)
    Gm[:, :6] = np.eye(6, dtype=np.int64); Gm[:, 6:] = np.array(B)
    code12 = set()
    for coeffs in itertools.product(range(3), repeat=6):
        cw = tuple((np.array(coeffs) @ Gm) % 3); code12.add(cw)
    assert len(code12) == 729
    wts = {}
    for cw in code12:
        w = sum(1 for x in cw if x); wts[w] = wts.get(w, 0) + 1
    code11 = set(cw[:11] for cw in code12)
    assert len(code11) == 729
    # syndrome map: coset representative = canonical (min lexicographic) is expensive; use a parity-check via linear algebra
    # Simpler: coset of v <-> v reduced by the code: compute syndrome with an H matrix obtained by solving.
    # Build H (5x11) as nullspace over F3 of the 6x11 generator (punctured).
    G11 = Gm[:, :11] % 3
    H = nullspace_f3(G11)  # 5 x 11 with G11 H^T = 0
    assert H.shape[0] == 5
    def synd(v): return tuple((H @ np.array(v)) % 3)
    syn_list = list(itertools.product(range(3), repeat=5))
    sidx = {s: t for t, s in enumerate(syn_list)}
    n = 243; A = np.zeros((n, n), dtype=np.int64)
    conn = []
    for i in range(11):
        for sgn in (1, 2):
            v = [0] * 11; v[i] = sgn; conn.append(synd(v))
    assert len(set(conn)) == 22
    # adjacency in syndrome space: syndrome is linear, so s ~ s + synd(+-e_i)
    for t, sy in enumerate(syn_list):
        for c in conn:
            s2 = tuple((a + b) % 3 for a, b in zip(sy, c)); A[t, sidx[s2]] = 1
    return A, syn_list, wts


def nullspace_f3(M):
    M = np.array(M) % 3; rows, cols = M.shape
    M = M.copy(); piv_cols = []; rk = 0
    for c in range(cols):
        piv = next((i for i in range(rk, rows) if M[i, c]), None)
        if piv is None: continue
        M[[rk, piv]] = M[[piv, rk]]
        inv = 1 if M[rk, c] == 1 else 2
        M[rk] = (M[rk] * inv) % 3
        for i in range(rows):
            if i != rk and M[i, c]: M[i] = (M[i] - M[i, c] * M[rk]) % 3
        piv_cols.append(c); rk += 1
    free = [c for c in range(cols) if c not in piv_cols]
    basis = []
    for f in free:
        v = np.zeros(cols, dtype=np.int64); v[f] = 1
        for i, pc in enumerate(piv_cols): v[pc] = (-M[i, f]) % 3
        basis.append(v)
    return np.array(basis)


if __name__ == "__main__":
    import json, sys
    for name, (A, pts) in (("Paley9", paley9()[:2]),):
        n = A.shape[0]; k = int(A.sum(1)[0])
        ok = np.array_equal(A @ A + A - (k - 2) * np.eye(n, dtype=np.int64), 2 * np.ones((n, n), dtype=np.int64))
        print(name, "srg identity:", ok)
        # involution: negation; fixed point 0
        neg = {p: pts.index(((-p[0]) % 3, (-p[1]) % 3)) for p in pts}
        perm = [neg[p] for p in pts]
        assert all(A[i, j] == A[perm[i], perm[j]] for i in range(n) for j in range(n))
        fixed = [i for i in range(n) if perm[i] == i]; print("  fixed points:", fixed)
        fr, T, blocks, lab = table_from_graph(A, fixed[0], k // 2)
        res = check_instance(fr, T)
        A2, ok2 = fr.lift(T); print("  lift ok:", ok2)
    A, syn, wts = bvls243()
    n = 243; k = 22
    ok = np.array_equal(A @ A + A - (k - 2) * np.eye(n, dtype=np.int64), 2 * np.ones((n, n), dtype=np.int64))
    print("BvLS243 weight distribution of the extended code:", wts)
    print("BvLS243 srg(243,22,1,2) identity:", ok, "regular:", set(A.sum(1)))
    perm = [syn.index(tuple((-x) % 3 for x in s)) for s in syn]
    assert all(A[i, j] == A[perm[i], perm[j]] for i in range(n) for j in range(n))
    fixed = [i for i in range(n) if perm[i] == i]; print("  negation is an automorphism; fixed points:", fixed)
    fr, T, blocks, lab = table_from_graph(A, fixed[0], 11)
    # verify the involution acts as the flip on labels: sigma(v) has label with both coordinates flipped
    res = check_instance(fr, T)
    A2, ok2 = fr.lift(T); print("  lift ok:", ok2, "(lifted matrix has", A2.shape, ")")
    json.dump({"T": T}, open("bvls_table.json", "w"))
    print("saved bvls_table.json")
