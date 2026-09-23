# Wave 110 failed routes and cautions

## Bounded MiniCard search

All four invariant `e(X0)` branches timed out after 45 seconds. Adding 50
row-lex comparisons did not change the solve status relative to Wave 105.
The result is `UNKNOWN`, not evidence for either extension or exclusion.

## Fixed labelled `X0` graph plus unrestricted row sorting

Wave 105 fixes one labeled representative for each three-vertex `X0`
isomorphism type. Imposing a full order on those same three labels afterward
is not automatically complete, because the fixed representative may leave
only a proper stabilizer. Wave 110 avoids this interaction by branching on
the label-invariant edge count and leaving the three individual edge
variables unfixed.

## Independent per-class sorting argument

Sorting one class can permute columns used when comparing another class.
Therefore a class-by-class verbal argument is insufficient. The derivation
uses one shared orbit potential whose minimizer satisfies every comparison
simultaneously.

## Solver exits without certificates

No SAT model or UNSAT answer was returned. Even if MiniCard had returned
UNSAT, the package would retain `UNKNOWN` without an independently replayed
proof trace. A SAT model would be accepted only after direct replay of the
99-vertex SRG matrix equation.
