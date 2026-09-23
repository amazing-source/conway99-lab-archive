import re, sys, json, math
from fractions import Fraction as F
import sympy as sp
sys.argv = ["x", "../arxiv/r7/The_Subgraphs_of_Order_Seven.tex"]
src = open("parse_r7.py", encoding="utf-8").read()
# reuse parser only (stop before the enumeration section)
exec(src.split("# ---- specialise")[0])
n, k, n3, z11 = sp.symbols("n k n3 z11")
Zc = dict(Z)
Zc[21]  = sp.expand(n*k*(k-2)*(k-4) - 2*n3 - z11/2)
Zc[80]  = sp.expand(sp.Rational(1,2)*n*k*(k-2)*(k-4)*(2*k-17) + 16*n3 + sp.Rational(3,2)*z11)
Zc[84]  = Zc[80]
Zc[176] = sp.expand(sp.Rational(1,8)*n*k*(k-2)*(k-4)*(k**4-24*k**3+236*k**2-1136*k+2264) + 6*(5*k-34)*n3 - 9*z11)
tot = sp.expand(sum(Zc.values()))
nk = k*(k-2)/2 + k + 1
target = sp.expand(sp.binomial(n, 7).expand(func=True).subs(n, nk))
print("corrected: coeff n3 =", sp.factor(tot.coeff(n3)), "| coeff z11 =", sp.factor(tot.coeff(z11)))
print("corrected: const - C(n,7) on srg locus =", sp.factor(sp.expand(tot.subs({n3:0,z11:0}).subs(n, nk) - target)))
for i in (21,80,84,176):
    print(" z_%d printed: %s\n        corrected: %s" % (i, Z[i], Zc[i]))
# also check the corrected formulas against the wave-23 family at n3=705 for these four
w23 = json.load(open("../conway-99-research/attempts/wave23-weighted-extensions/affine-witness.json"))
fam = {r["canonical_mask"]: (r["count_at_z_min"], r["delta_per_z"]) for r in w23["order_seven_affine_family"]["records"]}
for i in (21,80,84,176):
    e = Zc[i].subs({n:99,k:14}); v = e.subs({n3:705, z11:1412}); d = 4*e.coeff(z11)
    print(" z_%d corrected at (705,1412): %s slope %s -> repo classes: %s" % (i, v, d, [m for m,(a,b) in fam.items() if a==v and b==d]))
# corrected enumeration at (99,14)
spec = {i: sp.expand(e.subs({n:99,k:14})) for i,e in Zc.items()}
rows = [(F(str(e.subs({n3:0,z11:0}))), F(str(e.coeff(n3))), F(str(e.coeff(z11)))) for i,e in sorted(spec.items())]
import numpy as np
D = [math.lcm(a.denominator,b.denominator,c.denominator) for a,b,c in rows]
A = np.array([int(a*d) for (a,_,_),d in zip(rows,D)]); B = np.array([int(b*d) for (_,b,_),d in zip(rows,D)]); C = np.array([int(c*d) for (_,_,c),d in zip(rows,D)]); Dv = np.array(D)
feas = {}
zgrid = np.arange(0, 4*4158+1)
for v in range(0, 4159):
    vals = A[:,None] + B[:,None]*v + C[:,None]*zgrid[None,:]
    ok = np.all(vals>=0,axis=0) & np.all(vals % Dv[:,None]==0,axis=0)
    zs = zgrid[ok]
    if zs.size: feas[v]=(int(zs[0]),int(zs[-1]),int(zs.size))
n3s = sorted(feas)
print("corrected feasible n3: count", len(n3s), "min", n3s[0], "max", n3s[-1])
bad = [v for v in n3s if not (feas[v][0] == ((2*v+3)//4)*4 and feas[v][1] == 4*v)]
print("n3 values whose z11 range differs from [ceil4(2n3), 4n3]:", bad[:10], "count", len(bad))
print("at n3=705:", feas.get(705), " at 708:", feas.get(708), " at 4158:", feas.get(4158))
