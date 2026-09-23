# Wave 198 proof-A hostile audit: orientation lift

## Verdict

`ACCEPTED_AS_DERIVED`.

I independently reconstructed the orientation-sensitive incidence row and
the exact coefficient identity, then compared them line by line with the
sealed Wave198 proof-B package. No counterexample, orientation collision,
or coefficient discrepancy survived.

Conditionally on the frozen prism-free rank-11 endpoint,

```text
Q>=7037.
```

This remains a proof-agent result pending clean-room verifier promotion.
No graph, code, cover, SAT, LP, configuration, enumeration, isomorphism,
or brute-force search is used.

```yaml
role: proof_a
date_utc: 2026-07-29T05:55:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Hostile independent audit of the sealed Wave198 orientation-lift row,
  its interaction with privacy and old-raw orientations, and the exact
  Q>=7037 rational certificate.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  attempts/wave198-orientation-lift-proof-b/package-manifest.sha256: ba949fa2ededb7a23596fa0b05ca9e2d259f0e6a18c042814e2f3bc87b5b9054
method: >-
  Reconstruct oriented flag multiplicities without proof-B arithmetic,
  attack every possible label collision, expand the proposed certificate
  over independent rational coefficient vectors, and replay its null row.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave198-orientation-lift-proof-a-audit\exact_check.py --verify
  attempts\wave198-orientation-lift-proof-a-audit\exact-results.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave198-orientation-lift-proof-a-audit\test_exact_check.py
outputs:
  - agents/2026-07-29-wave198-orientation-lift-proof-a-audit.md
  - attempts/wave198-orientation-lift-proof-a-audit/
limitations:
  - This hostile proof-A audit does not itself confer verifier status.
  - The theorem remains conditional on the prism-free rank-11 endpoint.
  - The rational null is arithmetic only, not an asserted object.
  - No incompatible endpoint upper bound is obtained.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain
    UNKNOWN.
```

## 1. Independent orientation reconstruction

For an unordered label `e={x,y}` used by selected exact-three circuits,
let

```text
s_e = selected exact-three multiplicity of e,
t_e = number of occupied orientations x->y and y->x.
```

The Wave197 local theorem permits at most five selected flags with one
fixed center. Therefore

```text
s_e<=5*t_e.
```

There is no hidden factor of two. Two exact-three circuits on one
canonical flag are companions with the same three labels, and a minimal
cover cannot select both because neither would then own a private label.

Every one of the `p3` private labels occurs in exactly one selected
circuit. Its opposite orientation cannot occur in a second selected
circuit without destroying privacy. Hence its contribution is exactly

```text
s_e=t_e=1.
```

Writing `T=sum_e t_e`, the selected flags have three oriented labels
apiece, so

```text
3*n3+4*p3<=5*T.                                 (1)
```

## 2. Collision audit against the full pool

The `a3+b3` old-raw assignments come from private type-one/type-two source
labels outside the selected type-three label union.

- Distinct source private labels give distinct unordered labels.
- Two exact-three type-two raws on one source label have opposite
  orientations, not a collision.
- Their source labels lie outside the selected union, so neither
  orientation can collide with one counted by `T`.

Thus all `a3+b3` assignments add distinct oriented labels outside the
selected orientations. The verified full flag pool has oriented union
`J<=36V`, giving

```text
T+a3+b3<=J<=36V.
```

Combining this with (1) proves the proposed row

```text
S5=180V-3*n3-4*p3-5*a3-5*b3>=0.                (2)
```

As a consistency check, direct expansion gives

```text
S10=2*S5+(3*n3-p3).
```

The final term is nonnegative because a selected exact-three circuit has
only three labels. Hence (2) really strengthens, rather than merely
renames, the unordered Wave197 capacity row.

## 3. Independent coefficient audit

After the four raw substitutions

```text
n1=a1+a2+a3,
2*p2=b1+b3,
p3=c1+c2,
r1=a1+b1+c1,
```

independent rational vectors reproduce exactly

```text
Q0-(76C-349V)/40

 =4SI/5+6S2/5+SE2/5+7RA/10+3SL/10
  +S5/40+3SH/40+13SF/40
  +a1/10+3b3/5+c2/5+9g/40+2W/5.               (3)
```

The residual coefficient vector is exactly

```text
a1/10+3b3/5+c2/5+9g/40+2W/5,
```

with no negative or omitted coefficient.

The independently replayed rational row makes all eight structural
slacks in (3) zero and gives

```text
Q0=281457/40=7036.425.
```

Since the frozen pool theorem gives `Q>=Q0` and `Q` is integral,

```text
Q>=7037.
```

Adding the 693 edge-isolated projective circuits gives 7,730 projective
short circuits, or 15,460 nonzero scalar circuit words.

## 4. Hostile boundary checks

- Allowing both companions on one flag would invalidate the count, but
  minimal-cover privacy forbids that case.
- Treating a private unordered label as occupying two orientations would
  invalidate the bonus `4*p3`, but the second selected occurrence would
  contradict privacy.
- Reusing an old-raw orientation inside `T` would invalidate the gluing
  row, but old sources are private labels outside the selected
  type-three union.
- The Wave197 rational null has `S5=-165`; this correctly shows that the
  new row cuts off that arithmetic relaxation. It does not retroactively
  claim the old null was an object.

## Boundary

```text
five flags per fixed orientation:       frozen input
selected oriented incidence (1):        AUDIT PASS
old/raw orientation separation:         AUDIT PASS
S5>=0:                                  AUDIT PASS
certificate (3):                        independent exact replay PASS
rational null replay:                   PASS, not an object
conditional Q>=7037:                    ACCEPTED AS DERIVED
clean-room verifier promotion:          pending
endpoint contradiction:                 no
Conway-99 / external novelty:            UNKNOWN
```
