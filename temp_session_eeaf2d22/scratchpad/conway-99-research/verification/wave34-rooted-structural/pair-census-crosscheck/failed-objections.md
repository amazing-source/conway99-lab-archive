# Pair-census crosscheck: retained objections

## 1. The nine-state list might omit a larger c value

Failed. For distinct O-vertices, all four coordinates are nonnegative and
sum to two. Therefore `c<=2`, and exhaustive enumeration gives exactly the
nine published states.

## 2. The r-marginal 33,33,3 might assume a fixed B design

Failed. It follows for every simple `2-(15,3,2)` design. A fixed row contains
three Q-pairs, each with one other block; simplicity makes those three blocks
distinct. The total intersection multiplicity is `3*(14-1)=39`.

## 3. The row census might not be unique

Failed. The nine state counts are determined successively by nine pivots:
`g2`, `r2`, `hg`, `hr`, `gr`, remaining `r1`, remaining `g1`, remaining
`h1`, and remaining `r0`. A hostile change to `diag(DT)` changes the
solution, confirming that the fixed S-O equation is active.

## 4. g=2 might coexist with a B intersection

Failed. The exact pair equation is `g+r+h+c=2`. With `g=2` and the other
coordinates nonnegative, `r=h=c=0` is forced.

## 5. The 210 X11 pairs might not form a regular graph

Failed. `sum_{j!=i} g_ij r_ij=6` for every row, and the nine-state support
makes `(g,r)=(1,1)` the only contributing state. Every vertex has X11 degree
six, so the unordered edge count is `70*6/2=210`.

## 6. Disjointness from D might not imply disjointness from D squared

Failed for this state. X11 is specifically `(g,r,h,c)=(1,1,0,0)`, so both
`h=0` and `c=(D^2)_ij=0` hold. The two disjointness statements use different
coordinates and are both checked.

## 7. The 448,879,368 count might inherit the released dynamic program

Failed. The crosscheck does not use that program. It evaluates 7-by-7
weighted permanents for all 5,040 relative permutations and divides each
cycle class by its exact number of alternating decompositions.

## 8. Forbidding duplicate support pairs might remove more than one-cycles

Failed. A half-cycle of length one is exactly a doubled multigraph edge with
both parallel copies selected. Longer cycles select at most one copy of each
underlying point-line edge. Thus the duplicate-pair rule removes exactly the
classes containing a part `1`.

## 9. The count might describe compatible 15-column designs

Successful scope objection. It does not. The total is per single column
after `Pb=2*1` and the duplicate-pair rule only. Compatibility of fifteen
columns and all remaining graph equations stays `UNKNOWN`.
