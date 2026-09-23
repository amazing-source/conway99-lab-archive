# Wave 20 global-Schur literature/status preinspection freeze

```yaml
role: literature
date_utc: 2026-07-23T16:25:26Z
git_commit: a121e789e03a32c3d29bce8947b16033c0061ce7
claim_label: UNKNOWN
scope: prior-art and current-status audit only for the conditional inequalities n3 >= 705 and induced_C6_count >= 209991
inputs:
  agents/2026-07-23-wave20-global-schur.md: 64352e1d96ed9a924e075c2d0659be8de887751194068a14b096e112a9320632
method: freeze the exact claim and terminology before any new literature search
command: null
outputs:
  this_file: hash to be recorded after creation
limitations: no proof-candidate inspection or certification; a literature nonhit cannot prove novelty
```

## Frozen formulation

Conditional on the existence of a finite simple undirected
`srg(99,14,1,2)`, let `n3` denote the number of induced copies of the
six-vertex configuration `N3`: two vertex-disjoint triangles joined by
exactly two cross-edges, with those two cross-edges independent (vertex
disjoint). The candidate claims

```text
n3 >= 705
induced_C6_count = 209286 + n3
induced_C6_count >= 209991
```

The first inequality and its proof are out of scope for this audit. The
identity relating induced hexagons to `n3` is historical-source material and
is in scope.

## Terminology boundary

Here “independent” modifies the two cross-edges in `N3`; `n3` is **not** the
number of independent vertex 3-sets (cocliques). Searches will include both
the repository's `N3` vocabulary and the source authors' diagram/index
vocabulary so that a notation change does not create a false nonhit.

## Questions frozen for audit

1. Do primary sources through 2026-07-23 publish `n3 >= 705`,
   `induced_C6_count >= 209991`, or a stronger numerical bound for the same
   target and same `N3` count?
2. Do they publish an equivalent Schur/Hadamard-product inequality using a
   primitive idempotent/projector of the 231-vertex triangle (clique) graph?
3. Do current primary/maintained sources resolve existence of
   `srg(99,14,1,2)`?

The only admissible novelty verdicts are `KNOWN`, `NO RESOLUTION FOUND`, or
`UNKNOWN`. Search-engine absence alone cannot support `KNOWN` or a proof of
novelty.
