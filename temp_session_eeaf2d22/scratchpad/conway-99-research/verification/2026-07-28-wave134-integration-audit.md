# Wave 134 quaternary-code integration audit

Date UTC: 2026-07-28

Verdict: **PASS WITH TWO RECORDED PREPUBLICATION VETOES AND UNCHANGED
GLOBAL STATUS**.

The verifier independently reconstructed the final sealed Wave 134
quaternary-code package without importing discovery code.

## Verified scoped result

Conditional on a hypothetical `srg(99,14,1,2)`, the adjacency row code over
`Z/4Z` has type `4^54 2`, its dual has type `4^44 2`, and translation by
`2*1` exchanges the zero- and two-symbol counts. Complete coefficient
patterns on at most three adjacency rows force 84 expanded compositions and
8,557,760 distinct words. The even-sum closed-row patterns force 44 expanded
dual compositions and 4,126,784 distinct words.

The independently reconstructed symmetrized MacWilliams transform has:

```text
raw compositions:        5050
primal symmetry orbits:  1119
allowed dual orbits:     1114
forbidden dual orbits:   161
```

Discovery replay and 5/5 tests pass. Independent replay and 10/10 tests pass.

## Recorded verifier vetoes

1. The first preseal model omitted mixed odd/even coefficient patterns on
   supports of size at most three. The complete forced totals are
   8,557,760 primal and 4,126,784 dual words. Every solver outcome from the
   narrower model was invalidated.
2. The first sealed transform allowed dual residue weight 92. Since
   `Res(Cperp)=D intersect even`, `1` belongs to `D`, and `d(D)>=8`, the
   complement of such a residue would be a forbidden weight-seven word.
   Four more symmetry orbits are therefore zero, changing the final dual
   partition from `1118/157` to `1114/161`.

Both corrections were made before publication. Superseded manifests are not
evidence.

## Manifest bindings

```text
Wave134 discovery: 581678d37091754f4bf1f197223a120d82f3051020a45b601e84889dfdad81e9
Wave134 verifier:  7fc68ba875d7fdc31dd03584d95bd7f80e7ddec01d9c247ce351ac4b4ae6a858
```

## Status wall

Corrected rational and integral feasibility are `UNKNOWN_NOT_RUN`. No
quaternary code, adjacency matrix, graph, rank exclusion, endpoint exclusion,
strict upper bound below `n3=4158`, Conway-99 resolution, or novelty claim
follows.
