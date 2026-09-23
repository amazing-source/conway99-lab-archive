# Wave 45 clean-room flag-moment verification

Status: **finite Gram construction and immutable checkpoint verified; endpoint
UNKNOWN**.

This verifier froze its protocol, implementation, coefficient streams, and
Petersen/Clebsch controls before opening the Wave 45 discovery package. It
then compared only the sealed checkpoint-v1 artifacts, never the mutable live
search files.

## Exact finite matrices

For every labelled root embedding `rho`, let `z_rho` count induced
four-vertex rooted flags. The verified matrix is

```text
M = sum_rho z_rho z_rho^T.
```

Every actual graph therefore satisfies `c^T M c >= 0` for every integer
vector `c`. All overlaps between the two selected flags are retained. Their
unique unions express the matrix in unrooted induced-class counts:

```text
vertex root:          17 x 17, union orders 4..7
ordered edge root:    16 x 16, union orders 4..6
ordered nonedge root: 19 x 19, union orders 4..6.
```

The independent census found `9,21,62,208` locally admissible unrooted
classes at orders `4,5,6,7`. After translating the discovery upper-triangle
format, every one of its 484 class-matrix records and 16,660 nonzero ordered
entries matches the clean-room stream exactly.

The combined canonical stream SHA-256 is
`5eace9a5008e40c8a1a430bec43b23027fd0d564a0d440f354a8ec101fbdd4b9`.

## Independent controls

Direct sums of outer products on explicit Petersen and Clebsch graphs agree
entry-for-entry with the unrooted-class expansion for all three root types.
The exact matrix SHA-256 values also match discovery:

| Graph | Vertex | Ordered edge | Ordered nonedge |
|---|---|---|---|
| Petersen | `544605c5...9afc` | `00448b99...9aa2` | `47009713...afaa` |
| Clebsch | `1ff7f27c...b235` | `72effb5f...5fe4` | `9aa0a3ce...f077` |

Both graphs also pass exact lower-order reconstruction from their
seven-vertex decks and the all-ones quadratic identities.

## Stored witness result

The Wave 43 and Wave 44 aggregate count witnesses both fail the necessary
vertex-root PSD condition. Six independently replayed integer directions
for each witness have exact negative quadratic values:

```text
Wave 43:
-2439686160282, -642660113620, -27729959832,
-286352047812,  -21295863304,  -18307661814

Wave 44:
-3434158925036, -420407978596, -468970998184,
  -46796180000,   -1158870788, -161364476608
```

This exactly refutes those two aggregate vectors. It does not refute the
endpoint.

The ordered-edge and ordered-nonedge matrices are exact PSD matrices of rank
one for both witnesses. Structurally, these matrices use only induced counts
through order six, which are already fixed at the endpoint. The vertex-root
matrix reaches order seven and is the first of these three families capable
of distinguishing the competing seven-class witnesses.

## Immutable cutting checkpoint

The verifier accepted only
`checkpoint-v1-seed0-17cuts-15witnesses.json`, SHA-256
`96a50f9add4b12b2c86587da29ade8b9da34f88a7b7617c048ffb7139c12b64b`.

Exact replay established:

- all 17 cuts reconstruct from the independent coefficient stream;
- all 15 witnesses satisfy the original 170 equations;
- every witness satisfies all cuts retained before its iteration;
- every newly generated cut has a strictly negative exact value on its
  source witness;
- all 3,499 sparse cut coefficients are covered by the sealed records.

The next solver call returned `unknown` with reason `timeout`. Consequently:

```text
Wave 43 stored count witness: REFUTED
Wave 44 stored count witness: REFUTED
17-cut finite continuation:  VERIFIED INCOMPLETE
endpoint n3=4158:             UNKNOWN
strict upper bound:           NOT PROVED
Conway-99:                    UNKNOWN.
```

Live searches beyond checkpoint v1 are deliberately outside this verification
scope.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave45-flag-moment\independent_verify.py `
  --verify verification\wave45-flag-moment\independent-results.json

.\.venv\Scripts\python.exe -B `
  verification\wave45-flag-moment\compare_discovery.py `
  --verify verification\wave45-flag-moment\comparison-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave45-flag-moment -p "test_*.py" -v

.\.venv\Scripts\python.exe -B `
  verification\wave45-flag-moment\manifest_check.py
```
