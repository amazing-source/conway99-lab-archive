# Independent verifier request

Claim label submitted: `CANDIDATE`.

Independently check the artifact
`attempts/wave153-alternative-compatibility/exact-results.json.gz` without
trusting the floating discovery path.

Required checks:

1. Verify every frozen input hash in `input-freeze.sha256`.
2. Rebuild the 18 component adjacency matrices and all 275 frozen safe orbit
   representatives from the Wave60 inputs.
3. Rebuild every allowed six-set independently, including two-per-component,
   two-per-fibre, and zero-target-pair exclusions.
4. Decode every rational coefficient canonically.
5. For every representative, replay all 630 unordered pair totals against
   `G`, all 36 row margins against 10, total weight against 60, unique and
   in-range candidate indices, and `0 < x_s <= 1`.
6. Confirm the frozen coordinate orbits cover exactly all 1,140 unordered
   component triples, without assuming a target-graph automorphism.
7. Mutate at least one numerator, denominator, candidate index, orbit
   position, and coefficient bound; require each hostile case to fail closed.
8. Enforce the scope wall: rational feasibility is not a binary incidence
   design and says nothing by itself about residual-graph compatibility.

Requested disposition if all checks pass:

```text
VERIFIED_WITH_SCOPE:
exact rational null witness for the complete safe-orbit bounded
pair-correlation projection only
```

