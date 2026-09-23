# Wave 204 proof B: fourth-order projector detector

```yaml
role: proof_b
date_utc: 2026-07-29T19:02:43Z
git_commit: e6ac24b5728ae8f2dc13b5a6ee0f50e965843b71
claim_label: DERIVED
scope: >-
  Conditional prism-free n3=4158 and centered rank-11 endpoint: reduce every
  adjacent pair of rank-six star projectors to an exact 6-by-6 module and
  classify its alternating fourth trace.
inputs:
  verification/wave171-pq-centered-code/verification-report.md: 1f2ba5ed92ba6bb1ccc05cd753a8e359f208c3ddc7ca85766f26f8869346414f
  verification/wave176-star-projector-circuits/audit.md: f58577409f39e98b06bfbe206221d3d278f0c473bcf5057afc381094d5e65d05
  agents/2026-07-29-wave191-global-star-module-proof-b.md: afe7d35627ec14a9599b427bcca0751e86a3f32b71fb7baf4d91e9e2e335f75f
  verification/wave203-two-center-incidence-verifier/audit.md: 382d8553457557fe2ecbe0fd1733ecb06b01f5c60be879e65cab56c078edc3d7
method: >-
  Symbolic star-Gram compression, exact modular row reduction and polynomial
  identities, exterior/symmetric-square traces, and explicit rank-11 hostile
  controls. No graph, code, cover, SAT, LP, configuration, enumeration, or
  isomorphism search.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave204-projector-fourth-order-proof-b\exact_check.py --verify
  attempts\wave204-projector-fourth-order-proof-b\exact-results.json
outputs:
  attempts/wave204-projector-fourth-order-proof-b/exact-results.json: 008b098012807fa98a3874df641575c49e7030e120e4417c8eada153c792b151
limitations:
  - Adjacent pairs only; the nonedge fourth traces are not classified.
  - No global count of 4+2 edge types or incompatible rank bound is proved.
  - The abstract controls fail projective distinctness and graph incidence.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain UNKNOWN.
```

## Exact theorem

Let `x~y`.  In the six outer columns of each star, write

```text
G=J_6-I_6,
C=J_6+N,
```

where `N` is the biadjacency matrix of the Wave176 outer `2`-regular
bipartite graph.  Then

```text
G^-1 C=2N,
A_xy=P_xP_yP_x restricted to E_x=N N^T.
```

Consequently

```text
tr((P_xP_yP_x)^2)
 =tr(P_xP_yP_xP_y)
 =1 in F_3
```

if and only if the outer cycle type is `4+2`.  The trace is zero for types
`6`, `3+3`, and `2+2+2`.

Equivalently,

```text
tr((wedge^2 P_x)(wedge^2 P_y))
 =(tr(P_xP_y)^2-tr(P_xP_yP_xP_y))/2
```

is the same detector, because every adjacent pair has
`tr(P_xP_y)=0`.

## Sharp boundary

Two exact abstract systems with 99 projectors, 231 labelled singular
columns, rank-11 square-zero centered Gram, seven simplex columns per star,
column degree three, and zero total projector sum have the same labelled
pairwise projector trace Gram but different fourth-trace matrices.

They repeat projective directions and are not linear point-triangle
incidences, so they are not endpoint configurations.  They prove only that
the pairwise trace Gram does not determine fourth order.

The missing invariant is the graph-specific distribution and global
compatibility of

```text
h_xy=tr(P_xP_yP_xP_y),
```

especially on nonedges.  No endpoint exclusion or Conway-99 resolution
follows.
