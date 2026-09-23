# Failed routes and scope boundaries

## Treating the fixed graph as regular

The fixed graph need not be regular before the argument: each fixed degree
may be 3 or 14.  The verifier retains both types and derives the row identity
before eliminating mixtures.

## Using the all-degree-3 shortcut too early

The tempting regular-graph equation `9=2f-2` is valid only after all
degree-14 vertices have been ruled out.  The verified proof instead handles
the degree-14 identity branch and the mixed `f=22` branch explicitly.

## Confusing exact order with an exponent condition

The identity satisfies `g^11=1` but has order 1 and fixes all vertices.
Accordingly, the theorem is scoped to permutation order exactly 11.

## Promoting a conditional symmetry result

Wave 72 by itself shows only that any order-11 automorphism would act
semiregularly.  Excluding such automorphisms requires a separate complete
verification of the semiregular quotient exclusion.  Even that combination
would leave asymmetric targets and global existence unresolved.

## Initial verifier-harness failure

The first independent test run incorrectly rejected the legitimate empty
fixed-set model.  The enumerator had applied the constraint
`high_to_low <= number_of_low_vertices` even when there were no high vertices,
so a neighbor count belonging to an absent type was treated as meaningful.
Two of 14 hostile tests failed and the discovery comparison also failed.

The checker was corrected to apply each capacity constraint only when its
source type is nonempty.  The full independent replay then retained exactly
the empty and identity models, all 14 tests passed, and all six compared
fields matched.  This was a verifier implementation error, not a mathematical
counterexample.
