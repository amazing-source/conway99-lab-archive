# Boundary and failed shortcuts

## Projector traces are not intersection dimensions

The operators `P_x` are self-adjoint idempotents, but different star
projectors are not known to commute.  Therefore

```text
tr(P_x P_y)
```

cannot be replaced by `dim(E_x intersect E_y)` without an additional
argument.  All rank claims here use only the trace Gram in the
65-dimensional trace-zero symmetric square.

## Integer averages do not fix ternary rank

For each vertex, the 84 nonedge entries of `BLB^T` sum to 588 and average
7.  This does not fix their residues modulo three.  No rank lower bound
above 65 follows from the row sum alone.

## Gram nullity need not equal relation nullity

For a degenerate restriction, the kernel of a column Gram matrix can be
larger than the actual coefficient-relation space.  The exact cross-coset
weights are therefore promoted only for cycle types `6` and `4+2`, where
the radical inequality forces the span rank to equal the Gram rank 10.
For types `3+3` and `2+2+2`, only the rigorous dimension lower bounds are
claimed.

## Pairwise circuits are not yet globally incompatible

Every vertex pair forces a cross-star relation, and type `4+2` forces a
weight-four relation.  The present argument does not determine how these
relations overlap over all 99 stars.  A useful continuation is either:

1. classify the weight-four and weight-eight relations against the three
   centered Gram relations; or
2. obtain a structural lower bound for `rank_F3(BLB^T)` from its zero
   pattern and the nonedge residues.

Neither continuation should be reported as an endpoint exclusion before
independent verification.
