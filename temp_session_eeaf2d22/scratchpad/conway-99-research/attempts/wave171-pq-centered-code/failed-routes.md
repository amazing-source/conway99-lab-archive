# Retained boundaries and failed shortcuts

## The `t<=6` classification is not an existence theorem

Makhnev--Nirova explicitly retain the `(99,14,1,2)` graph as one of the
possible slender partial-quadrangle collinearity graphs.  Citing the paper's
abstract alone as a classification-based construction or nonexistence proof
would be a source-scope error.

## The 5-vertex condition does not force 3-isoregularity

Pech's 5-vertex theorem is automatic for partial quadrangles.  The target's
triads have zero or one center in the forced nonuniform counts 70,686 and
27,720.  No theorem found here says that `P=0` makes those counts uniform.
Indeed Pech's Theorem 5.10 specializes to the strict, permitted inequality
`710>200`; its equality characterization cannot be invoked.

## The nilpotent code is not a new endpoint obstruction

For every putative target graph, `X+C=2J`, `X=2(C+J)`, and

```text
rank_F3(X)=rank_F3(C)-1.
```

Thus the code is exactly the already studied centered code, up to nonzero
scalar multiplication.  At the endpoint the difficult rank-12 reflection
branch becomes the centered `[231,11]_3` code.  Wave 54 has a formally
feasible ordinary weight enumerator for that branch.

## Constant zero supports are not automatically a 2-design

At `P=0`, the 231 zero supports of the rows of `X` all have size 33, and
symmetry gives point replication 33.  If they were a 2-design, its parameter
would have to be

```text
lambda=33*32/230=528/115,
```

which is not an integer.  This proves only that the supports are not a
2-design.  There is no reason they must be one, so the calculation is not a
contradiction.

## Ordinary Pless moments remain too weak

The existing centered-code enumerator already survives the ordinary
MacWilliams/Pless constraints.  Any coding-theoretic continuation must use
the 99 intrinsic weight-seven dual checks jointly with the 231 distinguished
weight-198 words, for example through harmonic or marked weight enumerators.
This is a proposed theorem lane, not a completed calculation.
