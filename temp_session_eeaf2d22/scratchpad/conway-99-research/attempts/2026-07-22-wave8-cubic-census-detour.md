# Wave 8 cubic-census and Petersen detour

```yaml
role: proof_a
date_utc: 2026-07-23T01:36:12Z
git_commit: b2a31846d243a76b9e516f85304e21137e3fe874
claim_label: REFUTED
scope: superseded exploratory routes for the n3=30 equality case
inputs:
  house_of_graphs_cub10_g6:
    url: https://houseofgraphs.org/data/cubics/cub10.g6
    sha256: 0c3182bcbbfdc38fc7b84f3a1ac510834c3064524db00afeac212a3292f17c7b
method: attempted census-based point-family enumeration and an unnecessary spectral reduction
command: exploratory scratch commands, not a publication verifier
outputs:
  retained_decisive_output: none
limitations: both routes were abandoned before publication; the final proof and independent exhaustive audit supersede them
```

## Unoptimized census attempt

The first equality attack downloaded the 19 connected cubic graphs of order
ten from House of Graphs and planned to add the two disconnected types
`K4+K3,3` and `K4+prism`. A generic point-clique enumerator was drafted, but
its naive family-profile loop was terminated after roughly eighty seconds
without producing a graph-level result. The uncommitted draft was removed;
no mathematical conclusion relied on its incomplete run.

The later independent verifier replaced this route with a complete solver-free
generator. Its committed slow audit obtains 133,105 normalized labeled cubic
graphs, exactly 21 isomorphism types, and zero surviving exact-two covers. See
`verification/n3-equality/audit_exhaustive.py` and its certificate.

## Petersen detour

An early human derivation used the fixed-point identity to force fifteen size-
two points, then attempted a spectral reduction of the cubic complement to the
Petersen graph and a final line-graph contradiction. During adversarial review,
the orchestrator noticed that two size-two points meeting in an active graph-
triangle already give a forced actual graph edge. When their other complement
endpoints are nonadjacent, the support identity gives forbidden `H`-degree one.

This makes the Petersen classification unnecessary. More importantly, the
intermediate auxiliary graph in the detour had silently omitted those forced
internal graph edges. The spectral tail was therefore not published. The
corrected classification-free proof handles all connected and disconnected
cubic complements directly and is recorded in
`agents/2026-07-22-wave8-n3-equality.md`.
