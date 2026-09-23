# Wave 45 finite flag-moment handoff v1

## Exact scoped result

This immutable handoff derives the first genuinely overlap-sensitive
positive-semidefinite constraints used in the Conway-99 endpoint search.
For a rooted flag `F`, let `c_F(theta)` count free vertex subsets giving that
flag around a labelled root embedding `theta`. The finite matrix

```text
M(F,F') = sum_theta c_F(theta)c_F'(theta)
```

is an exact sum of outer products, so every actual graph must make it positive
semidefinite.

The v1 matrices are:

| Type | Root labels | Flag size | Matrix | Union orders |
|---|---:|---:|---:|---:|
| vertex | 1 | 4 | 17 x 17 | 4 through 7 |
| ordered edge | 2 | 4 | 16 x 16 | 4 through 6 |
| ordered nonedge | 2 | 4 | 19 x 19 | 4 through 6 |

Every overlap size is included. Coefficients count labelled-root embeddings
and ordered pairs of unordered free subsets directly; there is no
automorphism division or target-graph symmetry assumption.

At `n=99,k=14`, the exact probability normalization denominators are

```text
vertex:          99 * C(98,3)^2
ordered edge:    99*14 * C(97,2)^2
ordered nonedge: 99*84 * C(97,2)^2.
```

## Findings

The frozen Wave 43 unrooted witness and Wave 44 rooted witness both fail the
17-by-17 vertex moment matrix:

| Witness | Minimum normalized eigenvalue | Exact status |
|---|---:|---|
| Wave 43 | -0.0025217705384230947 | integer negative directions retained |
| Wave 44 | -0.008511645783987358 | integer negative directions retained |

The edge and nonedge matrices are exact LDL-positive-semidefinite of rank one.
The stored-result artifact retains six exact negative vertex directions for
each original witness. Known Petersen `(10,3,0,1)` and Clebsch `(16,5,0,2)`
SRG controls match direct Gram matrices exactly; hostile diagonal and
embedding-coefficient mutations are rejected.

Seed 0 then ran a fresh exact QF_LIA model after each cut. Fifteen additional
nonnegative integer solutions of all 170 Wave 44 rows were found and replayed
exactly. Every one was also exactly indefinite and supplied a new primitive
integer cut. The sixteenth solve timed out:

```text
retained cuts:       17
exact witnesses:     15
terminal status:     QF_LIA_UNKNOWN (timeout)
endpoint n3=4158:    UNKNOWN
strict upper bound:  NOT PROVED
Conway-99:           UNKNOWN
```

This rejects 17 specific aggregate witnesses—the original two plus 15 fresh
models. It does not exclude the entire feasible region.

## Immutable package boundary

The v1 package contains only:

- `checkpoint-v1-seed0-17cuts-15witnesses.json`;
- `checkpoint-v1-moment-coefficients.json`;
- `checkpoint-v1-stored-witness-results.json`;
- `checkpoint-v1-manifest.sha256`;
- `flag_moment-v1.py`;
- `replay-v1.py`;
- `replay-v1-results.json`;
- this README;
- `run-report-v1.yaml`; and
- `package-manifest-v1.sha256`.

Mutable files such as `cutting-plane.json`, unversioned scripts/results, smoke
outputs, and every `*.log` file are intentionally excluded. The three sealed
JSONs are never rewritten.

## Replay

From the repository root:

```powershell
.\.venv\Scripts\python.exe attempts\wave45-flag-moment\replay-v1.py
```

The replay independently rebuilds all coefficient tensors, re-evaluates both
stored witnesses, reconstructs all 17 primitive cuts, checks all 170 equations
for each of 15 QF_LIA witnesses, and verifies each exact negative quadratic
direction. Its retained verdict is `UNKNOWN` globally.

The versioned code fails closed if these external dependencies drift:

- `verification/wave43-seven-deck-endpoint/independent_check.py`
  SHA-256 `324a4b84c081c8d2ad8a6a11bae45e0327c03ee2158036156c27efa66fcf790b`;
- `attempts/wave43-seven-deck-endpoint/exact-results.json`
  SHA-256 `06b498a736a511a7d6f5912bd4686e5d4eb30f4041477e3ee9cbc1704f1757c8`;
- `attempts/wave44-rooted-flags/rooted-witness.json`
  SHA-256 `9be153b2487c3e07e20bffeb7ee6c890e69caa6e8d6b6e2936fbc5d8927bd5b9`;
- `attempts/wave44-rooted-flags/exact_check.py`
  SHA-256 `dac369a7cdea1bdd81e3bca689a428664e4cb6f89756e0095bac94d5e1947dfa`.

## Next flag level

The smallest still-available stronger lane is a three-labelled-vertex type
with five-vertex flags: two such flags unite on at most seven vertices, so it
can still be expressed in the existing order-seven variables. If that lane
also survives, ordered-pair five-vertex flags require order-eight variables,
and one-root five-vertex flags require order-nine variables.
