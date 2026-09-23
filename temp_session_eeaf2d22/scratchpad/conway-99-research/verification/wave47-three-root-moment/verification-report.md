# Wave 47 three-root moment: independent exact verification

## Verdict

**`VERIFIED_SCOPED`.**

The sealed Wave 47 finite construction was independently reproduced without
importing or executing its discovery implementation:

- all eight pointwise-labelled three-vertex root families;
- every locally admissible order-five flag with two unordered free vertices;
- every exact order-five, order-six, and order-seven coefficient;
- all Petersen and Clebsch direct Gram controls;
- all 17 immutable seven-count witnesses and their lower decks;
- all 2,664 supplied integer negative directions; and
- all 2,657 distinct primitive PSD inequalities and source cut values.

This verifies a finite obstruction ledger for the 17 recorded aggregate count
vectors.  It does **not** test the full PSD-constrained count region, exclude
`n3=4158`, prove a strict upper bound, construct a graph, or resolve
Conway-99.

## Separation and sealed inputs

The verifier is self-contained in `verify.py`.  It reads sealed JSON claims
and witness data but never imports or calls `three_root_moment.py`,
`compact_handoff.py`, or any other discovery implementation.  The shared
local `(lambda,mu)=(1,2)` admissibility convention and exact finite Gram
protocol were taken from the already independent Wave 45 verifier-side
contract.

Before and after the replay, the verifier checked:

- `compact-handoff.json`:
  `8b74110bc6ae983e288d448cd1a963f81521f178e8280bbbf5864274a1639a47`;
- `package-manifest.sha256`:
  `3fee6bf5ec42c5b70138f508ba3fbff6b44b56870601ea25111cd7da93473737`;
- canonical compact-handoff payload:
  `e6d1991c20c8c30c4e393a081cf3fa3c4264b6ee5dacae279d5b6ab726766867`;
- all six frozen Wave 43--45 input hashes;
- `coefficients.json`:
  `07b55f06ff8f7d5f2de53d92a3222366e122a7306028752ecd31c10962a824b3`;
- `results.json`:
  `a58d04b56ed66094536ffc158b32085e3e940e5c3e42a3983a471e95e99daf37`;
- `cuts.json`:
  `d2ea38ed74a1b9098c9cc8eae52f8d65723c2631335b0acedba647dc16aa313e`.

The manifest members and full reconstruction artifacts were unchanged at the
end of the run.

## Independent class and flag reconstruction

The verifier exhausts every labelled simple graph mask, applies the adjacent
common-neighbor cap one and nonadjacent cap two, and removes complete vertex
permutation orbits.  It obtained:

| Order | Admissible labelled masks | Unlabelled classes | Class-stream SHA-256 |
|---:|---:|---:|---|
| 5 | 683 | 21 | `f9bd6d5818a81c1b026ac46e467609435576a54f933e6d5beac5c13b20259686` |
| 6 | 13,174 | 62 | `5cd10b0861dfba894731a89a269255a7c0a495f8ee7420552aebb13bafb8b75f` |
| 7 | 394,020 | 208 | `89c646b6cae3018cad44b2f73cd1ef2569f4e108132002f0bcc7653d7229314a` |

The root-pattern bits are independently interpreted as ordered pairs
`01,02,12`.  Only the two free vertices are quotiented by their swap; roots
remain fixed pointwise.  The exact flag dimensions are:

| Family | Flags | Ordered roots at `n=99` |
|---|---:|---:|
| `root_000` | 64 | 590,436 |
| `root_001` | 56 | 99,792 |
| `root_010` | 56 | 99,792 |
| `root_011` | 42 | 16,632 |
| `root_100` | 56 | 99,792 |
| `root_101` | 42 | 16,632 |
| `root_110` | 42 | 16,632 |
| `root_111` | 20 | 1,386 |

The eight ordered-root counts sum to `99*98*97=941094`.  Every root has
`C(96,2)=4560` free pairs.

## Exact coefficients and adversarial convention checks

For each unrooted class, the verifier enumerates every ordered root triple and
every ordered pair of two-subsets whose union is the entire nonroot set.  This
gives union order five, six, or seven exactly once.  No automorphism divisor
is used.

The eight family streams contain 57,006 nonzero upper-triangle class entries.
The entire independently constructed coefficient document equals the sealed
document as a data structure, with canonical payload SHA-256
`34b7c6b19a2224bb9407e3dff45b819acfabc08565c6b9c1389d8a7eb4c6b283`.

The following hostile checks passed:

- all 48 combinations of an `S3` root permutation and source family give the
  exact cross-family flag bijection and coefficient-tensor permutation;
