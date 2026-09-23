# Wave153 triangle-root correlation-polytope protocol

Frozen: 2026-07-28T12:33:00Z.

## Conditional scope

Assume the prism-free `n3=4158` endpoint and the `kappa=3` fixed-triangle
lane. The 36-vertex neighbour core is a disjoint union of three classified
12-vertex fibre-labelled components. A hypothetical `36 x 60` binary
incidence matrix has two ones in every graph fibre and two ones in every
component, with exact Gram target

```text
G = 12I - A_X + 2J - blockdiag(J12,J12,J12) - A_X^2.
```

No target-graph automorphism is assumed. Simultaneously relabelling the three
fixed-triangle vertices, all three fibres, and their component coordinates is
only a change of labels. The frozen Wave60 action gives 275 safe coordinate
orbits among all 1,140 unordered component triples.

## New finite projection

For each orbit representative, enumerate every distinct allowed six-set
column `s`. Let `a_s` be its 630-coordinate pair-incidence vector. Test the
bounded rational column polytope

```text
sum_s x_s a_s = vec_upper(G),
0 <= x_s <= 1.
```

This retains the exact triangle-root component/fibre profile, every zero Gram
pair, every pair multiplicity, total column weight, and the distinct-column
upper bound. It is stronger than unrestricted PSD, parity, and a nonnegative
pair cone without explicit upper bounds. It is weaker than a binary design:
rational coefficients need not be zero or one.

Wave63 supplied exact witnesses for a fixed 74-lane stress subset, not all
275 safe coordinate orbits. Wave153 tests every safe representative. If all
275 receive exact witnesses, coordinate relabelling transfers rational
feasibility to all 1,140 unordered triples and closes this rational
pair-coordinate projection as an obstruction route.

## Certificate gate

- Floating solver success is used only to choose a support.
- A positive claim requires an exact rational solve and replay of all 630
  pair equations, total weight 60, uniqueness of candidate indices, and every
  bound `0 < x_s <= 1`.
- Floating infeasibility or timeout remains `UNKNOWN` without an exact Farkas
  certificate.
- A binary incidence candidate must be emitted completely and checked
  directly before any integral claim.
- Discovery does not verify itself.

## Resource and scope wall

The implementation refuses to start below 20% free physical memory, stricter
than the user's 15% floor. It runs lanes sequentially.

Even complete rational feasibility neither constructs the binary incidence
matrix nor supplies the compatible 60-vertex residual graph. No endpoint
existence, endpoint exclusion, strict `n3` bound, Conway-99 resolution, or
novelty claim follows without a stronger certificate.
