"""Independent cross-check (sympy/numpy) of the six-motif kernel screen: PSD counts, integer-kernel saturation, phase-equation ranks."""
import json, itertools
import numpy as np, sympy as sp
cases = json.load(open("cases.json", encoding="utf-8"))["cases"]
PAIRS = list(itertools.combinations(range(6), 2))
def F_of(mask):
    F = np.zeros((6, 6), dtype=int)
    for k, (i, j) in enumerate(PAIRS):
        if mask >> k & 1: F[i, j] = F[j, i] = 1
    return F
def moment_direct(F, E):
    P = np.zeros((18, 18), dtype=int)
    for i in range(6):
        for a in range(3):
            for b in range(3):
                if a != b: P[3*i+a, 3*i+b] = 1
    for i, j in PAIRS:
        if F[i, j]:
            for a in range(3):
                P[3*i+a, 3*j+(a+E[i, j]) % 3] = P[3*j+(a+E[i, j]) % 3, 3*i+a] = 1
    R = 12*np.eye(18, dtype=int) + 2 - P@P - P
    return np.array([[sum(a*R[3*i, 3*j+a] for a in range(3)) % 3 for j in range(6)] for i in range(6)])
def integer_kernel_basis(G):
    M = sp.Matrix(G.tolist()); ns = M.nullspace()
    if not ns: return []
    # clear denominators, then saturate via Smith normal form of the basis matrix
    B = sp.Matrix.hstack(*[v * sp.lcm([x.q for x in v]) for v in ns])
    B = B.applyfunc(lambda x: sp.Integer(x))
    from sympy.matrices.normalforms import smith_normal_form
    S = smith_normal_form(B, domain=sp.ZZ)
    d = [abs(S[i, i]) for i in range(min(S.shape))]
    assert all(x == 1 for x in d), ("kernel basis not saturated", d)   # invariant factors all 1 <=> saturated
    return [list(map(int, B[:, k])) for k in range(B.shape[1])]
counts = {"neg": 0, "notpsd": 0, "psd": 0}; nullities = {}; nontrivial = []
for c in cases:
    F = F_of(c["mask"]); G = 6*np.eye(6, dtype=int) + 6 - 5*F - F@F
    if (G < 0).any(): counts["neg"] += 1; continue
    ev = np.linalg.eigvalsh(G.astype(float))
    if ev.min() < -1e-9: counts["notpsd"] += 1; continue
    counts["psd"] += 1
    K = integer_kernel_basis(G); nullities[len(K)] = nullities.get(len(K), 0) + 1
    edges = [(i, j) for i, j in PAIRS if F[i, j]]
    eqs = []
    for a, b in itertools.combinations(K, 2):
        row = []
        for (i, j) in edges:
            E = np.zeros((6, 6), dtype=int); E[i, j], E[j, i] = 1, -1
            D = moment_direct(F, E); row.append(int(np.array(a) @ D @ np.array(b)) % 3)
        eqs.append(row)
    r = sp.Matrix(eqs).rank(iszerofunc=lambda x: x % 3 == 0) if eqs else 0
    # rank over F3 properly:
    if eqs:
        Mm = sp.Matrix(eqs).applyfunc(lambda x: x % 3); r = 0
        from sympy import GF
        from sympy.polys.matrices import DomainMatrix
        r = DomainMatrix.from_Matrix(Mm).convert_to(GF(3)).rank()
    if r: nontrivial.append((c["mask"], edges, r))
print("counts:", counts, "| nullities among PSD:", dict(sorted(nullities.items())))
print("nontrivial (mask, edges, rank_F3):", nontrivial)
