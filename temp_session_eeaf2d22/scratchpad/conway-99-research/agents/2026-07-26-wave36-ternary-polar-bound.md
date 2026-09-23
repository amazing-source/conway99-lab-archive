# Wave 36 ternary polar-graph rank bound

```yaml
role: proof_b
date_utc: 2026-07-26T22:59:41Z
git_commit: 697cc02bcbe16b69aaf08822298e03c66329c64c
claim_label: CANDIDATE
scope: >
  Conditional n3=4158 lower bound on rank_F3(M), obtained by embedding the
  endpoint rows in the norm-two projective orthogonality graph over F_3.
inputs:
  verification/wave35-n3-upper-spectral/independent-results.json: c704d8fce8f1d5975204b9a06ada0098c66fbdb9e0de8016a1ff89d86e691305
  verification/wave35-n3-upper-spectral/run-report.yaml: 40ded0143abe9b0edcec1b87146621dd6ee0fae3483d3d522fec0c83417d6c95
method: >
  Exact quadratic-form point counts, strongly-regular polar-graph
  parameters, and a rational spectral-mixing inequality.
command: |
  .\.venv\Scripts\python.exe -B -m unittest -v attempts/wave36-ternary-polar-bound/test_exact_check.py
  .\.venv\Scripts\python.exe -B attempts/wave36-ternary-polar-bound/exact_check.py --output attempts/wave36-ternary-polar-bound/exact-results.json
  .\.venv\Scripts\python.exe -B attempts/wave36-ternary-polar-bound/exact_check.py --verify attempts/wave36-ternary-polar-bound/exact-results.json
outputs:
  attempts/wave36-ternary-polar-bound/exact_check.py: 50c943b520a253db4d98838f78e58753570d61b31795dca4d5a49471dd054bf9
  attempts/wave36-ternary-polar-bound/test_exact_check.py: 6fa0c4b4177c7eabd77ea488fd0eb2f966c8dd7caf249914334b946a917a482b
  attempts/wave36-ternary-polar-bound/exact-results.json: 7d7c15ad99952ee3ca70582a887e771331156b8ef8e50524d296f1dc15f425a1
  attempts/wave36-ternary-polar-bound/input-freeze.sha256: b78e5b241c67188c2ea6ab34f5e38800cc394eaa3f3159ebeb2ed1231a24dba9
  attempts/wave36-ternary-polar-bound/failed-routes.md: f150a99e5eb778d054dfe36840b4bc43c687f4320c6332c9be0a3cf84bdef1cb
limitations:
  - Discovery-side candidate requiring independent adversarial verification.
  - No endpoint matrix, finite-field point configuration, or graph is constructed.
  - Rank twelve with square discriminant and every rank from 13 through 44 survive.
  - The endpoint n3=4158 is not excluded and the global upper bound is unchanged.
  - No literature-novelty claim is made.
```

## Claim

Conditional on the prism-free endpoint `n3=4158`, let

```text
r3=rank_F3(M)=rank_F3(C),  C=2M-21I.
```

The Wave 35 endpoint package gives

```text
C^2=441I,
diag(C)=-13,
C_ij in {0,+2,-2},
(+2,-2,0) off-diagonal row counts = (32,36,162),
rank_Q(M)=44.
```

The new candidate conclusion is

```text
r3 >= 12.                                           (1)
```

Moreover, if `r3=12`, the nondegenerate factor form described below must
have square determinant class over `F_3`.

This improves a modular necessary condition.  It does not exclude the
endpoint, so the rigorous graph-theoretic upper bound remains `n3<=4158`.

## 1. The endpoint rows give 231 distinct polar points

Reduce modulo three.  A symmetric rank-`r3` factorization gives

```text
C = V H V^T,
```

where `V` has 231 rows `v_i`, has full column rank `r3`, and `H` is a
nondegenerate symmetric form.  Since the diagonal of `C` is two modulo
three,

```text
(v_i,v_i)_H=2.
```

The projective points `[v_i]` are distinct.  If `v_i=v_j`, the distinct
integer alphabet residues force

```text
row_i(C)-row_j(C)=-15(e_i-e_j).
```

If `v_i=-v_j`, they instead force

```text
row_i(C)+row_j(C)=-15(e_i+e_j).
```

