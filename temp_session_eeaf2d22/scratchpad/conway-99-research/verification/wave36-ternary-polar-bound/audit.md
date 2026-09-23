# Wave 36 ternary polar-graph adversarial audit

Verdict: **PASS for the scoped conditional rank bound**

The candidate argument is correct:

```text
n3=4158  ==>  rank_F3(M)>=12.
```

If equality holds, the nondegenerate factor form must have square determinant
class over `F_3`.  The proof does not exclude the endpoint: rank twelve with
square determinant and every rank from 13 through 44 survive this density
test.  The graph-theoretic upper bound remains `n3<=4158`, and Conway-99
remains `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-26T23:08:30Z
git_commit: 697cc02bcbe16b69aaf08822298e03c66329c64c
claim_label: VERIFIED
audit_verdict: PASS_SCOPED_CONDITIONAL_RANK_BOUND
scope: >-
  Conditional n3=4158 finite-field factorization, polar-point embedding,
  strong regularity, exact spectrum, mixing bound, rank floor, and
  rank-twelve determinant-class split.
inputs:
  agents/2026-07-26-wave36-ternary-polar-bound.md: 062e8b5478b93195dae4d9a571677688cefcd7397cda75246dbd03503f7c9b85
  attempts/wave36-ternary-polar-bound/exact_check.py: 50c943b520a253db4d98838f78e58753570d61b31795dca4d5a49471dd054bf9
  attempts/wave36-ternary-polar-bound/test_exact_check.py: 6fa0c4b4177c7eabd77ea488fd0eb2f966c8dd7caf249914334b946a917a482b
  attempts/wave36-ternary-polar-bound/exact-results.json: 7d7c15ad99952ee3ca70582a887e771331156b8ef8e50524d296f1dc15f425a1
  verification/wave36-ternary-polar-bound/input-freeze.sha256: 48cce8d7726d885b4b4045e9446838b6903a3ed856a91e462d219d2fa8d49673
method: >-
  Independent quadratic-space and graph reconstruction without importing the
  discovery module, including a direct proof and exhaustive controls for the
  degenerate nonadjacent-span case. Candidate replay followed independent
  completion.
command: |-
  .\.venv\Scripts\python.exe -B -m unittest -v verification/wave36-ternary-polar-bound/test_independent_check.py
  .\.venv\Scripts\python.exe -B verification/wave36-ternary-polar-bound/independent_check.py --verify verification/wave36-ternary-polar-bound/independent-results.json
  .\.venv\Scripts\python.exe -B -m unittest -v attempts/wave36-ternary-polar-bound/test_exact_check.py
  .\.venv\Scripts\python.exe -B attempts/wave36-ternary-polar-bound/exact_check.py --output verification/wave36-ternary-polar-bound/submitted-regenerated.json
outputs:
  verification/wave36-ternary-polar-bound/independent_check.py: 1fafb633e2bc4967f1af8f72239064ebbed627a0899a716e4800fb6e8fd03c49
  verification/wave36-ternary-polar-bound/test_independent_check.py: 9b6a898667c489384999c4454d8b800e02e8fce6f4f10030903f95159275f259
  verification/wave36-ternary-polar-bound/independent-results.json: 38ec002886c2a9b38f8d11824dc79e07147b16386dcc3449064633efb630beeb
  verification/wave36-ternary-polar-bound/submitted-regenerated.json: 7d7c15ad99952ee3ca70582a887e771331156b8ef8e50524d296f1dc15f425a1
limitations:
  - The graph-to-reflection bridge is inherited from the verified Wave 35 package.
  - The endpoint matrix and its finite-field factor rows are hypothetical.
  - Passing the ambient polar-graph density bound is not a realization.
  - Rank twelve square determinant and ranks thirteen through forty-four survive.
  - Endpoint exclusion, a stronger n3 upper bound, and novelty are not obtained.
```

## 1. Conditional endpoint rows

At the putative endpoint, the verified Wave 35 package gives

```text
C=2M-21I,
C^2=441I,
diag(C)=-13,
C_ij in {0,+2,-2},
(+2,-2,0) off-diagonal counts=(32,36,162),
rank_Q(M)=44.
```

Modulo three, `C=2M`, so `rank_F3(C)=rank_F3(M)=r`.  A symmetric rank-`r`
matrix over `F_3` has a factorization

```text
C=V H V^T,
```

where `V` has full column rank and `H` is symmetric and nondegenerate.  This
follows by choosing a basis of the column space, using equality of row and
column spaces for a symmetric matrix, and applying left and right inverses to
make the coordinate form symmetric and nonsingular.

For every row `v_i` of `V`,

```text
(v_i,v_i)_H=C_ii=2 mod 3.
```

The 231 projective points `[v_i]` are distinct.  If two factor rows were
equal, the integer rows of `C` would be congruent modulo three.  Residue
injectivity of `{0,+2,-2}`, together with `-13=+2 mod 3`, forces

