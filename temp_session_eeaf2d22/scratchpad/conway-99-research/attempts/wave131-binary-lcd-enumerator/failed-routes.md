# Wave 131 failed routes and surviving boundary

## Ordinary rational MacWilliams infeasibility

This route is refuted as a relaxation.  The stored exact rational witness
has image distance 14, dual distance 15, all forced low-weight
coefficients, complement symmetry, and nonnegative coefficients through
all forward and inverse MacWilliams rows.

## Integral ordinary enumerator

The rational witness is not integral.  A hard-bounded full integral scout
ended `UNKNOWN_HARD_TIMEOUT`.  No integral formal enumerator and no
infeasibility certificate were found.  Timeout supplies no evidence.

## Treating LCD as an enumerator property

Ordinary weight coefficients do not certify
`C intersection C^perp={0}`.  LCD is imported for a hypothetical graph but
is not realized by the formal witness.

## Treating distinguished rows as arbitrary codewords

The 99 neighborhood rows have pairwise dot products equal to the unknown
adjacency entries.  The 99 closed-neighborhood dual rows have Gram `I+A`.
Merely requiring enough words at weights 14 and 15 discards these labelled
intersection matrices.

## Live continuation

The next code shift should use a joint/split enumerator or a finite
distinguished-row incidence system that retains:

1. 99 labelled weight-14 image words;
2. 99 labelled weight-15 dual words;
3. their two Gram matrices `A` and `I+A`;
4. mutual orthogonality;
5. the target degree and common-neighbor equations.

The current package does not solve this system.
