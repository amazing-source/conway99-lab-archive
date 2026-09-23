# Wave 28 literature/status audit: protocol freeze

Frozen before live searching at `2026-07-24T02:33:38Z`.

```yaml
role: literature
public_base_commit: d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b
claim_label: UNKNOWN
search_through_utc: 2026-07-24
target_status_before_search: UNKNOWN
novelty_before_search: UNKNOWN
```

## Frozen inputs

| Input | SHA-256 |
|---|---|
| `agents/2026-07-24-wave28-orchestrator-brief.md` | `6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e` |
| `agents/2026-07-24-wave28-glue-discriminant.md` | `3c1354a04f33602c6e339875c8de4f77d1874bd6e8f83dbcb712b91717d6c1ff` |
| `agents/2026-07-24-wave28-theta-modular.md` | `8783be7e730306637ed863b4d9fbe8f4193ad756e7ec86d697c7407688a5423a` |
| `agents/2026-07-24-wave28-simultaneous-neighbor-freeze.md` | `7b8fce3763e2f6d4db2e0f7841e680d01486195d3ea4b6b04c5f59ace768d90a` |

The last input is an orchestrator-frozen candidate, not a verified result.
The other discovery reports also remain subject to their separate exact and
independent checkers.  This audit checks literature and source attribution;
it does not certify their arithmetic.

## Questions frozen before search

1. **Exact target status.** Is existence or nonexistence of
   `srg(99,14,1,2)`—also called Conway's 99-graph problem—resolved by a
   construction, proof, correction, or catalogue update?
2. **Scaled-dual lattice package.** Is there a published classification or
   exact result covering positive-definite even rank-44 lattices `L` with
   `21L* <= L` and determinant in
   `{9,21,49,81,189,441,729,1029}`?
3. **Discriminant/root glue.** Which primary sources support the standard
   ingredients used for elementary 3- and 7-primary discriminant modules,
   Milgram's signature relation, overlattice/isotropic-subgroup gluing,
   primitive root closures, and rootless complements?  Does a source state
   the exact combined Wave 28 reduction?
4. **Theta controls.** Do primary catalogues or papers support only the
   attributed identities for the Coxeter--Todd lattice `K12` and the
   Koch--Venkov rank-32 lattice `Lambda(F)`/`KV32F`?  Is the exact comparison
   `K12 orthogonal_sum Lambda(F)` versus `E6^6 orthogonal_sum E8` already
   present?
5. **Simultaneous two-neighbor package.** Is there prior work on a single
   Kneser two-neighbor basis change acting contragrediently on a paired form
   or scaled-dual endomorphism package, beyond the standard one-lattice
   neighbor construction?
6. **Marked frame/Schur-cubic package.** Is there a source treating 231
   selected norm-four vectors in rank 44 with tight-frame/projector,
   restricted Gram alphabet, Schur-square, and cubic-tensor constraints?
7. **Exact root-image pattern result.** Is the reduction from 46
   zero-sum/squared-norm count patterns to 32 patterns under the cubic-energy
   bound already stated in the literature?

## Candidate-independent terminology

The searches use terminology fixed independently of the candidate's desired
outcome:

- `"strongly regular graph (99,14,1,2)"`, `"srg(99,14,1,2)"`,
  `"Conway 99 graph"`, and `"Conway's 99-graph problem"`;
- `"even lattice"`, `"rank 44"`, `"21L* subset L"`, `"scaled dual"`,
  `"21-modular lattice"`, `"3-elementary"`, `"7-elementary"`, and the eight
  determinant values;
- `"finite quadratic form"`, `"discriminant form"`, `"Milgram formula"`,
  `"overlattice"`, `"isotropic subgroup"`, `"root sublattice"`,
  `"primitive closure"`, and `"glue code"`;
- `"Coxeter-Todd lattice"`, `"K12"`, `"Koch-Venkov lattice"`,
  `"Lambda(F)"`, `"KV32F"`, `"E6^6"`, and `"E8"`;
- `"Kneser 2-neighbor"`, `"two-neighbor lattice"`,
  `"simultaneous neighbor"`, `"paired quadratic forms"`, `"contragredient"`,
  and `"scaled-dual endomorphism"`;
- `"tight frame"`, `"projector Gram matrix"`, `"Schur square"`,
  `"Hadamard square"`, `"cubic moment tensor"`, `"spherical design"`,
  `231`, `44`, and the alphabet `{0,+/-1,-2}`;
- `"root projection"`, `"root image code"`, `"zero sum"`,
  `"squared norm 42"`, `"46 patterns"`, and `"32 patterns"`.

The exact frozen query strings are in `query-ledger.json`.  To preserve
that pre-search plan as frozen evidence, executed outcomes are recorded
separately and keyed one-to-one by query ID in `query-results.json`.

## Source and status rules

1. Prefer original papers, author-maintained catalogues, official graph
   tables, and current bibliographic records.  Secondary sources may locate a
   primary source but cannot by themselves establish a theorem's hypotheses.
2. Inspect the theorem, proposition, catalogue field, matrix, or page actually
   supporting an attribution.  Do not transfer a theorem for modular or
   strongly modular lattices to the weaker containment `21L* <= L`.
3. Catalogue prose may support a name, rank, determinant, minimum, or matrix
   attribution only when it explicitly states that datum.  Matrix arithmetic
   such as determinants, inverse integrality, root counts, theta
   coefficients, or isometry of discriminant forms remains delegated to the
   exact and independent verifiers unless the source explicitly states it.
4. Separate:
   - **standard ingredient located**;
   - **nearby theorem with unmet hypotheses**;
   - **exact combined result located**;
   - **no direct match found in the recorded search**.
5. A non-hit never proves novelty or openness.  The only permitted negative
   status sentence is: “No direct resolution/equivalent result was found in
   the sources searched as of 2026-07-24.”
6. Record failed services, inaccessible full texts, ambiguous snippets, and
   unverified citations.  Do not count them as searched evidence.
7. The default conclusion remains:

   ```text
   srg(99,14,1,2) existence: UNKNOWN
   n3=708 endpoint: UNKNOWN
   Wave 28 novelty: UNKNOWN
   ```
