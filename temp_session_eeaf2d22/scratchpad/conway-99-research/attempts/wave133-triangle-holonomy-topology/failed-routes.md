# Wave 133 retained null routes

## Local sign parity

Fixed-point-free permutations of twelve points have both signs.  The exact
controls use cycle types `2^6` and `12`; both lift to cubic triangle-free
36-vertex fibre cores satisfying the inherited partial-star codegree caps.
No claim may infer a sign from derangement alone.

## Global sign multiplication without twists

Multiplying the local signs gives the exact identity

```text
product_T sign(h_T)=(-1)^H=(-1)^(chi+E-F).
```

An orientable-surface argument would force `chi` even, but orientability is
not among the endpoint consequences currently derived.  The endpoint-scale
control has all-`222` counts, a simple 36-regular quotient, six `C6` link
components at every triangle, and `chi=-693`.  Its odd Euler characteristic
forces nonorientability and its global sign product is `+1`.

## Covering-space parity

Passing to the orientation double cover cannot repair this route.  It
doubles `H`, `E`, `F`, and `chi`; the lifted sign product is a square and is
therefore `+1`.  A covering argument needs extra information that constrains
the twist cocycle before taking the cover.

## Scope of the positive control

The control is an abstract closed surface incidence system.  It is not an
SRG, does not reconstruct the 99 graph vertices or 693 graph edges, and does
not impose the simultaneous one-triangle `B/H` completion equations.
Survival of this relaxation is not evidence that the Conway 99-graph exists.
