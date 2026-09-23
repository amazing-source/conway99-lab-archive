# Independent Wave 65 verifier audit

## Verdict

**VERIFIED**, strictly within the discovery package's stated scope.

The rooted-scaffold identity, hypergraph Gram identities, block-graph local
structure, trace and four-cycle formulas, scalar spectral coupling, all 43
scaffold-averaged PSD parameters, and the explicitly local positive control
were reproduced without importing or executing discovery code. There were
zero mathematical mismatches.

This does **not** verify an endpoint graph. It verifies a collection of exact
necessary consequences and null results. The endpoint `n3=4158`, Conway-99,
strict improvement of the general upper bound, novelty, and priority remain
`UNKNOWN`.

One verifier-procedure limitation is recorded: the first preinspection
inventory used `rg --files` without hidden files and therefore omitted
`.gitattributes`. The later independent manifest audit checked that file and
all ten other sealed local artifacts, but the initial freeze was not a
complete hidden-file freeze.

## Independence and input handling

- Discovery code was read only after the visible package inventory and hashes
  were frozen.
- Discovery code was never imported or executed.
- `independent_verify.py` rebuilds every checked object from definitions.
- The explicit JSON certificate is treated as untrusted data.
- Exact integer matrix products stay far below signed 64-bit range.
- Every rational calculation uses `fractions.Fraction`.
- The discovery manifest was parsed by independent code. Eleven entries
  matched byte-for-byte, including `.gitattributes`; local coverage equals all
  package files other than the self-excluded manifest.

## 1. Rooted scaffold and block identity

Fix a root in a hypothetical `srg(99,14,1,2)`. Its 14 neighbors induce the
matching `7K2`, because two adjacent vertices have exactly one common
neighbor and that common neighbor is the root. Each of the 84 remaining
vertices has exactly two root-neighbors, which form a non-matching edge of

```text
H = K14 - 7K2.
```

Thus residual labels are the 84 edges of `H`. Let `N` be the 14-by-84
endpoint-incidence matrix and let `Q` be the line graph of `H`. Independent
reconstruction gives

```text
N^T N = 2I + Q,
degree(Q) = 22,
spectrum(Q) = 22^1, 10^7, 8^6, (-2)^70.
```

The residual-residual block of the strongly regular graph equation

```text
A^2 = 12I - A + 2J
```

is

```text
N^T N + B^2 = 12I - B + 2J.
```

Substituting the incidence Gram gives exactly

```text
B^2 + B = 10I + 2J - Q.
```

The right side has row sum 156, agreeing with `12^2+12`.

## 2. Hypergraph orientation, local structure, and spectrum

At the frozen prism-free endpoint decomposition, the 420 edges of `D` are
140 edge-disjoint triangles. Their point/block incidence matrix has shape
84-by-140, row sum 5, column sum 3, and no repeated point pair. Therefore

```text
D + 5I = Z Z^T.
```

The orientation matters: the block-intersection graph is

```text
R = Z^T Z - 3I
```

on 140 vertices. It is 12-regular. The endpoint local condition excludes
Berge triangles outside the 140 point-star triangles, so each block's
neighbors split according to its three points into `3K4`.

Since `R+3I=Z^T Z` is positive semidefinite,

```text
lambda_min(R) >= -3.
```

Also `rank(Z)<=84`, so the kernel of `Z` in the 140-dimensional block space
has dimension at least `140-84=56`. Hence the multiplicity of the eigenvalue
`-3` of `R` is at least 56. The inequality direction and the 84-by-140
orientation were explicitly attacked and are correct.

## 3. Trace and four-cycle identities

For a simple `k`-regular graph on `n` vertices,

```text
tr(A^4) = nk(2k-1) + 8 c4(A),
```

where `c4` counts ordinary (not necessarily induced) four-cycles.

For `R`, the local graph `3K4` has 18 edges, so `R` has
`140*18/3=840` triangles. Therefore

```text
tr(R)   = 0,
tr(R^2) = 1680,
tr(R^3) = 5040,
tr(R^4) = 38640 + 8 c4(R).
```

The positive-power traces of `ZZ^T` and `Z^TZ` agree. Expanding
`(R+3I)^m` gives

```text
tr(D+5I)   = 420,
tr((D+5I)^2) = 2940,
tr((D+5I)^3) = 23940,
tr((D+5I)^4) = 201180 + 8 c4(R).
```

Independently expanding `(D+5I)^4`, using the 10-regular point graph with
140 triangles, gives `211260+8c4(D)`. Equating the two orientations yields

```text
c4(R) = 1260 + c4(D).
```

The target `B` spectrum gives `c4(B)=1071`. Since `D` is a subgraph of `B`,
every four-cycle of `D` remains a four-cycle of `B`, even if it gains chords.
Thus

```text
1260 <= c4(R) <= 1260+1071 = 2331.
```

The interval is nonempty and is not an exclusion.

## 4. Target B and generic transition moments

The frozen target spectrum

```text
12^1, 3^40, 0^7, (-2)^6, (-4)^30
```

