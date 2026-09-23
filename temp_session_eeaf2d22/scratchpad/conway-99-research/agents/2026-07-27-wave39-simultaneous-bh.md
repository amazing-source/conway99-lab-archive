# Wave 39 proof A: simultaneous B/H and centered equality boundary

```yaml
role: proof_a
date_utc: 2026-07-27T02:22:33Z
git_commit: 019b78ac9a5170107d105ad4d8fcd27f55dde642
claim_label: DERIVED
scope: >
  Conditional prism-free endpoint n3=4158: exact simultaneous B/H
  overlap and edge decomposition, and the centered characteristic-three
  rank-twelve equality case.
inputs:
  attempts/wave39-simultaneous-bh/input-freeze.sha256: 54d3e703b113159a4b52d58b46e2efca5ae7564027b431d00510d2277c650939
method: >
  Integral reflection row arithmetic; finite-field centering;
  coordinate-DP reconstruction of the oriented isotropic association
  scheme; ternary code support recovery; and exact XX/XY/YY block counting.
command: |
  .\.venv\Scripts\python.exe -B attempts\wave39-simultaneous-bh\exact_check.py --verify attempts\wave39-simultaneous-bh\exact-results.json
  .\.venv\Scripts\python.exe -B -m unittest -v attempts\wave39-simultaneous-bh\test_exact_check.py
outputs:
  attempts/wave39-simultaneous-bh/exact-results.json: 1aab10ae2bf080d682a22d6c1e66a29f001ab2a889dc6b190b67fe0a0e0ad77d
  attempts/wave39-simultaneous-bh/package-manifest.sha256: 0ff05f1409d54e0aa38c6be6e086f02352911d5eb50f6bff9bd4b5bc6240b20b
limitations:
  - Discovery cannot verify itself; independent reconstruction is required.
  - Every oriented-scheme transform is positive, so rank twelve survives this test.
  - The B/H decomposition assumes a full simultaneous completion and does not construct one.
  - The frozen rank-ten core is a local relaxation, not an endpoint graph.
  - No endpoint exclusion, improved upper bound, construction, or novelty claim is made.
```

## Result

The prism-free endpoint is not excluded.  This lane adds two exact packages
that use information absent from the Wave 38 individual-column relaxation:

1. the surviving ternary equality case has a projective centered
   interpretation with strong code constraints; and
2. every full simultaneous `(B,H)` completion has a rigid edge
   decomposition into 32 edge-disjoint triangles and 36 point-labeled
   matchings.

The strongest justified status remains

```text
rank-twelve centered restrictions:       DERIVED
simultaneous B/H edge decomposition:      DERIVED
simultaneous 60-column B:                 UNKNOWN
compatible H:                             UNKNOWN
n3=4158 and Conway-99:                    UNKNOWN
upper bound on n3:                        4158
```

## 1. Centered rows at the rank-twelve boundary

Assume the surviving equality case

```text
r3=rank_F3(C)=12
```

with square determinant class.  The independently verified Wave 38
centering gives

```text
C=V H V^T,
(v_T,w)=2,
(w,w)=2,
z_T=v_T-w,
D=C+J=Z H_0 Z^T,
rank_F3(D)=11.
```

Every `z_T` is isotropic, and the restriction `H_0` to `w`-orthogonal is
nonsquare: in the orthogonal direct sum

```text
H = [2] orthogonal_sum H_0,
```

the full determinant is square, so `det(H_0)` is nonsquare.

### Equality is impossible

If `z_i=z_j`, then rows `D_i,D_j` agree modulo three.  The distinct
off-diagonal integer residues force

```text
C_i-C_j=-15(e_i-e_j).
```

The displayed vector has squared norm `450`, whereas `C^2=441I` makes
distinct integer rows orthogonal with squared norm `441`, so their
difference has squared norm `882`.

### Antipodality is also impossible

Suppose `z_i=-z_j`.  Looking at columns `i,j` first forces

```text
C_ij=+2.
```

At each of the other 229 coordinates, the integer pair must then be one of

```text
(+2,+2), (-2,0), (0,-2).
```

Let `a` count the first type.  Since both rows sum to `-21`,

```text
-22 + 4a - 2(229-a) = -42,
a=73.
```

Thus the integer row sum would have norm

```text
2*11^2 + 73*4^2 + 156*2^2 = 2034.
```

Orthogonality of the two distinct rows instead requires `882`.  This is a
contradiction.  A zero centered row is also impossible because it would
require all 230 off-diagonal entries of its `C` row to be `+2`, rather than
the exact 32.

Consequently the 231 centered rows give 231 distinct isotropic projective
points in the nonsquare eleven-space.

## 2. Exact oriented isotropic scheme

The centered row distribution is

```text
relation: equal antipodal inner0 inner1 inner2
count:      1      0       32    162     36.
```

The standard-library checker reconstructs the full scheme using the
diagonal form

```text
diag(1,1,1,1,1,1,1,1,1,1,2)
```

and coordinate dynamic programming.  Its valencies are

```text
1, 1, 19680, 19683, 19683.
```

An exact first eigenmatrix is

```text
[1,  1, 19680, 19683,  19683]
[1,  1,  -164,    81,     81]
[1, -1,     0,   -81,     81]
[1,  1,   160,   -81,    -81]
[1, -1,     0,   243,   -243].
```

