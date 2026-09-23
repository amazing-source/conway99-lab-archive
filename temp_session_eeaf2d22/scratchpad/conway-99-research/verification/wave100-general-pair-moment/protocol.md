# Wave 100 clean-room verification protocol

Freeze time: `2026-07-28T03:03:16Z`.

This protocol was recorded after reading only the Wave 100 package filename
inventory and its package manifest. The discovery derivation, checker,
results, tests, README, protocol, failed routes, run report, and input freeze
were not opened.

## Frozen discovery artifact

```text
attempts/wave100-general-pair-moment/package-manifest.sha256
sha256 0dedf60c7994f842887c084bae7f6585f8fc98be568c940efb5b5ea90320bc88
```

The manifest lists nine package files; together with the manifest itself,
the discovery directory contains ten files.

## Assigned checks

Independently reconstruct and attack:

1. the rootwise ceiling/floor transition-pair bound;
2. the direction and validity of the summed-floor inequality;
3. the identity `sum_o f_o = 6P`;
4. the substitution producing coefficient `-5*n3`;
5. the antipodal/even rounding for all 1,387 arithmetically compatible
   `(n3,P)` rows;
6. the status boundary, especially whether a general strict `n3` upper bound
   or graph nonexistence is actually proved.

The verifier must seal an independent result before opening any Wave 100
discovery content. Discovery code will not be imported or executed by the
independent reconstruction.

## Verdict policy

- `VERIFIED` requires exact independent agreement and fail-closed scope.
- A repairable error receives `CORRECTION`.
- A false central claim receives `REFUTED`.
- No finite arithmetic scan alone proves graph existence or nonexistence.
