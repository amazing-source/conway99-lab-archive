# Wave 32 rooted-vector retained failures and boundaries

## The reduction does not exclude the rooted branch

Actual incidence reduces every norm-two root image to the single pattern

```text
(+1)^21, 0^189, (-1)^21.
```

That pattern survives.  The checker builds a 99-vertex partial local control
whose signed 14-vertex support is the complement of the Fano incidence
graph, saturates all 14 support degrees, and gives every pair of support
vertices its exact `lambda=1` or `mu=2` number of common neighbors.  The
outside-only graph is deliberately absent.  This is evidence that the
displayed local equations are consistent, not a graph construction.

## Matrix-only extreme fibers stop at 16 patterns

Without the actual vertex-triangle transport, a coordinate `|y_i|=2`
produces an orthogonal root

```text
u_i=sign(y_i)x_i-r.
```

Same-sign fibers have pairwise products in `{-2,-1}` and size at most
three.  This reduces the verified Wave 28 count from 32 to 16, but does not
select the final hostile pattern.  The stronger 16-to-1 step uses
`M Z^231=21L*`, the exact identity for `NM`, and the target values
`lambda=1, mu=2`.

## A same-sign triple is not itself contradictory

Three same-sign extreme roots have the `A2` Gram, sum to zero, and make the
three frame products equal to one.  Every opposite-sign extreme root is
orthogonal to that `A2` triple in the transformed root coordinates, so all
three corresponding frame products are `-2`.  These relations are exact,
but a local triangle-incidence count alone did not turn them into a
contradiction.  Actual incidence instead eliminates all extreme coordinates
through the vertex-vector reduction.

## Root reflection is not a graph automorphism

The root reflection sends

```text
x_i -> x_i-y_i r
```

and induces `I-yy^T/21` on the 231-coordinate projector space.  It preserves
the Gram matrix because it is a change of frame factorization.  It need not
permute triangle coordinates or preserve the selected rows individually.
No orbit closure, graph automorphism, or extra row was inferred from it.

## Schur and A4 bounds remain nonempty

For the surviving pattern, both the first and double root contractions of
the harmonic cubic have exact positive norm bounds.  The double-contraction
norm remains one of

```text
6,14,22,30,38,46,54,62,70,78,
```

and the first-contraction norm remains one of the positive integers at most
78 congruent to two modulo four.  These lists are nonempty.  The identity
`y^T A4 y=441 y^T W y` therefore gives no contradiction.

## The partial Fano control is not extendibility evidence

The control leaves 85 outside vertices needing their remaining degrees and
all outside-only adjacency, common-neighbor, triangle, projector, and Schur
constraints.  It neither proves nor numerically suggests that an extension
exists.  Conversely, failure of a future bounded extension search would not
prove nonexistence without a complete checked certificate.

The first frozen discovery JSON misstated those remaining degrees as
`8,12,14`.  Independent reconstruction found current outside degrees
`4^42,2^28,0^15`, so the correct remaining degrees are `10^42,12^28,14^15`.
That metadata failure and its exact original hashes are retained in
`correction-ledger.md`; it does not affect the support theorem or triangle
census.

## Status wall

No automorphism, catalog classification, floating-point solver, or
failure-to-find inference is used.  Rooted endpoint existence, `n3=708`,
Conway-99 existence/nonexistence, and novelty remain `UNKNOWN`.
