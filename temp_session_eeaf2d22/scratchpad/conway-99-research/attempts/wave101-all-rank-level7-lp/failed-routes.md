# Retained null outcomes and failed routes

## Scalar positivity does not reach the signed-unit range

For every `q=2,4,...,14`, the exact first-15-coefficient level-7 scalar cone
has a feasible integral, even, nonnegative point with

```text
x7=x8=x9=0.
```

Thus this LP cannot by itself force a norm-14, norm-16, or norm-18 vector.
Those are the only norms for which the Wave 71 graph-specific signed-unit
dictionary is proved.

## Direct mod-7 rounding gives no extra total bound

Each reported objective was evaluated on the full Wave 71 affine solution
space modulo seven. Every objective varies in at least one affine direction,
so there is no fixed residue to combine with parity. A joint coefficientwise
integer/congruence program remains untested.

## Elementary lattice upper bounds do not collide

The best elementary comparison used here is

```text
|S_26| <= 2(2^44-1),
|S_28| <= 88(2^44-1).
```

All exact lower bounds remain far below these values. The scalar results do
not exclude any row.

## Rational modular controls are not realizations

Matching primal LP points prove optimality in the formal coefficient cone.
They do not prove the existence of a lattice, a discriminant form, the
marked 99-vector frame, or a graph. Conversely, failure to find a
realization would not be a nonexistence proof without a complete certified
search.
