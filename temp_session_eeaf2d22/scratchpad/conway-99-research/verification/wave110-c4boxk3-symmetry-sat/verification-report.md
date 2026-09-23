# Wave 110 independent verification report

Verdict: `VERIFIED_WITH_EVIDENCE_BOUNDARY`, within the frozen,
motif-conditional scope.

## Input and replay

The sealed discovery manifest has SHA-256
`1cef4ea7a81e844f10a56ccb1b5a5e0c4c7414b4efc766c486cdc666de8940ea`.
All 14 entries match. After freezing it, the discovery audit and all eight
discovery tests passed. All seven independent verifier tests passed.

The four 45-second branches were then rerun sequentially. Every branch again
returned `UNKNOWN_TIMEOUT`; the minimum reported free-memory fraction over
the fresh runs was `0.5608723604036477`, above the required `0.15`. No SAT
model or UNSAT certificate was produced.

## Lex-CNF audit

The discovery clauses were tested exhaustively for all pairs of Boolean
vectors of lengths zero through four, 341 base-vector pairs total.
Existential satisfiability of the auxiliary variables agreed exactly with
Boolean lexicographic order.

The generic invariant is also direct. A prefix auxiliary is true exactly
when every preceding pair of bits is equal. Under a true prefix, one clause
forbids the first unequal pair `(1,0)`. Therefore an auxiliary assignment
exists exactly for `left <=lex right`.

## Simultaneous symmetry theorem

Let the 87 fixed incidence rows be partitioned into classes of identical
motif neighborhoods. Their multiplicities are

```text
size 1: 12 classes
size 2: 12 classes
size 3:  1 class
size 4: 12 classes.
```

Permuting labels inside one class preserves `P`, all three block equations,
and every `e(X0)` branch. This is an encoding relabeling; it does not assert
an automorphism of a target graph.

For `w_i=2^(86-i)`, define

```text
Phi(D) = sum D_ij w_i w_j
```

over edges whose endpoints lie in different pattern classes. Choose a
labeling minimizing `Phi` in the finite product-of-symmetric-groups orbit.
For `i<j` in one class `C`, swapping the two labels changes the potential by

```text
(w_i-w_j) sum_{k not in C} w_k (D_jk-D_ik).
```

If row `i`, restricted to columns outside `C`, were lexicographically larger
than row `j`, the first differing column would contribute negatively. Its
power-of-two weight is larger than the sum of every later available weight,
so the displayed sum would be negative. Since `w_i>w_j`, the swap would
strictly lower `Phi`, contradicting minimality.

Thus every class is simultaneously nondecreasing in one shared minimizing
labeling. Comparing consecutive rows is sufficient. Comparing only columns
outside the class is also sufficient: those are exactly the coordinates
controlled by the swap calculation. Omitting within-class coordinates
avoids imposing an unproved canonical order on edges whose column labels move
under the same class permutations.

As a computational cross-check, the verifier checked all 2,048 graphs for
two five-vertex colored partitions and all 4,992 minimizing labelings; every
minimizer satisfied all class row orders simultaneously. The formal swap
argument, not this finite test, establishes the general claim.

## `X0` branch coverage

The three empty-pattern vertices have three possible internal edges.
Exhausting all eight labelled graphs gives edge-count census
`(1,3,3,1)` for counts `0,1,2,3`. Edge count is invariant under every
permutation of `X0`, and the shared potential omits all within-`X0` edges.
Therefore potential minimization stays in the same branch. The four exact
cardinality branches partition every labeling without fixing an incompatible
canonical `X0` graph.

## Independent count reconstruction

The verifier reconstructed:

```text
3,741 outside-edge variables
317,985 common-neighbor conjunction variables
4,126 lex-prefix variables
325,852 variables total

953,955 conjunction CNF clauses
24,756 lex CNF clauses
978,711 CNF clauses total

1,044 distinct incidence rows
87 degree rows
1 e(X0) branch row
3,741 outside-pair rows
4,873 exact-cardinality rows
9,746 native at-most constraints
```

These agree with the submitted and archived counts.

## Evidence boundary

The archived hashes authenticate the preserved JSON bytes. Their RAM numbers
remain self-reported telemetry, although the fresh verifier reruns reproduced
the reserve claim. All eight historical and fresh outcomes are timeouts and
remain `UNKNOWN`.

This verification establishes no graph, no UNSAT result, no exclusion of the
motif, no resolution of Conway-99, and no novelty claim.
