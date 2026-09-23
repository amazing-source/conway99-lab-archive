# Wave 48 combined conic moment scout

Status: `CANDIDATE_NUMERICAL / EXACT_FACES_DERIVED`; endpoint `UNKNOWN`.

## Combined real relaxation

This package combines:

- all 170 exact Wave 44 endpoint count equations;
- nonnegativity of all 208 order-seven class variables;
- `2079 <= h11/4 <= 4158`;
- all three sealed Wave 45 one/two-root moment families; and
- all eight sealed Wave 47 three-root/two-free moment families.

Counts are scaled as probabilities and every moment matrix is divided by its
exact probability-normalization denominator. CVXPY 1.9.2 with Clarabel 0.11.1
and SCS 3.2.11 is used only as a floating heuristic.

## Exact facial reduction

The 170-row rational affine system has exact rank 93 and nullity 116. Direct
minimum-eigenvalue optimization was degenerate because every moment family
has universal affine kernel directions. `exact_faces.py` rationalizes the
small integer directions, proves every matrix-vector identity by exact
reduction against the Wave 44 equations, and proves completeness by matching
the complementary rank modulo three primes.

```text
family                    active rank / nullity
Wave45 ordered edge              1 / 15
Wave45 ordered nonedge           1 / 18
Wave45 vertex                   12 / 5
Wave47 root 000                 58 / 6
Wave47 root 001                 50 / 6
Wave47 root 010                 50 / 6
Wave47 root 011                 36 / 6
Wave47 root 100                 50 / 6
Wave47 root 101                 36 / 6
Wave47 root 110                 36 / 6
Wave47 root 111                 17 / 3
```

No individual diagonal is forced to zero by the affine equations. The faces
come from non-coordinate linear combinations of flags. The exact face result
SHA-256 is
`49d157a2c6025f7a7d1149619959e3f488229d619a5c65a03a79e7a71a93f066`.

## Numerical verdict

No solver run produced an exact feasible vector or an exact infeasibility
dual. The diagnostics instead cluster around a highly degenerate boundary:

| Run | Status | Minimum probability | Minimum eigenvalue | Scaled equation residual |
|---|---|---:|---:|---:|
| Clarabel, original margin | `optimal_inaccurate` | `-1.58e-11` | `-3.35e-10` | `1.11e-13` |
| SCS, original margin | `optimal` | `-3.68e-7` | `-2.36e-6` | `3.03e-9` |
| Clarabel, exact face | `optimal_inaccurate` | `-1.67e-8` | `-2.29e-8` | `3.00e-15` |

The signs and scales disagree, and every displayed candidate violates
nonnegativity or PSD by a small floating amount. Therefore:

```text
robust real feasible point:      NOT RETAINED
exact real feasible point:       NONE
exact infeasibility certificate: NONE
numerical conclusion:            UNKNOWN
endpoint n3=4158:                UNKNOWN
```

The bounded margin-zero/log-det analytic-center follow-up exceeded its wall
budget and was terminated. It emitted no artifact and no candidate. This is
a failed numerical route, not infeasibility evidence.

## Next same-order moment layer

Five labelled roots plus one free vertex is a tractable and genuinely
different next layer. Two flags unite on only six or seven vertices, so no
order-eight variables are needed.

- 21 canonical locally admissible root types, representing 683 labelled root
  masks;
- matrix sizes from 10 to 32 (listed in `wave48-summary.json`);
- roughly 44,600 order-six and 524,000 order-seven labelled-root embeddings,
  before the factor of two for ordered free-vertex pairs.

Recommendation: build the 21 canonical families next. Root relabelling must
be proved as a pointwise-label permutation congruence between matrices. That
uses equality of labelled counting problems and does not assume any
automorphism of the unknown target graph.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave48-conic-moment\exact_faces.py --verify

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave48-conic-moment -p "test_*.py" -v
```

The numerical files preserve their complete solver versions, settings,
statuses, residuals, candidate vectors, eigenvalue diagnostics, and dual
summaries. Rerunning a floating solver is not expected to be byte
deterministic.

All heavy stages enforce a 20% free-physical-memory guard. No target-graph
automorphism is assumed.

## Scope wall

- Exact facial identities do not prove PSD feasibility.
- Floating feasibility does not become evidence through a solver status.
- Tiny negative margins are not infeasibility certificates.
- An aggregate PSD witness would not construct a graph.
- The Wave 47 coefficient package remains `CANDIDATE` pending its clean-room
  verification.
- Branch 15, the endpoint, a strict upper bound, and Conway-99 remain
  `UNKNOWN`.
