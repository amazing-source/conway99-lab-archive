# Wave53 exact cut-loop protocol

## Frozen scope

This discovery run starts at the independently verified Wave51 support-136
rational witness for the fixed 174-cut endpoint relaxation. It does not alter
or regenerate any Wave45--Wave52 input.

The bounded run adds exactly three cuts. At each of the four rational
witnesses it evaluates all available verified coefficient families:

- three Wave45 edge/nonedge/vertex matrices;
- eight Wave47 ordered three-root matrices; and
- twenty-one Wave49 five-root attachment matrices.

There is no assumed target-graph automorphism.

## Exactness boundary

Floating point has only two proposal roles:

1. HiGHS selects an active LP basis.
2. A symmetric eigensolver proposes a negative direction.

An LP point is retained only after rational active-row reconstruction and
exact substitution in all 170 Wave44 equations, all cumulative cuts,
nonnegativity, and the `2079 <= h11/4 <= 4158` bounds.

A matrix is called indefinite only when a primitive integer vector has
strictly negative exact rational quadratic value. If the numerical proposal
does not work, exact LDL either emits such a direction or an exact PSD
certificate.

## Cut construction

For an integer direction `v`, each lower-order matrix coefficient is pushed
to the order-seven variables through the exact deletion identity

`count(H) = sum_G count(G) * induced_H(G) / C(99-|H|, 7-|H|)`.

The resulting rational row is cleared of denominators and divided by its
integer gcd without changing sign. Its value at the source witness must equal
the same positive scale times `v^T M v`, and must be strictly negative.

Among nonduplicate directions, selection minimizes

`q / (||v||^2 * max(1, sum_i |M_ii|))`

exactly, with layer and family as deterministic tie-breakers.

## Resource rule

Every matrix and LP phase checks that strictly more than 20% of physical
memory is free. Live RAM percentages are deliberately not embedded in the
sealed mathematical result; only the threshold, check count, and pass status
are retained.

## Status wall

Discovery may label the bounded artifacts only `CANDIDATE` or `DERIVED`.
Rational aggregate feasibility is not integer feasibility, graph feasibility,
endpoint feasibility, a strict upper bound, or a solution of Conway-99.
