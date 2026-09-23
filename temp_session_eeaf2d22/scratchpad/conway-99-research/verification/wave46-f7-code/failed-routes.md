# Retained null routes and corrections

## Ordinary code constraints

The 17 explicit `[231,r]_7` controls prove nonvacuity for every
`r=28,...,44`. They satisfy self-orthogonality, one-perp, projectivity, the
dual-distance lower bound, forbidden-weight congruences, and a much stronger
weight-69 lower bound.

They do not satisfy the six endpoint generator compositions and are not
projector matrices. Their success blocks only the generic ordinary-code
relaxation.

## Complete moments through degree two

All strength-two moments pass with strict slack. This is necessary but far
from sufficient: the compositions of almost all codewords remain
undetermined, and no nonnegative complete enumerator has been constructed.

The pre-discovery clean freeze reported raw diagonal moments `n_a^2`. The
frozen request uses the falling derivative moment `n_a(n_a-1)`. This was
corrected transparently after freeze:

```text
raw-basis minimum second slack:
498756830339225186256549252

falling-basis minimum second slack:
498756830339225186222981718
```

Both are strictly positive. No discovery claim changes, but the basis
distinction is retained to avoid presenting the first number as the requested
one.

## Weight congruences

Coordinate sum and squared norm zero exclude only weights `1,2,4`. They
permit all other weights as residue patterns, so they give no broad
divisibility theorem.

## Schur-cube rank

The full third Schur power gives `r7>=11`, whereas prior work already gives
`r7>=28`. The identity is exact structural information but not a stronger
rank bound.

## Prompt object mismatch

`A+3I` is a `99 x 99` invertible matrix over `F7`; `M=21E_0` is the
conditional `231 x 231` projector object. The former is verified only as a
hostile control and is never used in the endpoint argument.

## Nonpromotion wall

No concrete endpoint projector, complete enumerator, graph, endpoint
infeasibility certificate, strict upper-bound improvement, or novelty result
was produced. All such statuses remain `UNKNOWN`.
