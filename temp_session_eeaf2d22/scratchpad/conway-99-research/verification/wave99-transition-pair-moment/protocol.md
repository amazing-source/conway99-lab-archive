# Wave 99 clean-room verification protocol

Freeze time: `2026-07-28T02:56:04Z`.

The verifier recorded this protocol before opening the Wave 99 derivation,
checker, results, tests, README, or failed-routes files.

## Frozen discovery artifact

```text
attempts/wave99-transition-pair-moment/package-manifest.sha256
sha256 e3a30e37bbf08dcd60e4fff7df6f8f4e51780987ba3446e96ff136954e94a9e6
```

The discovery manifest listed ten files. Their contents were not inspected
before this freeze. The discovery input freeze named the verified Wave 90
discovery and verifier packages and the verified Wave 86 package.

## Assigned clean-room checks

Starting from the rooted transition definitions and the verified imported
short-vector data, independently reconstruct and attack:

1. the transition and seed sets, without importing discovery code;
2. the claimed per-transition co-incidence cap 18;
3. especially the assertion that two transitions with the same triple,
   together with the fixed transition, violate the target's
   \(\lambda=1\) common-neighbor condition;
4. whether all eligible centers are counted, without loss or duplication;
5. the multiplicity identity involving \(\sum\binom j2\);
6. the rational pointwise moment certificate and every denominator/sign;
7. the conversion from rooted/sign data to the claimed
   \(N_{14}\le4950\), including the factor between roots, signs, and
   supports;
8. the Wave 86 weighted rearrangement
   \[
   407N_{16}+43N_{18}\ge2165002;
   \]
9. scope separation between a `P=0` branch and the general conditional
   rank-28 row.

## Status policy

- The discovery receives `VERIFIED` only if every exact claim is reproduced
  independently and no scope inflation is found.
- A repairable error is `CORRECTION`; a false central claim is `REFUTED`.
- No verifier result constructs the target graph or resolves Conway-99.
- The verifier will compare with discovery files only after producing an
  independent machine-readable result.
