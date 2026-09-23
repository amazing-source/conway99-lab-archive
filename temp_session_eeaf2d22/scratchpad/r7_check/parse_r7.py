"""Transcribe Reimbayev arXiv:2608.19410v1 order-seven frequency formulas from TeX,
check figure-free consistency identities, specialise to srg(99,14,1,2), and
enumerate the feasible (n3, z11) lattice.

Usage: python parse_r7.py <path to The_Subgraphs_of_Order_Seven.tex>
"""
import re, sys, json
from fractions import Fraction
import sympy as sp

TEX = sys.argv[1]
src = open(TEX, encoding="utf-8").read()
blk = src[src.index(r"\begin{flalign*}"): src.index(r"\end{flalign*}")]
blk = blk.replace(r"\begin{flalign*}", "")
# join continuation lines ("\\&" at start of the next physical line)
blk = re.sub(r"\\\\\s*&", "", blk)
lines = [l.strip() for l in blk.split("\\\\") if l.strip()]

n, k, n3, z11 = sp.symbols("n k n3 z11")

def tex2expr(s):
    s = s.replace("&", "").replace(" ", "")
    s = s.rstrip(",.")
    # \frac{A}{B} with one level of nested braces
    frac = re.compile(r"\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}")
    while True:
        s2 = frac.sub(lambda m: "((%s)/(%s))" % (m.group(1), m.group(2)), s)
        if s2 == s:
            break
        s = s2
    s = s.replace("z_{11}", "Z").replace("n_3", "N")
    assert "_" not in s and "\\" not in s, s
    s = s.replace("^", "**")
    # tokenise and insert explicit multiplication
    toks = re.findall(r"\d+|[nkNZ]|\*\*|[()+\-/]", s)
    assert "".join(toks) == s, (s, toks)
    out = []
    for i, t in enumerate(toks):
        if i > 0:
            p = toks[i - 1]
            if (p.isdigit() or p in "nkNZ" or p == ")") and (t in "nkNZ" or t == "(" or t.isdigit()):
                out.append("*")
        out.append(t)
    e = sp.sympify("".join(out), locals={"n": n, "k": k, "N": n3, "Z": z11})
    return sp.expand(e)

Z = {}
for l in lines:
    m = re.match(r"z_\{?(\d+)\}?=(.*)", l.replace(" ", ""))
    assert m, l
    i = int(m.group(1))
    assert i not in Z, i
    Z[i] = tex2expr(m.group(2))
assert sorted(Z) == list(range(1, 209)), (len(Z), sorted(Z)[:5], sorted(Z)[-5:])
print("parsed", len(Z), "formulas")

# every formula must be affine in (n3, z11)
for i, e in Z.items():
    P = sp.Poly(e, n3, z11)
    assert P.total_degree() <= 1, (i, e)

# ---- figure-free identity 1: sum of all frequencies = C(n,7) on the srg locus n = k(k-2)/2 + k + 1
tot = sp.expand(sum(Z.values()))
coef_n3 = sp.expand(tot.coeff(n3)); coef_z11 = sp.expand(tot.coeff(z11))
const = sp.expand(tot.subs({n3: 0, z11: 0}))
print("sum: coeff n3 =", sp.factor(coef_n3), "| coeff z11 =", sp.factor(coef_z11))
nk = k * (k - 2) / 2 + k + 1
target = sp.expand(sp.binomial(n, 7).expand(func=True).subs(n, nk))
diff = sp.expand(const.subs(n, nk) - target)
print("sum const - C(n,7) on srg locus:", sp.factor(diff))
print("  at (99,14):", const.subs({n: 99, k: 14}), "vs C(99,7) =", sp.binomial(99, 7))

# ---- specialise
spec = {i: sp.expand(e.subs({n: 99, k: 14})) for i, e in Z.items()}
rows = []
for i in range(1, 209):
    e = spec[i]
    a = Fraction(str(e.subs({n3: 0, z11: 0})))
    b = Fraction(str(e.coeff(n3))); c = Fraction(str(e.coeff(z11)))
    rows.append((i, a, b, c))
json.dump([[i, str(a), str(b), str(c)] for i, a, b, c in rows], open("spec99.json", "w"), indent=0)

# ---- enumerate feasible integer (n3, z11): all z_i >= 0 and integral
import math, numpy as np
D = [math.lcm(a.denominator, b.denominator, c.denominator) for _, a, b, c in rows]
A = np.array([int(a * d) for (_, a, _, _), d in zip(rows, D)], dtype=np.int64)
B = np.array([int(b * d) for (_, _, b, _), d in zip(rows, D)], dtype=np.int64)
C = np.array([int(c * d) for (_, _, _, c), d in zip(rows, D)], dtype=np.int64)
Dv = np.array(D, dtype=np.int64)
print("denominators lcm:", math.lcm(*D))

# crude outer box from simple rows (z4=2n3>=0, z1>=0, z2, z3)
n3max = 99 * 14 * 12 // 4
feas = {}
zgrid = np.arange(0, 4 * n3max + 1, dtype=np.int64)
for v in range(0, n3max + 1):
    vals = A[:, None] + B[:, None] * v + C[:, None] * zgrid[None, :]
    ok = np.all(vals >= 0, axis=0) & np.all(vals % Dv[:, None] == 0, axis=0)
    zs = zgrid[ok]
    if zs.size:
        feas[v] = zs.tolist()
n3s = sorted(feas)
print("feasible n3 count:", len(n3s), "min", n3s[0] if n3s else None, "max", n3s[-1] if n3s else None)
# describe the projection
if n3s:
    steps = sorted(set(np.diff(n3s).tolist()))
    print("n3 gaps:", steps[:10])
    for v in n3s[:5] + n3s[-3:]:
        print("  n3=%d: z11 in [%d..%d], %d values" % (v, feas[v][0], feas[v][-1], len(feas[v])))
    # intersect with repo rigorous interval 708<=n3<=4158
    inter = [v for v in n3s if 708 <= v <= 4158]
    print("intersection with 708<=n3<=4158:", len(inter), "values; min", inter[0] if inter else None, "max", inter[-1] if inter else None)
    # which formulas are tight somewhere (active constraints)
    active = set()
    for v in n3s:
        for zz in (feas[v][0], feas[v][-1]):
            vals = A + B * v + C * zz
            for idx in np.where(vals == 0)[0]:
                active.add(rows[idx][0])
    print("formulas active (=0) at some boundary point:", sorted(active))
json.dump({str(v): [feas[v][0], feas[v][-1], len(feas[v])] for v in n3s}, open("feasible_n3_z11.json", "w"))
