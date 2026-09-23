"""Exact checks (sympy / integer numpy) supporting the method-transfer table.
 C1. Ishida rank equations for srg(99,14,1,2), p=2, Fix(t) = one vertex: both idempotents 2-integral,
     both principal 1x1 submatrices vanish mod 2, both equations give a_1(t) = 14 (nothing beyond a_1 = 14).
 C2. Ishida at p=3, Fix empty: a_1(x) = 18, hence tau = a_1/3 = 6 triangular orbits (C3 side note).
 C3. Ishida-type identities on T-invariant permutation modules of edges / triangles / quadrilaterals:
     the 2-integral idempotent built from E_{-4} restricted to the fixed objects is 0 mod 2 (trivial identity).
 C4. Control of the F2-rank mechanism on k=4 (srg(9,4,1,2), m=2): rank_F2(S mod 2) = multiplicity of eigenvalue 1.
 C5. Fourier/Z8 completion criterion for p=2: given the Q-identity, exactness <=> S^2+S-(k-2)I == 0 (mod 8).
"""
import sys, itertools
from fractions import Fraction as F
import numpy as np
import sympy as sp

sys.path.insert(0, r"C:\Users\RESEARCHER\Desktop\conway99-involution\code\z2")

v, k, lam, mu = 99, 14, 1, 2
r, s = 3, -4
# E_theta = alpha I + beta A + gamma J  (Ishida eq. (Ers)): E_theta = (A - theta' I - (k-theta')/v J)/(theta-theta')
def idem(theta, thetap):
    d = F(theta - thetap)
    return (F(-thetap) / d, F(1) / d, F(-(k - thetap), v) / d)   # alpha, beta, gamma
a3, b3, g3 = idem(3, -4); a4, b4, g4 = idem(-4, 3)
print("C1  E_3 =", (a3, b3, g3), " E_-4 =", (a4, b4, g4))
assert (a3, b3, g3) == (F(4, 7), F(1, 7), F(-2, 77)) and (a4, b4, g4) == (F(3, 7), F(-1, 7), F(1, 63))
for name, (al, be, ga) in (("E_3", (a3, b3, g3)), ("E_-4", (a4, b4, g4))):
    dens = [x.denominator for x in (al + ga, be + ga, ga)]
    print("    %s entry denominators (diag, adj, nonadj):" % name, dens, "-> 2-integral:", all(d % 2 for d in dens))
    assert all(d % 2 for d in dens)
# Fix = {x}: principal submatrix is the 1x1 matrix (alpha+gamma); rank mod 2 = 1 iff numerator odd
rho_r = 1 if (a3 + g3).numerator % 2 else 0
rho_s = 1 if (a4 + g4).numerator % 2 else 0
a1_from_r = (r - s) * rho_r + s * 1 + (k - s)
a1_from_s = r * 1 + (k - r) - (r - s) * rho_s
print("    diag entries: E_3[x,x] =", a3 + g3, " E_-4[x,x] =", a4 + g4, " ranks mod 2:", rho_r, rho_s,
      " -> a_1(t) =", a1_from_r, "and", a1_from_s)
assert a1_from_r == 14 and a1_from_s == 14

# C2: p = 3, Fix empty, E_3 3-integral (denominators 7, 77)
dens3 = [x.denominator for x in (a3 + g3, b3 + g3, g3)]
assert all(d % 3 for d in dens3)
a1_p3 = (r - s) * 0 + s * 0 + (k - s)
print("C2  p=3, Fix empty: E_3 3-integral", dens3, " a_1(x) =", a1_p3, " tau = a_1/3 =", F(a1_p3, 3))
assert a1_p3 == 18

# C3: incidence-module idempotents from E_{-4}.  Bx Bx^T for vertex/triangle: A + 7I (eigs 21,10,3);
# vertex/quadrilateral: 83I + 11A + J (eigs 336,116,39).  The -4 summand idempotent is B^T E_-4 B / c with c the
# eigenvalue of B B^T on the -4 eigenspace: c = 3 (triangles), 39 (quadrilaterals) -> 2-integral.
Ad = sp.Symbol('A')
for nm, c in (("triangles", 3), ("quadrilaterals", 39)):
    print("C3  %s: scalar %d is odd -> B^T E_-4 B / %d is 2-integral" % (nm, c, c)); assert c % 2
