# Wave 48 exact facial-reduction verification

Status: **VERIFIED_SCOPED** for the exact affine rank and the eleven complete
universal moment kernels. Endpoint feasibility and `n3=4158` remain
**UNKNOWN**.

## Independent reconstruction

Before parsing the Wave48 face-claim JSON, the verifier:

- froze the Wave44 row system and Wave45/Wave47 coefficient hashes;
- concatenated all 170 Wave44 integer equations;
- computed an exact rational RREF with rank 93 and affine nullity 116;
- checked 170 particular-solution identities and `170*116=19,720`
  homogeneous nullspace identities exactly;
- derived every needed order-4, order-5, and order-6 count from induced-subset
  identities on the rational affine space; and
- for every moment family, stacked one affine-point matrix and 116 exact
  direction matrices, computed the exact common kernel, and proved completeness
  by rank plus nullity equalling the ambient matrix size.

The independently sealed reconstruction has SHA-256
`e2b7c1684cf4681504c303a090fe3b8f9882ddb2a6c514a973fd6686394a10e4`.

The exact active-rank/nullity pairs are:

| Source | Family | Rank | Nullity |
|---|---|---:|---:|
| Wave45 | `ordered_edge` | 1 | 15 |
| Wave45 | `ordered_nonedge` | 1 | 18 |
| Wave45 | `vertex` | 12 | 5 |
| Wave47 | `root_000` | 58 | 6 |
| Wave47 | `root_001` | 50 | 6 |
| Wave47 | `root_010` | 50 | 6 |
| Wave47 | `root_011` | 36 | 6 |
| Wave47 | `root_100` | 50 | 6 |
| Wave47 | `root_101` | 36 | 6 |
| Wave47 | `root_110` | 36 | 6 |
| Wave47 | `root_111` | 17 | 3 |

All ranks also agree modulo `1000003`, `1000033`, and `1000037`.

## Comparison

Only after the reconstruction was written and frozen did the verifier parse
`attempts/wave48-conic-moment/exact-faces.json`. All eleven family comparisons
passed:

- ambient sizes, exact active ranks, and nullities agree;
- independently reconstructed and discovery kernel bases span the same
  rational subspaces;
- forced-zero diagonal sets and modular ranks agree; and
- every discovery kernel vector was marked as an exact affine identity.

The Wave48 discovery Python implementation was neither imported nor executed.
No floating solver result, candidate, residual, eigenvalue, or dual artifact
was opened.

## Reproduction

From the repository root:

```powershell
.\.venv\Scripts\python.exe verification\wave48-conic-moment\verify_exact_faces.py reconstruct
.\.venv\Scripts\python.exe verification\wave48-conic-moment\verify_exact_faces.py compare
.\.venv\Scripts\python.exe -m unittest verification\wave48-conic-moment\test_exact_faces.py
```

The reconstruction enforces a 20% free-physical-memory floor. This scoped
verification does not prove SDP feasibility or infeasibility, exclude the
endpoint, construct a graph, or prove a strict upper bound.
