# Derivation and local null model

Fix nonadjacent vertices `u,v` with common neighbors `p,q`. Under `P=0`, the
40 marked induced five-cycles split into 36 core and four fringe marks as in
Wave 167.

## 1. Forced completion candidates

For a mark

```text
m=(u,p,v,y,x),
```

let `r` be the other common neighbor of `u,y` besides `x`, and let `s` be
the other common neighbor of `v,x` besides `y`.

If `r` is nonadjacent to `p`, the pair already has common neighbor `u`, so
`mu=2` forces a unique second common neighbor `z_L`. Similarly, `s,p`
force `z_R` besides `v`. A valid completion requires

```text
z_L=z_R
```

and the remaining induced-pattern checks. Thus all candidate vertices are
forced and the mark succeeds zero or one times.

Consequently,

```text
successful marks = 8*W8,
F=166320-8*W8.
```

The success indicator lives on the five marked vertices plus `r,s,z`, so it
is an induced order-eight event.

## 2. Why marginal PSD has the wrong strength

One may encode forced left and right candidates by one-hot vectors `L_m,R_m`
after placing invalid states in distinct failure symbols. Then successful
agreement is a cross-correlation, while mismatch is a squared-distance
energy.

Cauchy-Schwarz controls that energy from below, whereas the proof needs an
upper bound on failures. Equal left and right marginals are not enough: two
equal candidate multisets can be paired by a derangement and have no
successes. Any useful PSD certificate must contain joint left/right
correlations, not only their separate degree distributions.

## 3. Pairwise failure graph proposal

Let the 40 marks be vertices of an incompatibility graph `Gamma_uv`, joining
two marks only when the currently derived pairwise/root-local clauses prove
that they cannot both fail.

The desired pointwise result would follow from

```text
alpha(Gamma_uv)<=4.
```

This proposal has a local null model.

## 4. Five simultaneous mismatch failures

Choose five optional pure core marks in one lane, with pair-support endpoints

```text
(rho_i,sigma_i), i=1,...,5,
```

chosen disjoint within the abstract shell.

Let `a,b` be the triangle mates of `up,vp`. Complete the middle-vertex
neighborhood as the seven disjoint edges

```text
N(p) =
  {u,a} disjoint_union {v,b}
  disjoint_union
  {alpha_i,beta_i}, i=1,...,5.
```

For each `i`, prescribe

```text
CN(p,rho_i)   = {u,alpha_i},
CN(p,sigma_i) = {v,beta_i},
alpha_i != beta_i.
```

Make `rho_i,sigma_i` nonadjacent and assign their two required common
neighbors outside `N(p)`, so neither is a common `p`-neighbor. Then the two
forced completion candidates for mark `i` disagree, and all five selected
marks fail.

The displayed middle neighborhood has degree exactly 14 and the required
`7K2` form. The five gadgets can be kept otherwise disjoint, with every
specified edge having at most its one allotted common neighbor, every
specified nonedge having at most or exactly its two allotted common
neighbors, and no prism forced inside the displayed local structure.

This is not a 99-vertex SRG and is not claimed globally extendable. Its exact
scope is that every pair among the five failures, and the displayed
five-gadget as a whole, is compatible with the clauses used to build the
pairwise incompatibility graph. Hence those clauses cannot imply
`alpha(Gamma_uv)<=4`.

## 5. Conditional inherited failures

The four fringe marks always fail. Extra core failures inherited from fringe
incidences are conditional:

- if the ordinary endpoints of two same-side fringe edges are distinct, each
  retains a core incidence and creates an impure core mark;
- if the two fringe edges share their ordinary endpoint, that endpoint has
  no core incidence and this inherited failure disappears.

Therefore four additional inherited core failures form a compatible branch,
not a universal count.

## 6. Higher-order replacement

The missing information includes completing all fresh gadget vertices to
degree 14 within 99 vertices, satisfying every cross-gadget `lambda/mu`
condition, assigning all remaining unique triangle apices, preventing every
global prism, and respecting the full spectrum and incidence geometry.

A retained certificate must encode at least one such closure mechanism. A
schematic five-way target is

```text
sum_(m in T) (1-t_m) <= 4
```

for each globally admissible five-mark set `T`, certified by extension
identities rather than assumed from the local shell. Globally, it is enough
to prove only `E<=8`, so a successful certificate may also average
five-way constraints across overlapping nonedge roots.
