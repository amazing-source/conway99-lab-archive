# Wave 199 proof-B audit: near-face gluing contradiction

```yaml
role: proof_b
date_utc: 2026-07-29T06:22:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Independent hostile audit of the Q0=7037 face exclusion: reconstruct
  the 23-unit Wave198 slack budget, the global orientation-multiplicity
  lower bound, the tight and deficient local-center caps, and the
  conditional consequence Q>=7038.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave196-four-fiber-hilton-milner-verifier/package-manifest.sha256: eb833bf4ad503fb2243882704492f6bf836525f4b619de8a1979ffc6f0f785c9
  attempts/wave198-orientation-lift-proof-b/package-manifest.sha256: ba949fa2ededb7a23596fa0b05ca9e2d259f0e6a18c042814e2f3bc87b5b9054
  attempts/wave198-orientation-lift-proof-a-audit/package-manifest.sha256: 60f5b4a87893fe0e820f05989e666c26abaaa8f30b9a5598a7a7db571740c924
  attempts/wave199-near-face-gluing-proof-a/package-manifest.sha256: 1a3aa613b343fa071eee79fc337742f25f0aa949cc141f8da4eca29ecfb72671
  attempts/wave199-near-face-gluing-proof-b-audit/independent-result-freeze.sha256: 9c78ecd7234b402e69e7148f8621031d1463ed2504664cd51ee7af80da8d2494
method: >-
  Clean-room integer slack arithmetic, oriented multiplicity deficits,
  four-fiber repetition, the classified Hilton--Milner equality
  templates, exact source comparison, and replay. No graph, code, cover,
  SAT, LP, configuration, enumeration, isomorphism, or brute-force search.
command: >-
  python -B attempts/wave199-near-face-gluing-proof-b-audit/exact_check.py
  --verify attempts/wave199-near-face-gluing-proof-b-audit/exact-results.json;
  python -B -m unittest -v
  attempts/wave199-near-face-gluing-proof-b-audit/test_exact_check.py
outputs:
  - agents/2026-07-29-wave199-near-face-gluing-proof-b-audit.md
  - attempts/wave199-near-face-gluing-proof-b-audit/
limitations:
  - This is a proof-B hostile audit, not clean-room verifier promotion.
  - The result is conditional on the frozen prism-free rank-11 endpoint.
  - It excludes Q0=7037 but supplies no incompatible endpoint upper bound.
  - The Wave198 generic-discovery import failure is a non-mathematical
    portability limitation and is not evidence for the theorem.
  - Rank 11, endpoint existence, strict original n3 improvement, external
    novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

`AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

The budget identity, both global multiplicity identities, all integer
rounding, and both local-center cases survive hostile audit.  The
conditional conclusion is

```text
Q>=7038.                                          (1)
```

The independent mathematical result was frozen at SHA-256
`9c78ecd7234b402e69e7148f8621031d1463ed2504664cd51ee7af80da8d2494`
before the sealed proof-A package was opened.

## 1. Exact 23-unit budget

Wave198 proves

```text
Q0-(76C-349V)/40
 =4SI/5+6S2/5+SE2/5+7RA/10+3SL/10
  +S5/40+3SH/40+13SF/40
  +a1/10+3b3/5+c2/5+9g/40+2W/5.
```

If `Q=7037`, then `Q0` is an integer with

```text
281457/40<=Q0<=Q,
```

so `Q0=7037`.  Multiplication by 40 gives

```text
32SI+48S2+8SE2+28RA+12SL+S5+3SH+13SF
 +4a1+24b3+8c2+9g+16W=23.                       (2)
```

All entries are nonnegative integers.  In particular,

```text
SF<=1, g<=2, SH<=7, S5<=23.                      (3)
```

## 2. Global orientation multiplicity

Let

```text
T       = selected oriented-label union,
J       = full-pool oriented-label union,
a       = a3+b3,
delta   = 3564-J,
eta     = J-T-a.
```

