import json, sys
from fractions import Fraction as F
REPO = sys.argv[1]
spec = {int(i): (F(a), F(b), F(c)) for i, a, b, c in json.load(open("spec99.json"))}
w23 = json.load(open(REPO + "/attempts/wave23-weighted-extensions/affine-witness.json"))
fam = {r["canonical_mask"]: (r["count_at_z_min"], r["delta_per_z"]) for r in w23["order_seven_affine_family"]["records"]}
tot = sum(v for v, d in fam.values()); print("repo family sum at (705,1412):", tot, "C(99,7)=14887031544", "slope sum", sum(d for v,d in fam.values()))
def val(i, n3, z11):
    a, b, c = spec[i]; return a + b * n3 + c * z11
sig = {}
for m, (v0, d) in fam.items(): sig.setdefault((v0, d), []).append(m)
hit = {}; bad = []
for i in range(1, 209):
    key = (val(i, 705, 1412), 4 * spec[i][2])
    ms = sig.get((int(key[0]), int(key[1])) if key[0].denominator == 1 and key[1].denominator == 1 else None)
    if ms: hit[i] = ms
    else: bad.append(i)
print("printed formulas matching some repo class at n3=705:", len(hit), "; unmatched:", bad)
for i in bad: print("   z_%d -> (a,b,c)=%s  value(705,1412)=%s" % (i, spec[i], val(i, 705, 1412)))
# ambiguity / multiplicity
from collections import Counter
cnt = Counter()
for i, ms in hit.items():
    for m in ms: cnt[m] += 1
over = {m: c for m, c in cnt.items() if c > len(sig[(fam[m][0], fam[m][1])])}
print("repo signatures hit by MORE printed formulas than classes sharing the signature:")
for m, c in over.items(): print("   mask", m, "count", fam[m], "classes sharing sig:", sig[(fam[m][0], fam[m][1])], "printed hits:", [i for i, ms in hit.items() if m in ms])
unhit = [m for m in fam if m not in cnt]
print("repo classes hit by no printed formula:", len(unhit))
for m in unhit: print("   mask %d: count(705,z)=%d %+d*(z-353)" % (m, *fam[m]))
print("sum of printed constants deficit:", 14887031544 - sum(val(i,705,1412) for i in range(1,209)))
