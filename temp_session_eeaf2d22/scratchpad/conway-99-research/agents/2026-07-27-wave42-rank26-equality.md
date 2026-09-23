# Wave 42 rank-26 equality classification

```yaml
role: proof_a
date_utc: 2026-07-27T14:01:37Z
git_commit: ef49b60aafd67f9007f6c218c39fd50392453a1b
claim_label: CANDIDATE
scope: >
  Complete discovery-side classification of rank-26 equality for all eleven
  edge-local partitions of six, without a completed-graph automorphism
  restriction.
method: >
  Frozen Wave 41 singular Schur decomposition; complete minimum-border
  enumeration and all 10,395 labelled third-fibre matchings for seven
  even-part types; unique first-nonzero-diagonal pivot CSP implicitly
  covering all 12! labelled borders for every matching in four all-odd
  types; exact rank-one and full-block controls.
limitations:
  - Discovery cannot verify itself.
  - No graph or global compatibility certificate is constructed.
  - The endpoint n3=4158 remains UNKNOWN.
  - No upper bound below n3<=4158 is proved.
  - Novelty and priority remain UNKNOWN.
```

## Candidate result

Wave 41 gives, for a type with `e` even parts,

```text
rank(K39) = (25-2e) + 2 rank(F) + rank(B),
rank(F) >= e.
```

Hence rank 26 requires exactly `rank(F)=e` and a symmetric residual `B` of
rank one.

The seven even-part searches enumerate every minimum-`F` labelled
permutation and all 10,395 labelled third-fibre matchings. The four all-odd
searches use the identity

```text
B_ik B_pp = B_ip B_pk
```

at the unique first nonzero diagonal pivot. This yields a complete
all-different CSP over all `12!` labelled borders for each matching, rather
than an automorphism-restricted sample.

All eleven types have zero rank-one residuals. The discovery-side candidate
is therefore

```text
rank_F7(K39) >= 27
rank_F7(M) >= 27.
```

The explicit even-part lane covers 1,714,426,560 labelled pairs. The exact
all-odd CSP covers 19,916,886,528,000 labelled pairs implicitly, for
19,918,600,954,560 pairs across all types. The composed discovery result is
`94473b4c9f35184376765f76ab16646956222112836f49bcb22e950142a863a1`.

This is not a Conway-99 solution and must remain `CANDIDATE` until a clean
verifier independently reconstructs both finite lanes and the pivot-CSP
completeness proof.

## Artifacts

The complete package is in `attempts/wave42-rank26-equality/`. It contains
the checker, eleven atomic results, composed result, proof, failed routes,
tests, exact input freeze, run report, and SHA-256 manifest.
