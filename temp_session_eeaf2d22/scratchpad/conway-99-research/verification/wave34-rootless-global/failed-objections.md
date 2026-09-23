# Wave 34 Stage 2 adversarial objections

This file retains attempted refutations and scope attacks so they are not
mistaken for new proof routes later.

## 1. Cross-fibre maps might fail to be bijections

Attempt: challenge Lemma 1 by allowing a vertex of `Xi` to have zero or
multiple partners in `Xj`.

Outcome: failed. The pair `(x,tj)` is nonadjacent and has exactly
`mu=2` common neighbours. One is `ti`; the other is unique and lies in
`Xj`. Reversing `i,j` gives the inverse map.

## 2. The degree formulas might silently assume constant q

Attempt: look for transitivity or a constant-`q` step in the endpoint count.

Outcome: failed. All four degrees are pointwise in `q(T)`. Only the global
identity `3 sum_T q(T)=2|E(R2)|` is used. The candidate does not assume
constant `q`.

Retained qualifier: `q=1` is algebraically accepted by the displayed formulas
but cannot occur for a permutation. Stage 1 already records `q(T)!=1`.

## 3. The mixed trace might count one motif rather than two

Attempt: remove one orientation of the `R2` adjacency matrix.

Outcome: the hostile trace drops from `2` to `1`. This confirms, rather than
refutes, the candidate's factor of two for symmetric adjacency matrices.

## 4. Triple overlaps might be confused with forbidden double overlaps

Attempt: test whether a fixed pair occurring in all three transported
matchings was included in the forbidden motif count.

Outcome: failed. Multiplicity two gives relation `R2`; multiplicity three
gives relation `R3`. The candidate separates them correctly.

## 5. The projector kernel might allow two distinct completions

Attempt: observe that the Gram kernel identifies a vector but does not by
itself prove triangle-row injectivity.

Outcome: failed after adding the missing hostile check. The diagonal marked
row entry is `4`; every distinct disjoint entry is at most `1`, every
one-vertex-overlap entry is at most `0`, and a distinct two-vertex overlap is
forbidden by `lambda=1`. Equal marked rows are impossible.

## 6. The cap 383 might imply motif positivity

Attempt: combine the `R3`-triangle upper cap with the endpoint average.

Outcome: failed. Edge-disjointness gives only an upper bound of 383
`R3` triangles and 1,149 central triple-overlap events. No positive lower
bound on triple overlaps or double overlaps follows.

## 7. The factor scan might classify arbitrary matching triples

Attempt: generalize the `11^3` scan to all triples of perfect matchings.

Outcome: rejected as out of domain. The scan covers ordered triples chosen
from one fixed canonical one-factorization only. The candidate states this
restriction. A hostile repeated-factor triple `(0,0,0)` produces
multiplicities `(41,0,0,4)` for `m=0,1,2,3`, showing why factor choice
matters.

## 8. The 45-vertex certificate might already be a target graph

Attempt: apply every target degree and common-neighbour equality to the
emitted 45 vertices as a complete graph.

Outcome: successful scope attack, not a refutation of the stated candidate.
There are 42 degree failures, 24 edge-`lambda` failures, and 713
nonedge-`mu` failures. The candidate explicitly labels the object partial.

## 9. All completion-completion edges might really be undecided

Attempt: inspect common core neighbours of the 15 completion pairs.

Outcome: successful wording correction. Nine pairs already have two common
core neighbours and are forced nonadjacent in any target extension. Six
pairs remain edge-undecided. No candidate-assigned edge is contradicted.

## 10. The completion search might be heuristic

Attempt: independently enumerate every six-neighbour core pattern in the
stated domain and independently backtrack over the six defect closures.

Outcome: failed. The six domain sizes reproduce as
`2345,2353,2346,2346,2346,2353`; deterministic first-witness search takes
31 nodes and returns the frozen certificate exactly.

## 11. Candidate tests might supply independent verification

Attempt: treat the candidate's 12 tests as a second implementation.

Outcome: rejected. Those tests import `check_local_model.py`, so they are
candidate-owned regression tests, not clean-room verification. The verifier
uses a separate implementation and 29 hostile tests.

## 12. Candidate input provenance might be exact

Attempt: validate every input hash written in the candidate report and
machine-readable summary.

Outcome: refuted. The claimed Wave 33 comparison-results hash is
`8b7b27fd67f12bb82c60eb27c72a62c913d06f2d86f3eb626dcddd6ac75afeb`;
the frozen file hash is
`8b7b27fd67f12bb82cb6eebf645d0c46324d7227e51bdeb0093fbcdf9d753872`.
This remains a recorded provenance failure. It does not invalidate the
independent derivations in this Stage 2 package.
