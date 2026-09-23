# Wave 189 proof A: orbit-closed star translations

## Status

`DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

Closing private-label extraction circuits under the Wave 180 exact-three
companion involution gives the uniform conditional circuit bound

```text
Q>=4852.
```

The coefficient certificate first proves `Q>=4851`.  Equality would force
1,386 selected anticomplete triangle-stars to partition all 4,158 nonedges
and would force all 2,079 canonical quadrilateral supports to be
checkerboard circuits.  Inside each selected `3+6` leaf translate,
subtracting its canonical checkerboard relation produces a new `2+5`
weight-seven relation and hence a fourth circuit for the same label,
contradicting equality.

```yaml
role: proof_a
date_utc: 2026-07-29T02:22:37Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: private-label circuit
  extractions closed under exact-three companionship, Q>=4851, complete
  equality-face analysis, and strict exclusion giving Q>=4852.
inputs:
  attempts/wave189-orbit-closed-star-translations/package-manifest.sha256: d62ce505ebbaa7bd3799c05a6f0ac50ed920fdd519044e287bada2cb582e39d2
method: >-
  Ternary majority-star translation, minimal-cover privacy, companion-orbit
  closure, type-two endpoint-center separation, exact coefficient
  combination, anticomplete triangle-star design identities, and local
  subtraction of a checkerboard conic relation. No graph, cover, code, SAT,
  configuration, or isomorphism search.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave189-orbit-closed-star-translations\exact_check.py --verify
  attempts\wave189-orbit-closed-star-translations\exact-results.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave189-orbit-closed-star-translations\test_exact_check.py
outputs:
  - attempts/wave189-orbit-closed-star-translations/
  - agents/2026-07-29-wave189-orbit-closed-star-translations-proof-a.md
limitations:
  - Independent verification is required before promotion.
  - All claims are conditional on the prism-free rank-11 endpoint.
  - The exact checker replays scalar and local F3 identities, not graph or
    cover existence.
  - The result supplies no incompatible upper bound for Q.
  - Rank 11, endpoint existence, strict n3 improvement, external novelty,
    and Conway-99 remain UNKNOWN.
```

## Exact consequences

The selected cover, its `n_3` distinct triple companions, and the
orbit-closed extraction pool are disjoint by private-label ownership.  If
`I` is the private-label row, the exact coefficient identity is

```text
12Q
 >=7I+4n_1+2(p_2-n_2)+(3n_3-p_3)+3p_2
 >=14*4158.
```

Thus `Q>=4851`.  The strict local relation described above excludes
equality.

Adding the 693 verified edge-isolated projective circuits gives 5,545
projective circuit classes and therefore

```text
B_4+B_5+B_6+B_7+B_8+B_9>=11090
```

from circuits alone.  The verified Wave 188 bound `18018`, which counts all
short dual words including noncircuits, remains numerically stronger.

The sealed derivation, equality design, null controls, exact replay, tests,
and hashes are in
`attempts/wave189-orbit-closed-star-translations/`.
