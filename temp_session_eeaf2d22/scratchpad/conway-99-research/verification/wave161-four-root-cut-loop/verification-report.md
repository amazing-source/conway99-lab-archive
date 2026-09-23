# Wave161 verification report

## Verdict

`VERIFIED_WITH_SCOPE`: the Wave159 order-seven/order-eight count vector is an
exact rational feasible point of the specified fifteen-cut linear
relaxation. It is not feasible for the full four-root covariance system
because two independently replayed integer directions have strictly negative
quadratic values.

## Frozen evidence

- Wave159 manifest SHA256:
  `44b76ca9538f5a3ed9d9a1f44ef29373f0cb6e422b0886063153bdff3545ff8b`.
- All 16 Wave159 manifest entries match their current bytes.
- Wave152 before/after inventory SHA256:
  `d235e6ba2ed2297f10cb3d5cedcca06c8bebfa5941ada38ee5e096ab98a24621`.
- The inventories are byte-identical and all 42 frozen files match.
- Wave152 sealed-package manifest SHA256:
  `1fe84e8e8e52b091293a30e1b09c6772f092123803e1e62362726c6c73d1f38d`.

## Independent reconstruction

No Wave159 or Wave152 discovery Python was imported or executed. The verifier
hash-pinned the prior clean-room primitive engine at
`c8aecd00c7da53fa929b53503bf437c0d0714c79a2e85a451168ac2e85b75c88`.
From graph masks, rooted flags, and the declarative integer directions, it
rebuilt the root counts, projected first moments, order-six constants,
order-seven/order-eight coefficient streams, primitive divisors, and
canonical cut hashes.

The two fresh cuts were reconstructed exactly:

| root | flags | direction support | x7 terms | x8 terms | cut SHA256 |
|---:|---:|---:|---:|---:|---|
| 3 | 155 | 53 | 155 | 842 | `93c3dceb...8f113` |
| 12 | 178 | 49 | 79 | 573 | `8fc95276...39f525b` |

Both are strictly negative on the frozen thirteen-cut pseudowitness and zero
on the new fifteen-cut pseudowitness.

## Exact witness replay

- Nonnegative coordinates: yes.
- Order-seven support: 204.
- Order-eight support: 887.
- Order-seven total: `C(99,7) = 14,887,031,544`.
- Order-eight total: `C(99,8)`.
- Wave44 equalities: 170.
- Deletion equalities: 208.
- Marked equalities seen: 5,384.
- Ordered-edge moment entries: 2,211.
- Ordered-nonedge moment entries: 3,828.
- Exact rows: 10,313.
- Restricted rows: 10,274.
- Modular rank: 887/887 modulo 1,000,003.
- Cut inequalities: 15 nonnegative, exactly 3 active.
- Maximum denominator:
  `33121404273704148365737112224522932266944`.

The independently replayed active cuts are the prior root-12 cut
`68a099dd...1240` and the fresh root-3/root-12 cuts
`93c3dceb...8f113` and `8fc95276...39f525b`.

## Four-root refutation of this pseudowitness

The verifier reconstructed each certificate direction from its flag indices
and integer vector, checked the flag-mask semantics, rebuilt its exact
covariance form, and obtained:

| root | vector support | scaled quadratic value |
|---:|---:|---:|
| 3 | 49 | `-27011041286703517116394938226429083495309284913470656030516224` |
| 12 | 50 | `-88438068438190522607991067007701768100527095926734078733792256` |

These strict negative integers independently prove that the displayed
pseudowitness fails both blocks. The remaining roots
`0,1,7,11,13,15,30` had no stored exact negative certificate; this is not a
positive-semidefinite proof for those blocks.

## Limitations

The certificate concerns only a finite rational count relaxation. It does not
construct a graph, establish endpoint feasibility, exclude the endpoint,
improve the general `n3 <= 4158` bound, or resolve Conway-99. All of those
global conclusions remain `UNKNOWN`.
