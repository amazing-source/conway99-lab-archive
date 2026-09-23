# Wave 200 proof-B audit: additive two-face gluing

```yaml
role: proof_b
date_utc: 2026-07-29T06:42:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Hostile audit of the uniform Q0=7037,7038 exclusion: verify the
  at-most-63 slack budget, the forced saturation lower bound, and
  especially the additivity and distinct-fiber premises behind the
  local inequality 3s<=delta, deriving the conditional Q>=7039.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave196-four-fiber-hilton-milner-verifier/package-manifest.sha256: eb833bf4ad503fb2243882704492f6bf836525f4b619de8a1979ffc6f0f785c9
  attempts/wave198-orientation-lift-proof-b/package-manifest.sha256: ba949fa2ededb7a23596fa0b05ca9e2d259f0e6a18c042814e2f3bc87b5b9054
  attempts/wave198-orientation-lift-proof-a-audit/package-manifest.sha256: 60f5b4a87893fe0e820f05989e666c26abaaa8f30b9a5598a7a7db571740c924
  attempts/wave199-near-face-gluing-proof-b-audit/package-manifest.sha256: a754b48754faac4c98febc7c5cae6ab351c416bf144403e1d456ba4020381e6c
  attempts/wave200-two-face-gluing-proof-a/package-manifest.sha256: b909a16d3324f76e394322e6058f844bcf3bcc61409d567fdfd6f50ab53aced4
method: >-
  Exact integer slack arithmetic and a per-pair-fiber decomposition of
  local leaf occurrences. The fixed-center four-vertex fibers are
  disjoint, so repeated-label losses add. The two fixed Hilton--Milner
  equality templates are used only at c_x=13. No graph, code, cover,
  SAT, LP, configuration, enumeration, isomorphism, or brute-force search.
command: >-
  python -B attempts/wave200-two-face-gluing-proof-b-audit/exact_check.py
  --verify attempts/wave200-two-face-gluing-proof-b-audit/exact-results.json;
  python -B -m unittest -v
  attempts/wave200-two-face-gluing-proof-b-audit/test_exact_check.py
outputs:
  - agents/2026-07-29-wave200-two-face-gluing-proof-b-audit.md
  - attempts/wave200-two-face-gluing-proof-b-audit/
limitations:
  - This is a proof-B hostile audit, not clean-room verifier promotion.
  - The result is conditional on the frozen prism-free rank-11 endpoint.
  - The coarse budget mechanism does not exclude Q0=7039.
  - It supplies no incompatible endpoint upper bound.
  - Rank 11, endpoint existence, strict original n3 improvement,
    external novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

`AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

The arithmetic and the additive local loss both survive hostile audit.
Conditionally,

```text
Q>=7039.                                          (1)
```

## 1. Uniform budget and forced saturation

For either `Q0=7037` or `Q0=7038`, let

```text
B=40Q0-(76C-349V).
```

At `C=4158,V=99`, these two budgets are respectively 23 and 63. The
Wave198 nonnegative certificate contains the subrow

```text
S5+3SH+13SF+9g<=B.                               (2)
```

Retain

```text
S5=5delta+5eta+epsilon,
4q=297-3SF-3g-SH+epsilon+delta+eta,
s>=q-epsilon.
```

Then

```text
4s
 >=297-3SF-3g-SH-3epsilon+delta+eta
 >=297-(3SF+3g+SH+3S5)
 >=297-3B.                                       (3)
```

The last step is coefficientwise from three times (2). Thus the two
faces separately give

```text
Q0     B    forced s
7037   23   s>=57
7038   63   s>=27.
```

In particular, uniformly,

```text
s>=27.                                           (4)
```

## 2. Why distinct saturated labels use distinct fibers

Fix a center `x`. Its 84 nonneighbors are partitioned into 21 fibers

```text
F_x(P)={y:P_x(y)=P},  |F_x(P)|=4,
```

one for each pair `P` of local blocks. Every exact-three flag whose
three-set contains `P` has exactly one leaf in `F_x(P)`.

For a pair type `P`, let

```text
d_P = number of full-pool flags whose three-set contains P,
u_P = number of distinct leaves used in F_x(P).
```

The fixed-center three-set family is simple, so `d_P<=5`. If an
orientation `x->y` has selected multiplicity five and `P_x(y)=P`, then
five selected flags use `y` as their `P`-type leaf. Consequently

```text
d_P=5,  u_P=1,
```

and this fiber loses `d_P-u_P=4` labels. A second distinct saturated
label cannot use the same `P`: all five possible `P`-flags already have
their unique `P`-type leaf equal to `y`.

The fibers are disjoint because every leaf has a unique type `P_x(y)`.
Therefore

```text
j_x=sum_P u_P,
3c_x=sum_P d_P,
3c_x-j_x=sum_P(d_P-u_P).                        (5)
```

This proves that the four-unit losses from different saturated labels
are additive; no overlap correction is needed.

## 3. Tight and deficient centers

Write

```text
delta_x=36-j_x,
s_x=number of saturated orientations centered at x.
```

If `c_x=13`, the verified Hilton--Milner equality classification gives
exactly three pair types with `d_P=5`. Every saturated type loses four;
every other degree-five type loses at least one because its fiber has
only four vertices. Hence the occurrence loss in (5) is at least

```text
4s_x+(3-s_x)=3+3s_x.
```

Since `3c_x=39`,

```text
delta_x
 =36-39+(39-j_x)
 >=3s_x.                                        (6)
```

If `c_x<=12`, each saturated fiber contributes four additively, while
the unused baseline `36-3c_x` is nonnegative. Thus

```text
delta_x
 =36-3c_x+(3c_x-j_x)
 >=36-3c_x+4s_x
 >=4s_x.                                        (7)
```

Equations (6)--(7) give `3s_x<=delta_x` at every center. Summing,

```text
3s<=delta.                                       (8)
```

There is no assumption here that the deficient family has a
Hilton--Milner equality form; (7) uses only the fiber partition.

## 4. Contradiction and boundary

From `S5=5delta+5eta+epsilon` and the budget,

```text
delta<=S5/5<=B/5<=63/5.
```

Since `delta` is integral, `delta<=12`; (8) gives `s<=4`, contradicting
(4). Therefore both candidate faces are excluded and (1) follows.

Adding the 693 verified edge-isolated projective circuits gives at least
7,732 projective circuit classes and 15,464 nonzero scalar circuit
words.

At `Q0=7039`, `B=103` and the coarse right side `297-3B` in (3) is
negative. This audit confirms only that this mechanism stops there; it
does not claim that the face exists.

The sealed proof-A package has 10 matching manifest entries, exact replay
passes, and all six tests pass. No source file was modified.

```text
budgets 23 and 63:                       AUDIT PASS
forced saturation s>=27:                AUDIT PASS
distinct-fiber premise:                 AUDIT PASS
additive local loss 3s<=delta:           AUDIT PASS
local/global cap s<=4:                  AUDIT PASS
Q0=7037 and Q0=7038 faces:              REFUTED
conditional Q>=7039:                    DERIVED
clean-room verifier promotion:          pending
endpoint contradiction:                no
Conway-99 / external novelty:           UNKNOWN
```
