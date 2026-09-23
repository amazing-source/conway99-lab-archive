# Boundary and failed continuations

## The new count is not a Hamming-bound contradiction

The dual is a ternary `[231,220,>=4]` code.  Its radius-one Hamming bound
only compares `463` with `3^11=177147`; the new 693 projective short
circuits leave enormous slack.

## Circuit elimination is too weak by itself

The chosen circuits contribute between 2,772 and 5,544 support incidences,
so averaging gives repeated coordinates.  Eliminating a shared coordinate
between two size-at-most-eight circuits can still leave support as large as
14.  That does not contradict dual distance four.  No favorable overlap or
coefficient alignment is forced by the present count alone.

## Critical exponent is on the wrong code side

The available short words lie in `W^perp`.  Critical-exponent results for
the column matroid require a full-coordinate-support subcode of `W` (or
equivalent flat-lattice data), which is not supplied here.

## Subspace-EKR and sunflower hypotheses fail

The 99 star subspaces are six-spaces in an 11-space, so pairwise
intersection is automatic.  Only graph edges carry the stronger
cycle-dependent data, and their intersection dimensions are not constant.
Known pairwise-intersecting or equidistant-family theorems therefore do not
accept the present hypotheses.

## Projector rank still lacks entry control

Wave 176 gives a `99 x 99` trace Gram matrix of rank at most 65.  Its edge
entries vanish modulo three, but the nonedge entries are not fixed.  The
new circuit injection does not yet provide a rank lower bound exceeding 65.
