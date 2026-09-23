# Wave 41 even-part equality classification

```yaml
role: proof_b
date_utc: 2026-07-27T05:25:43Z
git_commit: 4f1754a28723a8e0e4ea3025312cd264b1b117d2
claim_label: CANDIDATE
scope: >
  Complete discovery-side K39 rank-25 equality test for all seven
  edge-local alternating partition types containing an even part.
method: >
  Singular Schur congruence, complete minimum-permutation subspace cover,
  canonical right-kernel constraints, and exhaustive 10,395-matching lookup.
limitations:
  - Discovery cannot verify itself.
  - Combination with the all-odd lane remains CANDIDATE until independently checked.
  - No endpoint exclusion, n3 upper-bound improvement, graph, or novelty claim is made.
```

## Result

For

```text
H=[P+Q,F+3I+P;(F+3I+P)^T,P+R],
```

rank `K39=25` in an even-part type is equivalent to a finite right-kernel
bilinear equality. The checker completely enumerates all boundary
permutations `F`, groups their exact constraints, and tests all `10,395`
labelled perfect matchings `R` for every distinct right kernel.

All seven types have zero compatible equality targets:

```text
1^4+2, 1^2+2^2, 1^2+4, 1+2+3, 2^3, 2+4, 6.
```

The atomic minimum-`F` counts are respectively

```text
80,640; 192; 768; 80,640; 32; 64; 2,592.
```

Thus the scoped candidate is

```text
even-part edge type => rank_F7(K39)>=26.
```

Together with the separate all-odd equality obstruction, this yields the
candidate universal theorem

```text
rank_F7(M)>=26
```

for every hypothetical `srg(99,14,1,2)`. The global Conway-99 problem remains
`UNKNOWN`: this rank floor is not an endpoint contradiction and gives no
improved upper bound on `n3`.

Twelve standard-library tests pass. The seven atomic outputs, proof,
limitations, reproduction commands, and manifest are in
`attempts/wave41-evenpart-equality/`.