independently gives

```text
tr(B^1..B^6) = 0, 1008, 840, 31752, 227640, 3138408.
```

For a triangle-free 2-factor `T`, closed-walk counting gives

```text
tr(T)   = 0,
tr(T^2) = 168,
tr(T^3) = 0,
tr(T^4) = 504 + 8 c4(T),
tr(T^5) = 10 c5(T),
tr(T^6) = 1680 + 48 c4(T) + 12 c6(T).
```

The verifier brute-checked these identities on every single cycle length
from 4 through 84; additivity over components proves the 2-factor formula.

## 5. Scalar spectral coupling

Write `a_lambda=tr(T E_lambda)` for the target `B` spectral projectors and
`w=a_3`. The exact mixed traces are

```text
sum a_lambda = tr(T) = 0,
sum lambda a_lambda = tr(BT) = 168,
sum lambda^2 a_lambda = tr(B^2T) = 0,
a_12 = 2.
```

The factor of two in `tr(BT)=168` was checked: `T` has 84 undirected edges.
For a `T` edge, the two labels already share the unique common root-neighbor;
the SRG `lambda=1` condition leaves no residual common neighbor, so its
entry of `B^2` is zero. Finally `E_12=J/84` and `T` is 2-regular, giving
`a_12=2`.

Solving over the rationals gives

```text
a_-4 = -(15/8)w,
a_-2 = (21/4)w - 72,
a_0  = 70 - (35/8)w,
a_3  = w,
a_12 = 2.
```

Because a 2-factor adjacency satisfies `-2I <= T <= 2I`, each projector
compression obeys `-2 rank(E_lambda) <= a_lambda <= 2 rank(E_lambda)`.
Intersecting the five intervals gives exactly

```text
64/5 <= w <= 16.
```

Consequently

```text
tr(B^3T) = 4032 + 105w,        5376 <= tr(B^3T) <= 5712,
tr(B^4T) = 40320 - 315w,
tr(B^4T) + 3 tr(B^3T) = 52416.
```

The scalar assignment `w=14` passes every compression trace inequality. It
is only a scalar relaxation and does not provide compatible matrices.

## 6. All 43 scaffold-averaged PSD lanes

The verifier independently constructed the six pair relations on signed
edges of `K7`. A generic integer combination was diagonalized only to
propose its six integer eigenvalues. Their exact minimal polynomial was then
checked by integer matrix multiplication, and exact polynomial projectors
recovered this joint eigenmatrix:

| multiplicity | relation eigenvalues |
|---:|:---|
| 1 | `1, 2, 1, 20, 20, 40` |
| 6 | `1, 2, 1, 6, 6, -16` |
| 7 | `1, 0, -1, 10, -10, 0` |
| 14 | `1, 2, 1, -4, -4, 4` |
| 21 | `1, -2, 1, 0, 0, 0` |
| 35 | `1, 0, -1, -2, 2, 0` |

For each integer `y=0,...,42`, the verifier formed the group average from
the exact undirected relation-edge counts

```text
0, 0, y, 84, 84-2y, 336+y
```

and subtracted the transition average `(1/10)A_3` from `B` before adding
`5I`. All `43*6=258` exact rational eigenvalue lanes are nonnegative. The
global minimum is `12/5`.

No target automorphism is assumed here. The scaffold group is used only to
average the universally positive semidefinite matrix `D+5I`; averaging a
PSD matrix preserves PSD. This route is necessary only and remains feasible.

## 7. Explicit positive control

The JSON certificate independently reconstructs:

- a linear 3-uniform, 5-regular hypergraph on 84 points and 140 blocks;
- no Berge triangle outside a certificate block;
- `D+5I=ZZ^T`;
- a 12-regular block graph `R` with every local graph exactly `3K4`;
- a Hamiltonian transition 2-factor `T`, edge-disjoint from `D`;
- a 12-regular sum `B=D+T` with every local graph `5K2` plus two isolates.

Its canonical certificate SHA-256 is
`383f2ce6c88fb227b98473633479204968e72f00d8127affea33fb13f191430d`.
The verifier also reproduced

```text
c4(D)=666, c4(R)=1926,
rank_2,3,5,7(Z)=84,83,84,84,
tr(B^1..B^6)=0,1008,840,37248,215620,3378180.
```

Subtracting the target moments gives exactly

```text
0, 0, 0, +5496, -12020, +239772.
```

The first failure is degree four. The certificate is therefore a positive
control for the deliberately weaker unlabelled local relaxation, not a
rooted-scaffold witness and not a residual-graph candidate.

## 8. Remaining obstruction

Every verified route here is scalar, averaged, spectral, or locally
unlabelled. The unresolved layer is the simultaneous, entrywise placement
of `Z` and `T` relative to the fixed line graph `Q`, including

```text
(T+D)^2 + (T+D) = 10I + 2J - Q.
```

That noncommutative two-root compatibility is not encoded by the surviving
relaxations. No endpoint conclusion follows.
