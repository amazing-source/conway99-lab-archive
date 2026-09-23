# Attacked gaps that did not refute Wave203

## Candidate-set mismatch

Forward leaf blocks lie in `C_y(x)`, but their images and reverse leaf
blocks both lie in `C_x(y)`. The capacity argument compares image slots
with reverse domains, so no unproved bijection between the two candidate
sets is required.

## Relative scaling

Both canonical relations are normalized by their own leaf coefficient.
That fixes their projective scalars and leaves the matched other-leaf
coefficient equal to two, so addition is legitimate.

## Full versus selected multiplicity

The slot theorem is proved for the full flag pool. Selected circuits are
a subset and cannot use both companions of one flag in a minimal cover,
so selected multiplicity cannot exceed full occupied slots.

## Bound inflation

The theorem proves `epsilon>=5b` but no existing row forces `b>0`.
Therefore no strict improvement beyond the conditional 7,059 checkpoint
is claimed.
