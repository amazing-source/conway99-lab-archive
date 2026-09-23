"""Match Reimbayev's 208 printed order-seven formulas (specialised to (99,14)) against the
conway-99-research wave-23 affine family (n3=705, z=h11/4 in [353..705]) and the wave-44
endpoint witness (n3=4158, h11=16632), without using the paper's figures.

A printed formula z_i = a + b*n3 + c*z11 matches repo class J iff
   value at (705, 1412) == count_at_z_min(J)   and   4*c == delta_per_z(J)
   and, if the class is also pinned at the endpoint, value at (4158,16632) == witness(J).
"""
import json, sys
from fractions import Fraction as F
REPO = sys.argv[1]
spec = {int(i): (F(a), F(b), F(c)) for i, a, b, c in json.load(open("spec99.json"))}

w23 = json.load(open(REPO + "/attempts/wave23-weighted-extensions/affine-witness.json"))
recs = w23["order_seven_affine_family"]["records"]
assert w23["parameters"]["h11_min"] == 1412
fam = {r["canonical_mask"]: (r["count_at_z_min"], r["delta_per_z"]) for r in recs}
w44 = json.load(open(REPO + "/attempts/wave44-rooted-flags/rooted-witness.json"))
print("wave44 keys:", w44["format"] if "format" in w44 else "", "h11", w44["h11"])
sup = w44["support"]
# support format discovery
print("support type:", type(sup).__name__, "len", len(sup), "sample:", (sup[:2] if isinstance(sup, list) else list(sup.items())[:2]))
end = {}
if isinstance(sup, dict):
    for kk, vv in sup.items():
        end[int(kk)] = int(vv)
else:
    for e in sup:
        if isinstance(e, dict):
            m = e.get("canonical_mask", e.get("mask")); end[int(m)] = int(e.get("count", e.get("value")))
        else:
            end[int(e[0])] = int(e[1])
for m in fam:
    end.setdefault(m, 0)   # witness lists support only; absent classes have count 0

def val(i, n3, z11):
    a, b, c = spec[i]; return a + b * n3 + c * z11

# invert: for each repo class, the two-point data -> which printed formulas agree
by_sig = {}
for m, (v0, d) in fam.items():
    by_sig.setdefault((v0, d, end[m]), []).append(m)
match, nomatch = {}, []
for i in range(1, 209):
    v0 = val(i, 705, 1412); d = 4 * spec[i][2]; ve = val(i, 4158, 16632)
    key = (v0, d, ve)
    if v0.denominator == 1 and d.denominator == 1 and ve.denominator == 1 and (int(v0), int(d), int(ve)) in by_sig:
        match[i] = by_sig[(int(v0), int(d), int(ve))]
    else:
        # partial: match on the n3=705 family only
        part = [m for m, (a0, dd) in fam.items() if v0 == a0 and d == dd]
        nomatch.append((i, part))
print("formulas fully matched to a repo class:", len(match))
multi = {i: ms for i, ms in match.items() if len(ms) > 1}
print("formulas whose signature is shared by several repo classes:", len(multi))
matched_masks = set(m for ms in match.values() for m in ms)
print("repo classes hit:", len(matched_masks), "of", len(fam))
print("\nUNMATCHED printed formulas (i, classes matching at n3=705 only):")
for i, part in nomatch:
    a, b, c = spec[i]
    print("  z_%d = %s + %s*n3 + %s*z11   | 705-family matches: %s" % (i, a, b, c, part))
unhit = [m for m in fam if m not in matched_masks]
print("\nrepo classes not hit by any printed formula:", len(unhit))
for m in unhit:
    v0, d = fam[m]
    # infer the affine (a,b,c) from the two repo points assuming c = d/4 and linearity in n3
    c = F(d, 4)
    # v0 = a + 705 b + 1412 c ; end = a + 4158 b + 16632 c  -> b = (end - v0 - c*(16632-1412)) / (4158-705)
    b = (F(end[m]) - v0 - c * (16632 - 1412)) / (4158 - 705)
    a = v0 - 705 * b - 1412 * c
    print("  mask %d: count(705,z)=%d%+d*(z-353), endpoint=%d  -> repo-implied (a,b,c) = (%s, %s, %s)" % (m, v0, d, end[m], a, b, c))
json.dump({"match": {str(i): ms for i, ms in match.items()}, "unmatched": nomatch, "unhit": unhit}, open("match_result.json", "w"), indent=1)