Either displayed integer vector has squared norm `450`.  But `C^2=441I`
makes distinct integer rows orthogonal with squared norm 441, so either their
sum or difference has squared norm `882`.  Hence neither proportionality is
possible.  Since the only nonzero scalars in `F_3` are `+1` and `-1`, the
rows define 231 distinct norm-two projective points.

Every endpoint row has exactly 162 zero off-diagonal entries.  Therefore
each selected projective point is orthogonal to exactly 162 other selected
points.

## 2. The ambient finite orthogonal graph

Let `W` be an `r`-dimensional nondegenerate quadratic space over `F_3`.
Its determinant has one of two square classes.  Write

```text
Omega_r^epsilon
```

for the projective points represented by vectors of norm two, and join two
points when they are orthogonal.

Every form is congruent to

```text
diag(1,...,1,epsilon),  epsilon in {1,2}.
```

The checker counts norm residues by adding one coordinate at a time.  If
`N_r^epsilon=|Omega_r^epsilon|`, the orthogonality graph has

```text
v      = N_r^epsilon,
k      = N_(r-1)^(2 epsilon),
lambda = N_(r-2)^epsilon.
```

The determinant class toggles in the first orthogonal complement because a
norm-two line has determinant two.  Two orthogonal norm-two lines span
determinant `2*2=1`, so the codimension-two complement retains the original
class.

The orthogonal group is transitive on ordered adjacent pairs and on ordered
distinct nonadjacent pairs of these anisotropic projective points.  Thus the
graph is strongly regular.  Its remaining parameter follows from the usual
two-path count:

```text
(v-k-1) mu = k(k-lambda-1).
```

The two nonprincipal adjacency eigenvalues are the roots of

```text
x^2-(lambda-mu)x-(k-mu)=0.
```

All counts and roots used below are exact integers.

## 3. Exact spectral-mixing obstruction

Let `A` be the adjacency matrix of a `k`-regular graph on `v` vertices, and
let `theta` be its largest nonprincipal eigenvalue.  For the characteristic
vector `x` of an `m`-vertex subset,

```text
x = (m/v) 1 + y,  y perpendicular to 1.
```

Consequently

```text
x^T A x
 <= k m^2/v + theta(m-m^2/v).
```

If the induced subgraph is `d`-regular, then `x^T A x=md`, giving the exact
average-degree bound

```text
d <= (k m + theta(v-m))/v.                       (2)
```

Here `m=231` and the endpoint requires `d=162`.

The exact cases near the boundary are:

| `r` | determinant | `v` | `k` | `lambda` | `mu` | `theta` | right side of (2) |
|---:|:---:|---:|---:|---:|---:|---:|---:|
| 7 | square | 378 | 117 | 36 | 36 | 9 | 75 |
| 7 | nonsquare | 351 | 126 | 45 | 45 | 9 | 86 |
| 8 | square | 1080 | 351 | 126 | 108 | 27 | 963/10 |
| 8 | nonsquare | 1107 | 378 | 117 | 135 | 9 | 86 |
| 9 | square | 3240 | 1107 | 378 | 378 | 27 | 104 |
| 9 | nonsquare | 3321 | 1080 | 351 | 351 | 27 | 4110/41 |
| 10 | square | 9882 | 3321 | 1080 | 1134 | 27 | 104 |
| 10 | nonsquare | 9801 | 3240 | 1107 | 1053 | 81 | 1710/11 |
| 11 | square | 29646 | 9801 | 3240 | 3240 | 81 | 9561/61 |
| 11 | nonsquare | 29403 | 9882 | 3321 | 3321 | 81 | 158 |
| 12 | square | 88452 | 29403 | 9882 | 9720 | 243 | 4149/13 |
| 12 | nonsquare | 88695 | 29646 | 9801 | 9963 | 81 | 158 |

Both determinant classes have right side strictly below 162 for every
`r<=11`.  Dimensions at most six already contain fewer than 231 norm-two
projective points.  This proves (1), conditional on independent verification.

At `r=12`, the nonsquare class still has upper bound 158 and is impossible,
while the square class has upper bound `4149/13` and survives.

## 4. What this does not prove

The polar graph supplies an ambient space in which any endpoint row
configuration must sit.  Passing its density test is only a necessary
condition.  No set of 231 points, endpoint matrix, or Conway graph is
constructed here, and no value of `n3` is excluded.
