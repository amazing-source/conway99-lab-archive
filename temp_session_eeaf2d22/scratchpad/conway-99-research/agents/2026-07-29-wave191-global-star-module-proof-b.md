# Wave 191 proof B: the global star module

```yaml
role: proof_b
date_utc: 2026-07-29T02:49:53Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional rank-11 endpoint: impose all 99 point-star relations
  simultaneously through the modular point-triangle incidence module,
  derive the exact star-span and dependency-radical ranges, and determine
  the sharp rank-only boundary.
inputs:
  verification/wave170-block-profile-ternary-code/verification-report.md: 2913e74995d320978c913e9831b9dc9f4a2bd50df8f9a11396c2118264ec5a03
  verification/wave171-pq-centered-code/verification-report.md: 1f2ba5ed92ba6bb1ccc05cd753a8e359f208c3ddc7ca85766f26f8869346414f
  verification/wave175-polar-cap-boundary/audit.md: cefd905cc0339175f74353b7d8ebe94937944271c77c0ba80a02f8520145fb50
  verification/wave176-star-projector-circuits/audit.md: f58577409f39e98b06bfbe206221d3d278f0c473bcf5057afc381094d5e65d05
  attempts/wave189-degree7-star-complete/package-manifest.sha256: dce4157a05fc20f9b3965ec9830a08f893eeefacdb347b084af13807fa417c90
method: >-
  Modular representation decomposition of A+I, nondegenerate orthogonal
  subspace duality, radical dimensions, point-triangle line-sum colorings,
  and deterministic hyperbolic-space controls. No graph, code,
  configuration, SAT, LP, or isomorphism search.
command: python -B attempts/wave191-global-star-module-proof-b/exact_check.py
outputs:
  attempts/wave191-global-star-module-proof-b/exact_check.py: 86ebd6d7a058902c105091a8c64fd629c81033f1d0a8b735f06e0c26e7ca6336
limitations:
  - The abstract controls realize the modular quadratic-space constraints,
    not a point-triangle incidence matrix or graph.
  - No complete weight enumerator of the line-sum coloring code is derived.
  - No four-point projector trace tensor is classified.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

Imposing all 99 stars simultaneously gives a new exact global theorem.
If `B` is the `99 by 231` point-triangle incidence matrix, then at the
rank-11 endpoint

```text
66<=rank_F3(B)<=82.                               (1)
```

Equivalently, the 99 all-one star words span a code of dimension `66..82`
and have a simultaneous dependency code

```text
L=ker(B^T),
17<=dim(L)<=33.                                  (2)
```

More strongly, if `ell=dim(L)`, the standard dot product restricted to `L`
has

```text
rank(L)=2ell-34,
radical dimension=34-ell.                        (3)
```

The all-one point vector lies in this radical.

These constraints are absent from the one-star rational control of Wave
189.  They do not, however, exclude rank 11: deterministic abstract
quadratic-space controls realize every integer `ell` from 17 through 33.
The exact exposed continuation is therefore the triangle-line weight
enumerator or, equivalently at the projector level, the uncontracted
three/four-point trace tensor.

## 1. The fixed modular representation

Work over `F_3`.  Let `A` be the point adjacency matrix, let `J` be the
all-one matrix, and put

```text
G=B B^T=A+I.
```

The strongly regular identity and the row sum give

```text
G^2=G-J,
GJ=JG=0,
J^2=0.                                          (4)
```

Therefore

```text
E=G-J
```

is a symmetric idempotent.  The verified value `rank(G)=55`, together
with `G=E+J`, gives

```text
rank(E)=54,
im(G)=im(E) direct_sum <1>.                      (5)
```

Indeed `E1=0`, so the two images in (5) are disjoint.

Put

```text
K=ker(E).
```

Since `E` is a symmetric idempotent, `K=im(E)^perp` is a nondegenerate
45-dimensional orthogonal space.  The vector `1` belongs to `K` and is
singular because `1^T1=99=0`.

On the two summands,

```text
A=0 on im(E),
A=J-I on K.                                     (6)
```

The second operator is invertible because `J^2=0`.

## 2. Decomposing the simultaneous star image

Let

```text
U=im(B) subset F_3^99.
```

Since `im(BB^T)` lies in `im(B)`, equations (5) give

```text
im(E) direct_sum <1> subset U.
```

The idempotent `E` preserves this containment, so

```text
U=im(E) direct_sum U_0,
U_0=U intersect K.                               (7)
```

Write

```text
d=dim(U_0).
```

Then

```text
rank(B)=54+d.                                    (8)
```

Every column of `B` has three ones.  Hence

```text
U subset 1^perp.
```

In particular `U_0 subset 1^perp`, while `1 in U_0`.  Thus `1` is in the
radical of the standard form restricted to `U_0`.

## 3. Rank 11 becomes a subspace-radical equation

The centered Gram matrix has the verified factorization

```text
D=B^T A B
```

and endpoint rank

```text
rank(D)=11.
```

Pullback through the surjection from block coefficient space onto `U`
shows that `rank(D)` is the rank of the `A`-bilinear form restricted to
`U`.

The `im(E)` part contributes zero by (6).  On `U_0`, equation (6) and
`U_0 subset 1^perp` give

```text
A=-I.
```

Consequently the standard Gram form on `U_0` has

```text
rank=11,
radical dimension=d-11.                          (9)
```

The marked radical vector `1` makes the radical nonzero, so

```text
d>=12.                                           (10)
```

Because `K` is nondegenerate of dimension 45, the radical in (9) is
contained in `U_0^perp`, whose dimension is `45-d`.  Hence

```text
d-11<=45-d,
d<=28.                                           (11)
```

Equations (8), (10)--(11) prove (1).

## 4. The exact line-sum dependency law

A coefficient vector on the 99 stars is a dependency precisely when

```text
B^T f=0.
```

Thus

```text
L=ker(B^T)=U^perp.
```

Since `U` contains the nondegenerate summand `im(E)`, equations (7) imply

```text
L=U_0^perp inside K.                              (12)
```

Therefore

```text
ell=dim(L)=45-d=99-rank(B),
17<=ell<=33.                                     (13)
```

Nondegeneracy of `K` gives

```text
rad(L)
 =L intersect L^perp
 =U_0^perp intersect U_0
 =rad(U_0).
