# Wave 60 construction/proof-B report: the three-component incidence design

```yaml
role: construction
date_utc: 2026-07-27T21:31:58Z
git_commit: 4bb1989e9e286b2ec753a855db58ad584e31f63a
claim_label: DERIVED
scope: conditional kappa=3 one-triangle neighbour core; exact component classification, invariant filters, and BB^T selection probes
inputs:
  - verification/wave36-block-compatibility/independent-results.json: b92ee5cde6a63ba3cce09bc2eae1518979aea09c4f5db39789b65f117b0768c4
  - attempts/wave58-cross-incidence-rank/exact-results.json: ec03c32fc72ec75222049a49b194b10bcae6bf1122ac82d9d9943e5b2f63181a
method: exhaustive fibre-labelled component census and canonicalization; exact F2 and spectral signatures; safe coordinate-orbit reduction; exact column enumeration; bounded PB/SAT; exact-marginal local search
command: .\.venv\Scripts\python.exe -B attempts\wave60-c3-incidence-design\test_exact_check.py
outputs:
  - attempts/wave60-c3-incidence-design/exact-results.json: 35b6436c7ba5619fcf7e3840cbdacd594461c01df8758686450f5d8eea8e36f3
limitations: no full B; no checked UNSAT certificate; no compatible Y graph; endpoint and Conway-99 remain UNKNOWN; discovery does not verify itself
```

## 1. Frozen conditional problem

Assume the prism-free `n3=4158` endpoint.  Fix a triangle and write its
36 neighbours as three twelve-point fibres `X0,X1,X2`.  In the case
`kappa=3`, Wave 36 forces the cubic graph `G[X]` to have three connected
components, each containing four vertices from every fibre.  Every one of
the sixty `Y` vertices has a six-point neighbour column meeting every fibre
twice and every component twice.

The target is the exact binary Gram equation

```text
B B^T = 12I - A_X + 2J - blockdiag(J12,J12,J12) - A_X^2.       (1)
```

No automorphism of the target graph or its completion was used.

## 2. Complete fibre-labelled component classification

A component has three four-point fibres.  Each fibre induces a perfect
matching and each pair of fibres is joined by a perfect matching.  Coordinate
relabeling fixes:

- the matching in fibre zero;
- the cross matching from fibre zero to fibre one;
- the cross matching from fibre zero to fibre two.

The two remaining within-fibre matchings have three choices each and the
remaining cross matching has `4!=24` choices.  Thus the normalized labelled
census has exactly

```text
3 * 3 * 24 = 216
```

records.  The checker retains precisely those which are connected, cubic,
triangle-free, and obey the exact sector-aware common-neighbour caps:

- a same-fibre nonedge has at most one common neighbour inside `X`, because
  its fibre root is already one of the SRG's two common neighbours;
- a cross-fibre nonedge has at most two common neighbours inside `X`.

Exactly 50 labelled records survive.  Their four-cycle counts are:

```text
C4=2:  6
C4=4: 30
C4=6: 14.
```

The full `S4 x S4 x S4` action inside the fixed fibres was then enumerated.
Taking the minimum adjacency code in every orbit gives exactly 18
fibre-preserving types.  This is finer than the three-value four-cycle
ledger: the construction problem cannot safely identify types merely because
their `C4` values agree.

## 3. Safe symmetry reduction

The three connected components are unordered, so the 18 types initially give

```text
C(18+3-1,3) = 1140
```

multisets.  There is one additional safe coordinate symmetry: simultaneously
relabel the three vertices of the fixed triangle and hence the three fibres
inside every component.  This is not an assumed graph automorphism; it is a
global change of names in the frozen construction.

The checker explicitly constructs the six resulting permutations of the 18
types.  Their action reduces the 1,140 multisets to 275 orbits.  Component
spectra, local-Gram spectra, local binary ranks, row signatures, and
fibre-preserving automorphism orders give fifteen coarser signature groups, but
those signatures are not used as an isomorphism claim.

## 4. The binary-rank obstruction fails exactly