# fixed triangles tau_i = {x,(i,0),(i,1)}: entries of B^T E_-4 B /3
d, ad, na = a4 + g4, b4 + g4, g4          # diag, adjacent, non-adjacent entries of E_-4
same = (3 * d + 6 * ad) / 3
diff = (d + 4 * ad + 4 * na) / 3           # (x,x); x-(j,.) and (i,.)-x adjacent: 4 pairs; (i,.)-(j,.) non-adjacent: 4 pairs
print("    fixed-triangle block: same =", same, " different =", diff, " -> both 0 mod 2:", same.numerator % 2 == 0 and diff == 0)
assert same.numerator % 2 == 0 and diff == 0
# fixed quadrilaterals q = U u D(U): different quadrilaterals are vertex-disjoint; entry = ((16-e) na + e ad)/39 with e edges between
e = sp.Symbol('e')
expr = ((16 - e) * sp.Rational(na.numerator, na.denominator) + e * sp.Rational(ad.numerator, ad.denominator)) / 39
print("    fixed-quadrilateral off-diagonal entry as a function of the number e of edges between them:", sp.simplify(expr),
      " (numerator parity = parity of e; e = 2(Q_UU'+Q_UV'+Q_VU'+Q_VV') is always even)")

# C4: k=4 control via orbit_sat (m=2): lift, then build S on the (-1)-eigenspace basis e_u - e_{tu} and check rank_F2.
from orbit_sat import build, lift
from pysat.solvers import Solver
cnf, pool, outer, rep, trep, A_, B_ = build(2, "none")
with Solver(name="cadical195", bootstrap_with=cnf.clauses) as so:
    assert so.solve()
    M, ok = lift(2, outer, rep, trep, A_, B_, so.get_model())
assert ok
n = M.shape[0]; m = 2
# vertex order in lift(): 0 = x, 1..2m inner ((i,0),(i,1) consecutive), then rep/trep pairs
pairs = [(1 + 2 * i, 2 + 2 * i) for i in range(m)] + [(1 + 2 * m + 2 * U, 2 + 2 * m + 2 * U) for U in range(len(outer))]
Vm = np.zeros((n, len(pairs)), dtype=np.int64)
for c, (p, q) in enumerate(pairs): Vm[p, c] = 1; Vm[q, c] = -1
# A V = V S  (columns of V span the -1 eigenspace of t); solve S = (V^T V)^{-1} V^T A V = V^T A V / 2
S = (Vm.T @ M @ Vm) // 2
assert np.array_equal(M @ Vm, Vm @ S)
assert np.array_equal(S @ S + S, (4 - 2) * np.eye(len(pairs), dtype=np.int64))
ev = sorted(np.linalg.eigvals(S).real.round(6)); f = sum(1 for x in ev if abs(x - 1) < 1e-6)
rk2 = sp.Matrix(S % 2).rank(iszerofunc=lambda x: x % 2 == 0)
# proper F2 rank
def rank_f2(Mx):
    Mx = [list(map(int, row)) for row in (np.array(Mx) % 2)]; rows = len(Mx); cols = len(Mx[0]); rk = 0
    for c in range(cols):
        piv = next((i for i in range(rk, rows) if Mx[i][c]), None)
        if piv is None: continue
        Mx[rk], Mx[piv] = Mx[piv], Mx[rk]
        for i in range(rows):
            if i != rk and Mx[i][c]: Mx[i] = [(x + y) % 2 for x, y in zip(Mx[i], Mx[rk])]
        rk += 1
    return rk
rk2 = rank_f2(S)
print("C4  k=4 control: S =", S.tolist(), " spectrum", ev, " mult(1) =", f, " rank_F2(S mod 2) =", rk2)
assert rk2 == f

# C5: with c0 + c1 = 4 and c0,c1 >= 0, c0 - c1 in {-4,-2,0,2,4}; congruence mod 8 forces 0, mod 4 does not.
vals = sorted(set(c0 - (4 - c0) for c0 in range(5)))
print("C5  c0-c1 values:", vals, " those == 0 mod 8:", [x for x in vals if x % 8 == 0], " those == 0 mod 4:", [x for x in vals if x % 4 == 0])
assert [x for x in vals if x % 8 == 0] == [0] and len([x for x in vals if x % 4 == 0]) == 3
print("ALL CHECKS PASSED")
