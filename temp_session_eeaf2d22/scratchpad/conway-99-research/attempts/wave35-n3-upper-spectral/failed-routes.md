# Wave 35 retained endpoint failures

All statements below are conditional on the frozen endpoint `n3=4158`.
None is evidence that the endpoint matrix or a Conway graph exists.

## Raw Schur and Krein positivity

At the endpoint there are no `M=-2` pairs.  Hence, entrywise,

```text
M o M o M = M + 60 I.
```

More generally every odd Schur power is `M+(4^k-4)I`, and every even
Schur power is `W+(4^k-16)I`, where `W=M o M`.  The cube is positive
definite, with eigenvalues `81^44,60^187`.  Thus the disappearance of
triangular-prism pairs makes this basic Schur test strictly feasible rather
than contradictory.

All forty previously accepted primitive-projector mixed Schur triples are
nonnegative at `n3=4158`.  Fifteen vanish for structural reasons and the
smallest positive value is `1/231`.

## Determinant and Smith form

Writing `S=M-4I` gives

```text
S^2 = 13S + 68I,
spec(S) = 17^44, (-4)^187.
```

The endpoint forces the exact Smith form

```text
SNF(S) = diag(1^44,4^143,68^44).
```

This is restrictive but internally consistent.  It supplies no forbidden
prime valuation or determinant residue.

The equivalent matrix

```text
C=2S-13I=2M-21I
```

has diagonal `-13`, off-diagonal entries in `{0,+2,-2}`, and satisfies
`C^2=441I`.  Its row norm is exactly `441` and its row sum is `-21`.
This integral orthogonal-reflection formulation also yields no contradiction
without new incidence information.

## Projector compression of the unsigned support

Let

```text
B=M o M-16I=S o S.
```

It is a 68-regular simple support graph.  Its exact traces against the four
`Gamma` eigenspace projectors are

```text
E_18:  68,
E_7:  -648/5,
E_0:  -44,
E_-3:  528/5.
```

Rank-wise Cauchy--Schwarz consumes only `126588/25` of
`tr(B^2)=15708`, leaving `266112/25` of Frobenius-square slack.  Therefore
these compression traces and ordinary interlacing do not exclude the
endpoint.

## Incidence-support Frobenius route

For a triangle `T`, entries of `B N^T` are:

- zero on the three points of `T`;
- two on the 36 points adjacent to `T`;
- `1+2t_x` on the 60 points nonadjacent to `T`, where `0<=t_x<=3` and
  `sum_x t_x=36`.

Consequently each row has squared norm between `492` and `780`.  The global
lower bound is `231*492=113652`.

Projector pinching gives only

```text
||B N^T||_F^2 >= 501732/5 = 100346.4.
```

The exact scalar allocation

```text
x_7=8208/5, x_0=44, x_-3=46992/5
```

meets every displayed trace/Cauchy constraint and attains `113652`.
It is only a scalar witness, not a matrix, but it blocks a contradiction from
these inequalities alone.

## Local incidence blocks

For adjacent original vertices, deleting their shared triangle leaves a
`6+6` cross-block that is the negative incidence of two disjoint perfect
matchings.  Their union is a 2-regular bipartite graph.  Its operator norm is
at most two, so the corresponding local Gram block has minimum eigenvalue at
least two for all cycle partitions

```text
C12, C8+C4, C6+C6, C4+C4+C4.
```

For nonadjacent original vertices, the checker contains an explicit `7x7`
matrix satisfying the forced two `-2` row sums, five `+1` row sums, the same
column sums, the two intersecting zero cells, and the two forced negative
cells.  It has only thirteen nonzero entries, so its operator norm is at most
`sqrt(13)<4`; the associated `14x14` Gram block is positive definite.

This control deliberately does not impose global compatibility or
`M^2=21M`.  It shows only that the immediate local row-sum and PSD attack
does not close.

## Exact remaining target

Because `rank(M)=44`, every `45x45` principal submatrix is singular.
Equivalently, every 45-index principal `S` submatrix has eigenvalue `-4`.

A sufficient endpoint contradiction would be a forced set of 45 triangle
indices with maximum internal absolute `S`-degree at most three.  Then
`4I+S[X]` would be strictly diagonally dominant and positive definite.
No such 45-set is proved here.
