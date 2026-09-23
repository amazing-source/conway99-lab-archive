# Hostile controls

Claim label: `VERIFIED`, within the conditional scope in `derivation.md`.

## Common-neighbor budget

- For a selected nonadjacent same-sign pair, the outside vertex consumes one
  of the two common neighbors, leaving at most one common neighbor on the
  opposite support.
- For a selected adjacent same-sign pair, it consumes the unique common
  neighbor, leaving zero on the opposite support.
- The proof uses only the weaker uniform intersection bound at most one, so
  adjacent pairs cannot invalidate it.

## Higher intersections

A direct four-set inclusion-exclusion display has alternating triple and
quadruple terms. The verifier instead counts point multiplicities and uses
\(m-1\leq\binom m2\). This proves the union lower bound without silently
discarding higher intersections.

## Equality perturbations

- Three size-four blocks with pair intersections at most one need at least
  nine points.
- Equality at nine forces all three pair intersections to have size one.
- A common point in all three blocks would have multiplicity three and make
  \(m-1<\binom m2\), forcing union size at least ten. Hence the three
  intersection points are distinct and the triple intersection is empty.
- Exhaustive labelled enumeration gives 7,560 equality triples, all rigid.
- Exhaustive backtracking finds no three-block family on eight points and no
  four-block family on nine points.

## Degree-five perturbation

For the norm-18 \(h=1\) lane, replacing one selected size-four block by a
size-five block raises the minimum union from nine to ten. Hence a \(d=3\)
outside block cannot contain either endpoint of the unique same-sign edge.
Selecting both endpoints only strengthens the obstruction because their
opposite-support neighborhoods are disjoint.

## Histogram perturbations

Every emitted row is checked against all three moments and against the
packing cutoff. Allowing one higher degree recovers additional Wave 74
scalar rows, confirming that the 1/7/4 collapse is caused by the new packing
bound rather than an accidental enumeration restriction.

## Status control

No scalar row is promoted to a labelled design or graph. No global
nonexistence, Conway endpoint, or novelty claim is made.