```

Using (9) and (13),

```text
dim rad(L)=d-11=34-ell,
rank of the form on L
 =ell-(34-ell)
 =2ell-34.                                       (14)
```

This proves (2)--(3).  The vector `1` belongs to both `U_0` and `L`, so it
is the distinguished radical line.

Combinatorially, `L` is the ternary triangle-line-sum coloring code:

```text
f_x+f_y+f_z=0
```

on every triangle block `{x,y,z}`.  Consequently every block has color
type

```text
000, 111, 222, or 012.                            (15)
```

This is the first genuinely simultaneous constraint on all 99 stars.

## 5. Sharp rank-only null controls

The checker constructs a nondegenerate 45-space as 22 hyperbolic planes
plus one anisotropic line.  It marks one isotropic vector as `1`.

For every

```text
12<=d<=28
```

it chooses:

1. the marked radical line;
2. a totally singular radical extension of dimension `d-12`; and
3. an orthogonal nondegenerate 11-space.

The resulting `U_0` has dimension `d`, Gram rank 11, and radical dimension
`d-11`.  Its orthogonal complement `L` has exactly the dimensions and
ranks in (13)--(14).  All seventeen cases pass exact modular row reduction.

These controls do not supply the 231 weight-three incidence columns of
`B`.  They prove the narrower and important null statement:

```text
the modular representation, rank, and radical equations alone
do not exclude any ell in 17..33.                 (16)
```

## 6. Next exposed invariant

The remaining graph-specific information is no longer a one-star moment.
It is the simultaneous realization of (15) by a code `L` satisfying
(13)--(14).

For a coloring `f in L`, let `n_i` count points of color `i`, and let `R`
count rainbow `012` triangle blocks.  If `m_i` counts monochromatic
`iii` blocks, point-triangle incidence gives

```text
7n_i=3m_i+R,  i=0,1,2.                            (17)
```

Thus the complete weight enumerator of `L`, together with joint
four-color/four-point refinements of (17), is the smallest exposed
invariant not present in the rational controls.

At the polar-projector level the same missing data is the symmetric cubic
trace tensor

```text
C_(x,y,z)=tr(P_x P_y P_z),
```

whose diagonal slices are the verified trace Gram
`C_(x,x,y)=tr(P_xP_y)` and whose contraction obeys

```text
sum_x C_(x,y,z)=0
```

because `sum_x P_x=0`.  Classifying this tensor, or the associated
four-point trace, would couple all stars beyond (14).

No rank-11 exclusion follows at this checkpoint.  Endpoint existence,
Conway-99, and external novelty remain `UNKNOWN`.