Every column has even weight in each fibre and in each component.  Over
`F2`, the three fibre indicators and three component indicators span a
five-dimensional space and annihilate every column.  Therefore

```text
rank_F2(B) <= 31.
```

The diagonal of (1) is ten, hence zero modulo two.  A symmetric
zero-diagonal matrix over `F2` is alternating and has even rank.  A necessary
condition is consequently

```text
rank_F2(G) <= 30 and even.
```

The complete scan of all 1,140 targets yields:

| `rank_F2(G)` | triple count |
|---:|---:|
| 14 | 67 |
| 16 | 415 |
| 18 | 412 |
| 20 | 185 |
| 22 | 51 |
| 24 | 10 |

Thus all triples pass.  The finite-field proposal is a checked
failure-of-obstruction, not an endpoint exclusion.

## 5. A useful exact marginal reduction

Inside any one 12-vertex component, every global column selects exactly one
local pair.  The off-diagonal target entries in that component sum to sixty.
Moreover, the target multiplicities of pairs incident with every local vertex
sum to ten.  Therefore, enforcing all within-component off-diagonal entries
already forces:

- exactly sixty selected columns;
- every row of `B` to have sum ten;
- all 36 diagonal entries of (1).

The global-cardinality equation and diagonal equations are redundant in the
SAT model.

There is another simplification special to `kappa=3`.  A column selects only
two vertices in any component.  For a selected vertex, `(I+A_X)b` is at most
two; for an unselected vertex it is also at most two.  Hence the Wave 36
mixed cut

```text
d(b)=2*1-(I+A_X)b >= 0
```

is automatic after the two-per-component condition.  The exact enumerator
observes zero mixed-cut rejections.

## 6. Candidate support is abundant

A local selected pair has one of six fibre categories:

- `A_i=(2,0,0)` with the doubled coordinate in fibre `i`;
- `B_i=(1,1,0)` with the zero coordinate in fibre `i`.

The fibre sum condition admits exactly 21 ordered triples of component
categories.  Summing the product of the three positive local-pair support
counts over these patterns gives the complete number of individually
available columns without enumerating them.

Across all 1,140 triples this count ranges from 15,936 to 27,200; no triple
has empty support.  For aligned component type `(4,4,4)`, direct enumeration
finds exactly 20,928 distinct six-subsets and all 21 formal pattern matrices.

This eliminates a simple support defect as the obstruction.  The remaining
difficulty is simultaneous multiplicity coupling.

## 7. Exact selection probes

For `(4,4,4)`, one Boolean variable was assigned to each of the 20,928
columns.  Sequential counters encode the 588 nontrivial off-diagonal target
equalities.  The compressed CNF has 953,580 variables and 1,971,780 clauses.

A bounded Glucose 4.2 run used:

```text
conflicts:     10,431
decisions:    134,788
propagations: 79,165,487
solver time:    25.29 seconds
```

and returned `UNKNOWN`.  It emitted no candidate and no proof certificate.

The exact-marginal construction search takes the sixty prescribed local-pair
occurrences in each component and changes only their coupling.  Three
symmetric aggregate pattern ledgers were tested, with `x_AAA=0,6,12`.  The
best squared cross-Gram errors were:

| type triple | `x_AAA=0` | `x_AAA=6` | `x_AAA=12` |
|---|---:|---:|---:|
| `(4,4,4)` | 88 | 88 | 104 |
| `(0,0,0)` | 84 | 88 | 82 |

All best states had zero duplicate columns.  Positive error is only search
telemetry: the move set is heuristic, the pattern ledgers are restricted,
and no nonexistence conclusion follows.

## 8. Conclusion

The run supplies a complete conditional component classification and reduces
the unrestricted `kappa=3` incidence search to 275 safely inequivalent
component triples.  It also proves that the natural `F2` rank and
individual-support obstructions do not close the case, while removing
redundant constraints from the exact design formulation.

It does not supply a full incidence matrix or a complete exclusion.  The
`kappa=3` case, the prism-free endpoint, and Conway-99 remain `UNKNOWN`.