```text
row_i(C)-row_j(C)=-15(e_i-e_j).
```

If the factor rows were negatives, the same check forces

```text
row_i(C)+row_j(C)=-15(e_i+e_j).
```

Either forced vector has squared norm 450.  But `C^2=441I` makes distinct
integer rows orthogonal of norm squared 441, so either combination has norm
squared 882.  Thus equality and antipodality are impossible.  These are all
nonzero projective scalings over `F_3`.

Finally, `C_ij=0 mod 3` precisely when the integer entry is zero.  Each
selected projective point is therefore orthogonal to exactly 162 of the
other selected points.  The endpoint rows induce a 162-regular subgraph on
231 vertices in the ambient graph defined below.

## 2. Both determinant classes and exact point counts

Every nondegenerate symmetric form of dimension `r` over `F_3` is congruent
to exactly one of

```text
diag(1,...,1,epsilon),  epsilon in {1,2},
```

according to its determinant square class.  Let `N_r^epsilon` be the number
of projective lines of norm two.

For one coordinate of coefficient `a`, zero contributes norm zero once and
the two nonzero field elements contribute norm `a` twice.  Convolving these
three residue distributions gives the following counts:

| dimension | square determinant | nonsquare determinant |
|---:|---:|---:|
| 1 | 0 | 1 |
| 2 | 2 | 1 |
| 3 | 6 | 3 |
| 4 | 12 | 15 |
| 5 | 36 | 45 |
| 6 | 126 | 117 |
| 7 | 378 | 351 |
| 8 | 1080 | 1107 |
| 9 | 3240 | 3321 |
| 10 | 9882 | 9801 |
| 11 | 29646 | 29403 |
| 12 | 88452 | 88695 |

The independent checker also enumerates every vector through dimension seven,
normalizes the first nonzero coordinate to one, and obtains the same table.
In dimensions at most six, neither class has 231 points.

## 3. Why the orthogonality graph is strongly regular

Let `Omega_r^epsilon` consist of the norm-two projective points, adjacent
when orthogonal.

### Vertices and degrees

The vertex count is

```text
v=N_r^epsilon.
```

For a norm-two vector `v`, the decomposition

```text
W=<v> orthogonal-direct-sum v^perp
```

shows that `v^perp` has determinant class `2epsilon`, since
`2^-1=2 mod 3`.  Therefore every vertex has degree

```text
k=N_(r-1)^(2epsilon).
```

This also proves vertex transitivity: complements of norm-two lines have the
same dimension and determinant class and are therefore isometric.

### Adjacent pairs

Two orthogonal norm-two vectors span a nondegenerate plane of determinant
`2*2=1`.  Its complement has dimension `r-2` and determinant class
`epsilon`.  Hence every adjacent pair has

```text
lambda=N_(r-2)^epsilon
```

common neighbors.  The same decomposition maps any ordered adjacent pair to
any other, proving adjacent-pair transitivity.

### Nonadjacent pairs and the degenerate span

This is the delicate case.  For distinct nonorthogonal projective points,
choose signs of norm-two representatives so that

```text
(v,w)=1.
```

Their Gram determinant is

```text
2*2-1^2=0 mod 3.
```

Thus their span is degenerate; it must not be treated as an ordinary
nondegenerate codimension-two block.  Put `u=v+w`.  Then

```text
(u,u)=0,  (u,v)=(u,w)=0,
```

so `<u>` is the radical.

Nondegeneracy of the ambient form gives a vector `t` with `(u,t)=1`.
Adding a multiple of `v` makes `(v,t)=0` without changing `(u,t)`, and then
adding a multiple of `u` makes `(t,t)=0`.  Consequently

```text
W=H_hyp orthogonal-direct-sum <v> orthogonal-direct-sum K,
```

where `H_hyp=<u,t>` has determinant `-1=2`, `<v>` has determinant two,
and `K` has dimension `r-3`.  The product of the first two determinant
classes is one, so `K` retains the ambient class `epsilon`.

A vector orthogonal to both `v` and `w=u-v` has the unique form

```text
a u + k,  a in F_3, k in K.
```

Its norm is the norm of `k`.  For each norm-two projective point `[k]` in
`K`, normalizing the nonzero `K` component leaves exactly three choices of
`a`.  Therefore every nonadjacent pair has

```text
mu=3N_(r-3)^epsilon
```

common neighbors.

The same canonical decomposition proves nonadjacent-pair transitivity
without assuming a nondegenerate span.  Given another ordered pair, map
`u,t,v` to the corresponding vectors and extend by an isometry between the
two `K` spaces.  Since `w=u-v`, the ordered pair is mapped as required.

Thus the graph is strongly regular.  As an executable hostile control, the
independent checker verifies that replacing the singular complement by a
nondegenerate codimension-two count gives the wrong `mu`.  It also constructs
both graphs and checks every vertex pair in dimensions four through seven:
all degrees, adjacent common-neighbor counts, and nonadjacent common-neighbor
counts have exactly the claimed values.