- every class all-ones sum equals its full ordered-root and ordered-free-pair
  census, ruling out hidden automorphism division;
- all 136 witness all-ones quadratics equal the exact normalization
  denominator;
- all 16 control all-ones quadratics have the direct combinatorial value;
- every one of the 2,664 direction linearizations distinguishes the correct
  `diagonal + 2*off-diagonal` formula from an undoubled hostile formula; and
- every admissible labelled mask maps to one unique minimum representative
  under the complete vertex-permutation orbit.

## Direct graph controls

The verifier independently constructs the Petersen graph as
`srg(10,3,0,1)` and the Clebsch graph as `srg(16,5,0,2)`.

For each graph and all eight root patterns, the direct sum of integer outer
products equals the unrooted coefficient expansion entry by entry.  All 16
matrix hashes match the handoff and sealed results.  PSD is exact by the
explicit outer-product representation, including the zero triangle-root
matrix for both triangle-free controls.

The induced-subset totals are:

- Petersen: `(252,210,120)` at orders `(5,6,7)`;
- Clebsch: `(4368,8008,11440)` at orders `(5,6,7)`.

## Witnesses, directions, and cuts

For every source support, the verifier checks compact SHA-256, strict mask
ordering, uniqueness, positivity, canonical class membership, and total
`C(99,7)=14887031544`.

Order-five and order-six counts are independently recovered from every
seven-deck by

```text
sum_J x_J d_m(H,J) = C(99-m,7-m) N_H.
```

Every division is exact and nonnegative.  All 17 witnesses give the same
lower decks, with sparse hashes:

- order five:
  `2401552a01692a2ac65b6c0df65c29b3ca5bb9f5d4cf67951cdb0e2fbb7b9032`;
- order six:
  `0050a1de6446a5b64af4c98c985b1812cf7241f3c30b71f0ae0f598537228861`.

All 136 independently expanded witness matrices match their sealed SHA-256
values.  Every supplied integer vector is primitive, has the correct
dimension, and satisfies the claimed exact quadratic numerator, which is
strictly negative.  Direction totals are 158, 156, and the recorded 15
Wave45 iteration totals, summing to 2,664.

For each direction the verifier independently forms the order-five through
order-seven quadratic coefficients, folds the lower orders into the
constant, divides by the exact greatest common divisor, and hashes the
primitive payload.  The raw quadratic equals the linearized source value
times the primitive divisor in every case.

First-occurrence deduplication gives exactly 2,657 cuts.  The independently
constructed list equals all 2,657 sealed records, including coefficients,
constants, primitive divisors, vectors, source routing, source values, and
cut hashes.  The seven removed occurrences are repeated `root_000` vectors,
not lost inequalities.  All 17 compact representative cuts also match their
complete-ledger records exactly.

## Numerical diagnostic note

The sealed `numerical_negative_eigenvalue_count` fields use a relative
reporting cutoff of `-1e-8` times the spectral scale.  The verifier reproduces
all 136 reported counts and minimum-eigenvalue diagnostics; the largest raw
minimum-eigenvalue difference was `0.00018310546875`, while the largest
normalized difference was below `4.86e-17`.

A separate backward-error threshold sees two additional small negative
floating modes in five matrices: the three Wave43 one-edge-root matrices,
Wave45 iteration 8 `root_000`, and Wave45 iteration 13 `root_000`.  This is
not a failure of an exact claim: the handoff claims the 2,664 directions the
run found, not a complete exact inertia, and all supplied directions replay.
The float counts remain diagnostic only.

## Reproduction and tests

From the repository root:

```powershell
.\.venv\Scripts\python.exe verification\wave47-three-root-moment\verify.py
.\.venv\Scripts\python.exe -m unittest verification\wave47-three-root-moment\test_verify.py -v
.\.venv\Scripts\python.exe verification\wave47-three-root-moment\verify.py --validate verification\wave47-three-root-moment\verification-results.json
```

The complete replay succeeded.  All six unit tests passed, and validation of
the generated record succeeded.  The verification record SHA-256 is
`1c80d2b70b8e6bef42d4d9df124cc82dc9baf642d36873c61e91e8f2acc99a43`.

The 20% free-memory guard never approached its floor; the minimum recorded
free physical memory was 55.34%.

## Scope wall

- finite Wave 47 reconstruction: `VERIFIED_SCOPED`;
- exact refutation of the 17 recorded aggregate witnesses: `VERIFIED_SCOPED`;
- full PSD-constrained integer count region: not tested;
- endpoint `n3=4158`: `UNKNOWN`;
- strict upper bound below `4158`: `NOT_PROVED`;
- graph construction: none;
- Conway-99: `UNKNOWN`;
- novelty and priority: `UNKNOWN`.
