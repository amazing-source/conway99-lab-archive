# Wave 123 failed routes and surviving boundary

## The concrete forty-word coordinates

The Wave120 signed supports are not a simultaneous coordinate realization
of the abstract residual Gram.  Their exact span projector violates the
universal diagonal `4/9` leverage bound at 46 coordinates.  This refutes
only that realization, not Wave120's pairwise positive control.

## Diagonal leverage alone

The explicit 26-subset in `candidate.json` has every leverage below `4/9`.
Therefore diagonal leverage cannot by itself prove the desired cap 25 for
families drawn from the Wave120 support code.

## Code-only three-point SDP

The candidate satisfies 2,340 rooted triple-intersection PSD blocks by
exact feature factorization.  More generally, the forty records are an
actual product-Johnson code, so code-only Schrijver/Terwilliger necessary
conditions cannot reject that code.  This does not transfer to a graph
eigenvector family.

## Graph-valued two-by-two completion

For the diagonal-pass 26-subset, 352 coordinate pairs admit neither
allowed value `1/63` nor `-8/63` in a PSD two-by-two completion of `E-W`.
The particular subset is refuted.

A 30-restart backward-removal heuristic evaluated 14,070 trial removals
and found no 26-subset with zero invalid rows.  This was not an exhaustive
enumeration, branch-and-bound proof, or semidefinite certificate, so it
provides no upper bound.

## Live continuation

The next credible constraint is a graph-valued PSD/SAT completion using:

1. one edge variable per coordinate pair;
2. `E-W` PSD or certified principal-minor/Schur consequences;
3. degree 14 and the exact `lambda=1`, `mu=2` pair equations;
4. all selected support eigen-equations in the same adjacency matrix.

The current package does not solve that completion.
