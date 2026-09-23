# Wave 120 failed routes and surviving boundary

## Raw projector radius

The exact real affine minimum for doubled cycle coordinates is `112/5`.
Even after using integrality, treating this only as the next even norm
would give 24.  The four anchor eigen-equations sharpen it to 32, so the
raw-radius route leaves useful information on the table.

## Pairwise PSD / Gram

The norm-32 sum bound gives new inner-product lower bounds.  They are not
enough: the exact size-40 witness has a positive-definite residual Gram of
rank 40 and satisfies all resulting allowed inner products.  Hence no
two-point semidefinite or Delsarte argument using only those data can prove
the needed cap 25 or 24.

The `r`-fold generalization `||sum_i x_i||^2>=4r^2+8r` also does not cap
the family.  Every positive subset of the same witness satisfies it
directly; the full forty-point sum has squared norm 9,836 against a lower
requirement of 6,720.

## Binary minimum distance

Taking supports modulo two yields constant weight 16 and pair distance at
least 14 in the witness.  Thus the ordinary binary constant-weight
minimum-distance relaxation also admits 40 points.  This does not test
membership in one target kernel code, its dual-strength constraints, or
MacWilliams data for the full ambient code.

## Low-norm difference profiles

Whenever a witness difference has norm 14, 16, 18, or 20, it has the
required balanced signed-unit magnitude profile.  What is not encoded is
the induced signed support graph: four-regularity and the norm-18/20
same-sign-edge restrictions require one simultaneous unknown adjacency
matrix.  This is higher-order graph compatibility, not an inner-product
condition.

## Live route

The smallest credible continuation is a three-point or simultaneous
outside-adjacency formulation around the fixed cycle.  It should encode:

1. one common 95-vertex outside graph;
2. all selected support eigen-equations;
3. the target kernel code and its verified dual-strength constraints;
4. triple intersections, not only pairwise distances.

No local cap, rank exclusion, graph construction, or Conway-99 resolution
is obtained here.
