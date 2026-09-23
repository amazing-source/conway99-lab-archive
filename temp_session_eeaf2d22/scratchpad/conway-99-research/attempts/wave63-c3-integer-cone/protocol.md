# Wave 63 integer-cone protocol

Frozen: `2026-07-27T22:01:00Z`

Status at freeze: `UNKNOWN`.

## Conditional target

Assume the prism-free `n3=4158`, `kappa=3` fixed-triangle lane.  The
36-vertex neighbour core `X` is a disjoint union of three 12-vertex
components, each with four vertices in each of the three fixed-triangle
fibres.  A hypothetical `36 x 60` binary incidence matrix `B` must obey

```text
BB^T = G
     = 12I - A_X + 2J - blockdiag(J12,J12,J12) - A_X^2.
```

Every column has two points in each graph fibre and two points in each
connected component.  A column is allowed only if all fifteen of its
unordered point pairs have positive target multiplicity in `G`.

No automorphism of the target graph or incidence design is assumed.
Coordinates inside the three fixed fibres are normalized only.

## Exact candidate system

For a component triple, enumerate all 21 component-by-fibre profiles whose
three row sums and three column sums are two.  For each profile, take the
Cartesian product of positive-target local pairs in the three components.
The resulting distinct six-sets are the variables `x_s`.

The exact pair system is

```text
sum_{s containing {i,j}} x_s = G_ij
```

for all 630 unordered point pairs.

## Stage A: rational cone

The floating HiGHS solve is only a screen.  A feasible result is retained as
`DERIVED` only after:

1. selecting the positive support of the floating basic solution;
2. choosing a square row minor;
3. solving that integer minor exactly over `Q` with FLINT/Dixon; and
4. replaying all 630 pair equations, nonnegativity, and total weight 60 using
   exact rational arithmetic.

A numerical infeasibility status would remain `UNKNOWN` unless accompanied
by an explicit rational Farkas certificate.  No infeasibility status or
Farkas certificate occurs in the final run.

## Fixed lane selection

Before inspecting LP outcomes, select:

- all 56 triples with the global minimum 15,936 candidate columns;
- the unique triple with the global maximum 27,200 columns;
- all 18 diagonal triples `(t,t,t)`; and
- the first triple in each of the seven Wave 61 full-pair `F2` rank strata.

After overlaps this is 74 triples.  This maximizes stress on the
minimum-support boundary while covering every component type and every
observed parity-rank stratum.  It is not the complete set of 275 safe
coordinate orbits or all 1,140 unordered triples.

The candidate counts for all 1,140 triples are independently recomputed
before the lane solves and must exactly match the frozen Wave 61 census.

## Stage B: distinct-column semigroup

On the first minimum-support lane, solve the exact pair system with binary
variables `x_s in {0,1}` for 30 seconds using one HiGHS MILP process.  A
model would be replayed exactly and retained as `CANDIDATE`.  A timeout or
nonhit is `UNKNOWN`, never nonexistence evidence.

## Sparse-dual boundary

An exact feasible rational witness rules out every separating Farkas
inequality using only the 630 pair coordinates for that lane.  Sparse
third-order coordinates remain potentially useful, but the Gram target does
not prescribe their right-hand sides.  A future triple-coordinate
separation must therefore couple one common nonnegative integral tensor to
the same sixty distinct columns; merely adding identities already implied
by the pair margins cannot exclude a lane.

## Resource and status guards

- One solver process at a time.
- Refuse to begin or continue below 20 percent free physical memory, stricter
  than the user's 15 percent floor.
- Discovery cannot verify itself.
- A rational witness is not an integer incidence design.
- An integer `B`, if found, would still not construct the compatible
  60-vertex `Y` graph or the full strongly regular graph.
- The endpoint and Conway-99 remain `UNKNOWN`.
