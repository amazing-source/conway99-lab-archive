# Wave 33 rooted construction: objections and dispositions

## The restricted MILP is not exhaustive over designs

`CONFIRMED`. The 4,900 assignment variables cover every one of the `70!`
bijections between the fixed O labels and the blocks of one fixed simple
`2-(15,3,2)` design. They do not range over other nonisomorphic designs.
The candidate states this restriction and does not claim it without loss of
generality.

## The timeout might be an exclusion

`REJECTED`. Status 1, no primal, no objective, no node count, no gap, no
output, and no entered O-O phase prove nothing about feasibility or
infeasibility. An independent replay reproduced only the same metadata.

## The hostile partial might be a graph or an extendibility witness

`REJECTED`. Its Q-side design properties are exact, but ten `BF=2J`
equations fail and no O-O edges are supplied. It is neither a graph nor
evidence that some O-O layer exists.

## "No O-O edges supplied" might mean the search fixed D empty

`REJECTED`. The certificate leaves D unsupplied. The verifier's D=0 matrix is
only a hostile control, showing degree histogram `5^70,14^29`; it is not the
search domain and says nothing about a different completion.

## A hidden outside automorphism may shrink the 70! domain

`REJECTED`. The assignment variables are indexed by every fixed O label and
every fixed block, with no orbit representative or lexicographic quotient.
The source and independent row reconstruction both contain all 4,900 cells.

## The exact certificate numbers may be discovery-checker artifacts

`REJECTED`. The pre-frozen clean-room checker reconstructs the public B
matrix and independently recomputes row degrees, column degrees, all Q-pair
intersections, and the ten signed defects. A separate reimplementation also
regenerates the certificate bytes.

## The discovery checker fully guards scope metadata

`REFUTED`, nonblocking for these frozen bytes. It does not bind scope,
evidence kind, restrictions, limitations, discovery status, or duplicate
JSON keys. The frozen candidate text is honest, and the clean-room verifier
adds exact gates for all of those fields.

## The initial nonmatching checker replay was a candidate defect

`REJECTED`. The orchestrator omitted `--partial-certificate`, producing the
valid base-only hash `97f307...`. The correct frozen command produces
`ba6640...` byte-identically.