## 4. Exact parameters and spectra

The direct `mu` formula satisfies the required two-path identity

```text
(v-k-1)mu=k(k-lambda-1)
```

in every audited case.  Since `mu>0`, each graph below is connected.  On the
orthogonal complement of the all-ones vector, the two adjacency eigenvalues
are the roots of

```text
x^2-(lambda-mu)x-(k-mu)=0.
```

The independent checker verifies the trace and trace-square equations,
including every multiplicity:

| `r` | class | `v` | `k` | `lambda` | `mu` | positive eigenvalue | negative eigenvalue | mixing bound |
|---:|:---:|---:|---:|---:|---:|---:|---:|---:|
| 7 | sq | 378 | 117 | 36 | 36 | `9^182` | `-9^195` | 75 |
| 7 | nsq | 351 | 126 | 45 | 45 | `9^168` | `-9^182` | 86 |
| 8 | sq | 1080 | 351 | 126 | 108 | `27^260` | `-9^819` | `963/10` |
| 8 | nsq | 1107 | 378 | 117 | 135 | `9^819` | `-27^287` | 86 |
| 9 | sq | 3240 | 1107 | 378 | 378 | `27^1599` | `-27^1640` | 104 |
| 9 | nsq | 3321 | 1080 | 351 | 351 | `27^1640` | `-27^1680` | `4110/41` |
| 10 | sq | 9882 | 3321 | 1080 | 1134 | `27^7380` | `-81^2501` | 104 |
| 10 | nsq | 9801 | 3240 | 1107 | 1053 | `81^2420` | `-27^7380` | `1710/11` |
| 11 | sq | 29646 | 9801 | 3240 | 3240 | `81^14762` | `-81^14883` | `9561/61` |
| 11 | nsq | 29403 | 9882 | 3321 | 3321 | `81^14640` | `-81^14762` | 158 |
| 12 | sq | 88452 | 29403 | 9882 | 9720 | `243^22022` | `-81^66429` | `4149/13` |
| 12 | nsq | 88695 | 29646 | 9801 | 9963 | `81^66429` | `-243^22265` | 158 |

Here `a^b` in an eigenvalue column means eigenvalue `a` with multiplicity
`b`; the principal eigenvalue is `k` with multiplicity one.

## 5. Exact mixing inequality and rank boundary

Let `A` be a `k`-regular graph on `v` vertices and let `theta` be the largest
eigenvalue on the all-ones orthogonal complement.  For a subset of size `m`
with characteristic vector

```text
x=(m/v)1+y,  y perpendicular to 1,
```

one has

```text
x^T A x
 = k m^2/v + y^T A y
 <= k m^2/v + theta(m-m^2/v).
```

Dividing by `m` bounds the induced average degree by

```text
d <= [k m + theta(v-m)]/v.
```

The endpoint subset has `m=231` and exact induced degree `d=162`.  Both
determinant classes in dimensions seven through eleven have upper bound
strictly below 162, as the table shows.  Dimensions at most six do not have
enough points.  Therefore

```text
rank_F3(M)>=12.
```

At rank twelve, the nonsquare class has upper bound 158 and is impossible.
The square class has upper bound `4149/13>162` and survives.

The independent checker also evaluates both determinant classes in every
dimension from 13 through 44.  All 64 cases survive; the smallest of their
bounds is

```text
116646/365 > 162
```

in the rank-13 nonsquare case.

## 6. Replay and boundary

The independent suite passed:

```text
Ran 12 tests
OK
```

The submitted suite passed:

```text
Ran 10 tests
OK
```

The submitted JSON regenerated byte-for-byte with SHA-256

```text
7d7c15ad99952ee3ca70582a887e771331156b8ef8e50524d296f1dc15f425a1.
```

| Obligation | Result |
|---|---:|
| Symmetric finite-field factorization | PASS |
| Projective point distinctness | PASS |
| Both determinant-class point counts | PASS |
| Vertex and adjacent-pair transitivity | PASS |
| Degenerate nonadjacent span | PASS |
| Three-lift formula for `mu` | PASS |
| Nonadjacent-pair transitivity | PASS |
| Strongly regular parameters | PASS |
| Eigenvalues and every multiplicity | PASS |
| Exact rational mixing bounds | PASS |
| `rank_F3(M)>=12` | VERIFIED |
| Nonsquare rank-twelve class | EXCLUDED |
| Square rank-twelve class | SURVIVES |
| Ranks 13 through 44 | SURVIVE THIS TEST |
| Endpoint matrix or graph | NOT CONSTRUCTED |
| Endpoint exclusion or upper-bound improvement | NOT OBTAINED |
| Novelty | NOT ASSESSED |

Final scoped status:

```text
conditional rank_F3(M)>=12: VERIFIED
rank 12 nonsquare determinant: EXCLUDED
rank 12 square determinant: SURVIVES
n3=4158 endpoint: survives
Conway-99: UNKNOWN
```