Every multiplication character is checked against every reconstructed
intersection number.  The endpoint Delsarte transforms are

```text
231, 209/135, 13/27, 493/1107, 23/9.
```

All are positive.  This exact two-point polar test therefore does not
exclude `r3=12`.

## 3. The centered ternary code

Since the uncentered frame has

```text
V^T V=0,  V^T 1=0,
```

and `231=0 mod 3`, centering preserves

```text
Z^T Z=0,  Z^T 1=0.
```

The vertex-star relations give

```text
N Z=0.
```

Thus

```text
W=col(Z)
```

is a projective self-orthogonal ternary `[231,11]` code.  Each column of
`D` is a codeword with complete weight

```text
(n1,n2)=(162,36), weight=198.
```

Projective distinctness of the centered rows gives 231 projective such
words, hence

```text
A_198 >= 462.
```

The 99 vertex-star incidence rows lie in `W`-dual and have weight seven.
Their sums and differences give additional exact lower bounds:

```text
B_7  >=   198,
B_12 >=  1386,
B_13 >=  1386,
B_14 >= 16632.
```

For adjacent original vertices, the two stars meet in their unique edge
triangle, so their difference has weight 12 and their sum weight 13.  For
nonadjacent vertices, the stars are disjoint, so both sums and differences
have weight 14.  The sign supports recover the original one or two star
centers; hence the displayed words do not collapse beyond their explicit
sign pairing.

These are necessary code constraints, not an enumerator or nonexistence
proof.

## 4. Exact simultaneous B/H overlap census

Fix a base triangle and retain

```text
|X|=36, |Y|=60,
BB^T       = 12I-A_X+2J-RR^T-A_X^2,
BH         = (J/3-I-A_X)B,
B^T B+H^2 = 12I-H+2J.
```

Let `c4=C4(A_X)`.  The off-diagonal entries of `G=BB^T` are zero, one,
or two.  There are:

```text
18+2c4 entries 0,
324-4c4 entries 1,
288+2c4 entries 2
```

among unordered row pairs.  The first term consists of the 18 forbidden
within-fibre matching edges plus the two opposite pairs of every core
four-cycle.

Two distinct columns of `B` meet in at most two points.  Double counting
row-pair concurrences and point incidences therefore forces the unordered
column-pair overlap census

```text
overlap 0: 438+2c4,
overlap 1: 1044-4c4,
overlap 2: 288+2c4.                         (1)
```

## 5. The compatible H is a triangle/matching overlay

For one block `b_y`, put

```text
e_y=number of A_X edges induced by b_y,
d_y=2*1-(I+A_X)b_y=B h_y.
```

Then

```text
b_y^T d_y=6-2e_y.
```

Every one of the 36 cross-fibre edges of `A_X` lies in exactly one block,
so

```text
sum_y e_y=36.
```

Summing the previous identity over `y` gives

```text
sum_(oriented H edges yz) |b_y intersect b_z| = 288.
```

The `YY` equation bounds an adjacent block overlap by one.  Since `H` has
240 edges, exactly

```text
144 H edges have overlap one,
 96 H edges have overlap zero.                    (2)
```

For distinct `y,z`, the same equation is pointwise

```text
common_H(y,z)=1-|b_y intersect b_z|  if yz is an edge,
common_H(y,z)=2-|b_y intersect b_z|  otherwise.    (3)
```

Equations (2)--(3) have a strong structural interpretation:

- every overlap-zero edge lies in exactly one `H` triangle;
- every overlap-one edge lies in no `H` triangle;
- the 96 overlap-zero edges are exactly the edge-disjoint union of the 32
  triangles of `H`;
- a vertex `y` belongs to `1+e_y` of those triangles; and
- for each `x in X`, the ten blocks containing `x` induce a four-edge
  matching in `H`.  These 36 labeled matchings partition the 144
  overlap-one edges.

Thus a compatible `H` is not an arbitrary 8-regular graph with the right
spectrum.  It is the overlay of a 32-triangle linear hypergraph and 36
point-labeled four-edge matchings, tied to the exact blocks.

## 6. Frozen rank-ten positive control

The Wave 38 rank-ten core has

```text
C4(A_X)=4.
```

If it admitted a full completion, (1)--(3) would force

```text
block-pair overlaps 0/1/2:       446 / 1028 / 296,
H-edge overlaps 0/1:              96 / 144,
H-nonedge overlaps 0/1/2:        350 / 884 / 296,
triangles(H):                      32,
four-cycles(H):                   175.
```

The last value reproduces the verified spectral identity

```text
C4(H)=171+C4(A_X).
```

All counts are nonnegative.  They neither construct nor exclude the
sixty-column design.

## Boundary

The next exact finite model should incorporate simultaneously:

1. the Gram and overlap census of `B`;
2. 96 overlap-zero pairs partitioned into 32 triples;
3. 144 overlap-one pairs partitioned into 36 labeled matchings;
4. the per-column triangle degree `1+e_y`; and
5. the full mixed and `YY` equations.

On the ternary side, any improvement over this lane must use the 99
distinguished dependent seven-cliques or a higher-point/code-integrality
constraint; ordinary oriented-scheme positivity has positive slack.

The focused suite reports:

```text
Ran 10 tests
OK
```

No independent verification has yet been performed, no novelty is claimed,
and the general upper bound remains `n3<=4158`.
