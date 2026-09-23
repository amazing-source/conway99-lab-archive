# Bounded routes attempted before the complete census

These searches were diagnostics used to choose the Wave153 projection. None
produced a proof or counterexample, and heuristic non-discovery is not
evidence of nonexistence.

## Pigeonhole correlation inequalities

For all 1,140 component triples, a bounded search over seven-row independent
supports tested the elementary correlation inequalities induced by six-set
occupancy. No violation was found.

Status: **null diagnostic**. The searched inequality family was restricted.

## Consecutive-integer variance inequalities

For subset sizes 7 through 18, indicator subsets were scored against the 275
safe representatives using the integer-variance lower bound on a column's
intersection size. Some inequalities were tight; none was violated.

Status: **null diagnostic**. The subset family was heuristic rather than
exhaustive over all row subsets.

## Component-local ternary hypermetrics

For every one of the 18 component types, all coefficient vectors in
`{-1,0,1}^12` supported inside that component were tested against the local
pair data. No negative correlation/hypermetric value occurred; only tight
zeros appeared.

Status: **exact for this local coefficient box**, but it does not cover global
36-coordinate inequalities or larger coefficients.

## Global ternary local search

Bounded local searches over global ternary coefficient vectors, including the
sum-one hypermetric normalization, found no negative candidate.

Status: **heuristic null result**.

## Small unrestricted correlation LPs

Random 10- and 12-row local correlation-polytope LP projections, plus 10-row
component/fibre-profile variants, were feasible in the sampled trials.

Status: **heuristic null result**. Neither the row subsets nor the local
polytope descriptions formed a complete global certificate.

## Why the final lane was retained

The complete 275-orbit bounded rational column census dominates these
pair-coordinate diagnostics in the exact fixed-triangle model: it uses all
630 pair coordinates, every allowed column, and the explicit upper bounds
`x_s <= 1`. Its exact feasibility therefore closes a concrete finite
relaxation, while the diagnostics above only record paths not worth repeating
in the same bounded form.

