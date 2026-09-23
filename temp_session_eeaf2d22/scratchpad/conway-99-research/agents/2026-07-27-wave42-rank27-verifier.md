# Wave 42 rank-27 clean-room verification

```yaml
role: verifier
date_utc: 2026-07-27T14:43:16Z
git_commit: ef49b60aafd67f9007f6c218c39fd50392453a1b
claim_label: VERIFIED
scope: >
  Universal rank_F7(M)>=27 for every hypothetical srg(99,14,1,2), through
  complete labelled exclusion of rank 26 in all eleven edge-local types.
```

The verifier froze its protocol, implementation, tests, and preliminary
mathematical result before opening Wave 42 discovery artifacts.

It independently regenerated 164,928 minimum-`F` permutations and 52 right
kernels, explicitly checked 1,714,426,560 even-type labelled pairs, and used
a structurally different complete pivot/mate CSP for
19,916,886,528,000 all-odd labelled pairs.  No rank-at-most-one residual
survived.

The first stored result included nondeterministic elapsed-time values, so its
byte replay failed.  The failure and original hash are retained.  Removing
only those timing fields produced a deterministic result that replayed
exactly.  Nineteen independent tests, ten discovery tests, the 21-entry
discovery manifest, and mechanical comparison all pass.  Every theorem count
and all seven labelled permutation stream hashes agree with discovery.

Therefore every 39-point block has rank at least 27, and verified rank
transport gives:

```text
rank_F7(M) >= 27.
```

This is not a Conway-99 solution.  The endpoint, upper bound below 4158,
construction, existence, novelty, and priority remain unresolved.
