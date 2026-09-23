"""Rebuild the wave-23 6->7 extension system at symbolic n3 (exact QQ arithmetic) and compare the
resulting affine family p + q*n3 + r*z (z = h11/4) with the corrected Reimbayev formulas."""
import sys, json
sys.path.insert(0, "../conway-99-research/attempts/wave23-weighted-extensions")
import model
from fractions import Fraction as F
from sympy.polys.matrices import DomainMatrix
from sympy import QQ

def dm(rows): return DomainMatrix([[QQ(int(x)) for x in r] for r in rows], (len(rows), len(rows[0])), QQ)
def nullspace(rows):
    ns = dm(rows).nullspace().to_Matrix()
    return [[F(int(x.p), int(x.q)) for x in ns.row(i)] for i in range(ns.rows)]
def solve(rows, rhs):
    # least-norm exact particular solution via rref of augmented matrix
    aug = DomainMatrix([[QQ(int(x)) for x in r] + [QQ(str(b))] for r, b in zip(rows, rhs)], (len(rows), len(rows[0]) + 1), QQ)
    R, piv = aug.rref()
    Rm = R.to_Matrix(); ncol = len(rows[0])
    assert ncol not in piv, "inconsistent system"
    x = [F(0)] * ncol
    for i, p in enumerate(piv):
        x[p] = F(int(Rm[i, ncol].p), int(Rm[i, ncol].q))
    return x

# 5->6: six-vector as affine function of n3
t5 = model.build_transition(5)
six_at_705 = dict(zip(model.SOURCE_N_MASKS, model.SIX_COUNTS))
six_cls = list(t5["upper_classes"]); six705 = [six_at_705[m] for m in six_cls]
ker5 = nullspace(t5["matrix_rows"]); assert len(ker5) == 1
n3col = six_cls.index(model.SOURCE_N_MASKS[2])
d6 = [v / ker5[0][n3col] for v in ker5[0]]          # direction with unit n3 coordinate
six = lambda n3: [F(a) + (n3 - 705) * d for a, d in zip(six705, d6)]
assert all(v.denominator == 1 for v in six(4158)), "six-vector not integral at 4158"

# 6->7 at n3 = 705 and n3 = 4158 (two points suffice: affine in n3)
t6 = model.build_transition(6); rows = t6["matrix_rows"]; cls7 = list(t6["upper_classes"])
ker6 = nullspace(rows); assert len(ker6) == 1
h11col = cls7.index(model.source_h_masks()[11])
zdir = [v / ker6[0][h11col] * 4 for v in ker6[0]]    # h11 = 4z -> per unit z
fam = {}
def family_at(n3):
    rhs = [int(r["rhs_multiplier"]) * six(n3)[int(r["lower_index"])] for r in t6["row_records"]]
    x = solve(rows, rhs)
    # shift particular solution so that the h11 coordinate equals 0 (then count = x + z*zdir with h11=4z)
    t = x[h11col] / zdir[h11col]
    return [xi - t * zi for xi, zi in zip(x, zdir)]
x705 = family_at(705); x4158 = family_at(4158)
p = [a - 705 * (b - a) / (4158 - 705) for a, b in zip(x705, x4158)]
q = [(b - a) / (4158 - 705) for a, b in zip(x705, x4158)]
r = zdir
# cross-check against the published wave-23 records at (705, z=353)
w23 = json.load(open("../conway-99-research/attempts/wave23-weighted-extensions/affine-witness.json"))
rec = {t["canonical_mask"]: (t["count_at_z_min"], t["delta_per_z"]) for t in w23["order_seven_affine_family"]["records"]}
ok = all(p[i] + q[i] * 705 + r[i] * 353 == rec[m][0] and r[i] == rec[m][1] for i, m in enumerate(cls7))
print("rebuilt family reproduces wave-23 records at n3=705:", ok)
# corrected Reimbayev at (99,14): from corrected.py logic
import sympy as sp
exec(open("parse_r7.py", encoding="utf-8").read().split("# ---- specialise")[0].replace("sys.argv[1]", "'../arxiv/r7/The_Subgraphs_of_Order_Seven.tex'"))
n, k, n3, z11 = sp.symbols("n k n3 z11")
Z[21]  = sp.expand(n*k*(k-2)*(k-4) - 2*n3 - z11/2)
Z[80]  = sp.expand(sp.Rational(1,2)*n*k*(k-2)*(k-4)*(2*k-17) + 16*n3 + sp.Rational(3,2)*z11); Z[84] = Z[80]
Z[176] = sp.expand(sp.Rational(1,8)*n*k*(k-2)*(k-4)*(k**4-24*k**3+236*k**2-1136*k+2264) + 6*(5*k-34)*n3 - 9*z11)
R = {}
for i, e in Z.items():
    e = sp.expand(e.subs({n: 99, k: 14}))
    R[i] = (F(str(e.subs({n3: 0, z11: 0}))), F(str(e.coeff(n3))), 4 * F(str(e.coeff(z11))))   # (a, b, per-z slope)
repo = {}
for i, m in enumerate(cls7): repo.setdefault((p[i], q[i], r[i]), []).append(m)
unmatched = [i for i, t in R.items() if t not in repo]
print("corrected printed formulas matching a repo class in ALL THREE coefficients (a, b_n3, c_z):", 208 - len(unmatched), "; unmatched:", unmatched)
hit = set(m for t in R.values() for m in repo.get(t, []))
print("repo classes not hit:", [m for m in cls7 if m not in hit])
# n3-only sanity: which printed formulas match at 705 but have a different n3 coefficient?
byval = {}
for i, m in enumerate(cls7): byval.setdefault((p[i] + 705 * q[i], r[i]), []).append((m, q[i]))
for i, (a, b, c) in R.items():
    key = (a + 705 * b, c)
    if key in byval and all(qq != b for _, qq in byval[key]): print("  n3-coefficient mismatch: z_%d printed b=%s, repo b=%s" % (i, b, [qq for _, qq in byval[key]]))
json.dump({"classes": cls7, "p": [str(x) for x in p], "q": [str(x) for x in q], "r": [str(x) for x in r]}, open("repo_family_affine.json", "w"))