For each occupied nonprivate selected orientation, let `m` be its
selected multiplicity.  Put

```text
q       = number of those orientations,
epsilon = sum(5-m).
```

Private selected type-three labels have one occupied orientation of
multiplicity one.  Direct substitution into the Wave198 row gives

```text
S5=5delta+5eta+epsilon.                           (4)
```

The selected incidence and union identities are

```text
3n3=p3+5q-epsilon,
3564-delta-eta=p3+q+a.
```

Using

```text
n3+h+g=1287-SF,
a=3h-SH,
```

eliminates `n3,h,p3,a` and gives

```text
4q=297-3SF-3g-SH+epsilon+delta+eta.              (5)
```

Equations (3)--(5) imply

```text
delta+eta<=4,
epsilon<=23,
4q>=281,
q>=71.
```

Every orientation below multiplicity five contributes at least one to
`epsilon`.  Hence at least

```text
s>=q-epsilon>=48                                 (6)
```

nonprivate selected orientations have multiplicity five.

## 3. Local gluing permits at most seven

Let `c_x` be the number of full-pool flags centered at `x`, and `j_x`
their leaf union.  Then

```text
sum_x(13-c_x)=SF<=1,
sum_x(36-j_x)=delta<=4.                          (7)
```

Thus all centers have `c_x=13`, except possibly one center with `c_x=12`.

If an orientation `x->y` has multiplicity five, all five selected flags
use the fixed pair-fiber `P_x(y)` and the same fiber vertex `y`.

For `c_x=13`, the local family is one of the two Hilton--Milner equality
templates.  It has exactly three degree-five pairs.  A saturated pair
loses four of its five leaf occurrences, while the other two degree-five
fibers each lose at least one.  Therefore

```text
s_x<=3,
36-j_x>=3.                                       (8)
```

For the possible `c_x=12` center, a saturated orientation alone loses
four leaf occurrences, and five incidences are required per saturated
orientation.  Since the 12 triples have 36 pair incidences,

```text
36-j_x>=4,
s_x<=floor(36/5)=7.                              (9)
```

If the deficient center saturates, it consumes all four units of
`delta`, so no tight center can saturate.  Otherwise at most one tight
center saturates by (8).  Thus

```text
s<=7.                                            (10)
```

This is stronger than the earlier loose `s<=12` estimate.  Equations
(6) and (10) contradict each other, excluding `Q0=7037` and proving (1).

Adding 693 verified edge-isolated projective circuits gives at least
7,731 projective circuit classes and 15,462 nonzero scalar circuit words.

## 4. Sealed-source comparison and replay

Only after the independent result freeze was hashed did the audit inspect
the sealed proof-A manifest
`1a3aa613b343fa071eee79fc337742f25f0aa949cc141f8da4eca29ecfb72671`.
The source and independent derivations agree on:

- the exact 23-unit budget;
- `q>=71` and `s>=48`;
- the strengthened local bound `s<=7`;
- exclusion of `Q0=7037`; and
- the conditional bound `Q>=7038`.

All ten source manifest entries match, the source exact replay passes,
and all six source tests pass.

The sealed Wave198 proof-A-audit package also passes its documented exact
replay and all six documented tests.  Generic unittest discovery,
however, fails to import its test module because the test uses

```text
from .exact_check import ...
```

without a package context.  This is a relative-import portability issue,
not a mathematical failure, and no sealed source was modified.

## Boundary

```text
independent result frozen before source:  PASS
23-unit budget:                          AUDIT PASS
global q and saturation identities:      AUDIT PASS
tight c=13 center:                       AUDIT PASS
deficient c=12 center:                   AUDIT PASS
Q0=7037 face:                            REFUTED
conditional Q>=7038:                     DERIVED
source manifest/replay/tests:             PASS
Wave198 generic discovery portability:    FAIL (non-math)
clean-room verifier promotion:            pending
endpoint contradiction:                   no
Conway-99 / external novelty:             UNKNOWN
```
