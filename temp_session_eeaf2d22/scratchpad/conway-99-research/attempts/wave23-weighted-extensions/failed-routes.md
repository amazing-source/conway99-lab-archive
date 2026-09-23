# Wave 23 closed and limited routes

## No Farkas obstruction exists for the frozen encoded system

The proposed infeasibility hypothesis for the frozen 712-row relaxation is
exactly contradicted by a nonnegative integer solution for every allowed

```text
h11 = 1412, 1416, ..., 2820.
```

Consequently neither the complete 712-row orbit-refined system nor its coarse
186-row aggregation can have a valid Farkas infeasibility certificate at these
parameters.

## The source six-count vector is not the defect

Counts through order five were reconstructed from `(n,k,lambda,mu)` alone.
The source order-six vector passes all 171 independently regenerated
orbit-refined `5->6` rows.  The `5->6` matrix has rank 61 over `F_7`; adding
the pinned `n3=705` coordinate raises the rank to 62.  Thus this gate does not
identify an omitted source-six term.

## The published Hamiltonian formulas are compatible, not independent inputs

Only the pinned identification of `H_11` and the coordinate equation
`H_11=4z` were used to parameterize the one-dimensional solution space.  The
other 18 source formulas were compared afterward and match the derived affine
coordinates exactly.  This compatibility result remains conditional on the
pinned human interpretation of the source figure's `H_i`-to-mask alignment.

## Scope wall

An affine vector of induced-subgraph counts is not a consistent assignment to
overlapping subsets and is not a `99 x 99` adjacency matrix.  The result proves
feasibility of necessary counting equations only.  It neither constructs nor
rules out `srg(99,14,1,2)`, and it gives no improvement over `n3>=705`.
