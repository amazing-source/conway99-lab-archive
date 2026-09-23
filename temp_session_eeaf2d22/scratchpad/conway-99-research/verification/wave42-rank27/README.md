# Wave 42 clean-room rank-27 verification

Verdict: **PASS**

```text
Every hypothetical srg(99,14,1,2) satisfies rank_F7(M) >= 27.
```

This package independently verifies the Wave 42 candidate after freezing its
protocol, implementation, tests, and preliminary mathematical result before
opening any Wave 42 discovery artifact.

## Exact reduction

For every labelled edge-local 39-point block,

```text
rank(K39)
  = rank(S) + 2 rank(F) + rank(Z^T W_R Z-Z^T U^T X).
```

If the edge type has `e` even parts, the verified Wave 39--41 inputs give
`rank(S)=25-2e` and `rank(F)>=e`.  Therefore rank 26 is possible exactly
when `rank(F)=e` and the symmetric residual has rank one.

The verifier independently regenerated all eleven edge types, all 164,928
minimum-`F` labelled permutations, 52 right kernels, and all 10,395 labelled
third-fibre matchings.

For the seven even-part types it explicitly applied a correct exact
rank-at-most-one predicate to

```text
164,928 * 10,395 = 1,714,426,560
```

labelled pairs.  Failing two-by-two principal minors provide exact rejection
certificates; every survivor of those filters is checked by the complete
nonzero-diagonal pivot identity.  There were zero rank-at-most-one residuals.

For the four all-odd types a structurally independent pivot/mate CSP loops
over the residual pivot and its mate in `R`, then reconstructs the only
possible matching while exhaustively enumerating the labelled border
bijection.  Any rank-one residual must occur in one of these branches.  The
CSP covers

```text
4 * 12! * 10,395 = 19,916,886,528,000
```

labelled pairs and closes every branch with zero leaves.  No automorphism of
a completed graph is assumed.

## Independent comparison

The discovery result has SHA-256

```text
94473b4c9f35184376765f76ab16646956222112836f49bcb22e950142a863a1.
```

The repaired deterministic verifier result has SHA-256

```text
a207b1bcc267aaefdea704c1173e3ed01a81029507d3bc76aa295caccad03be4.
```

Every partition count, pair count, right-kernel count, and rank-one survivor
count agrees.  All seven complete labelled minimum-`F` permutation stream
hashes agree.  The discovery method fixes `R` and searches border
permutations; the verifier fixes the pivot mate and reconstructs `R`, so the
two all-odd CSPs are structurally different.

## Freeze chronology

The first clean-room result was frozen before comparison at

```text
bb4c1fa6d8c46343df26caa475895906d22c8f80000e8225e6a1f4bb9eb760eb.
```

Its first required byte replay failed because wall-clock `elapsed_seconds`
values were serialized.  `freeze-repair.md` records the failure.  The repair
removed only nondeterministic timing metadata and unused timing statements;
all mathematical counts and the theorem were unchanged.  The repaired
result then passed a byte-exact full replay.

The final local suite has 19 passing tests.  The discovery suite has 10
passing tests, its 21-entry manifest validates, and mechanical comparison
reports zero discrepancies.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave42-rank27 -p "test_*.py" -v

.\.venv\Scripts\python.exe -B `
  verification\wave42-rank27\independent_check.py `
  --verify verification\wave42-rank27\independent-results.json

.\.venv\Scripts\python.exe -B `
  verification\wave42-rank27\comparison_check.py `
  --verify verification\wave42-rank27\comparison.json
```

## Scope wall

```text
universal rank_F7(M)>=27:       VERIFIED
endpoint n3=4158:               UNKNOWN
general upper bound below 4158: NOT PROVED
best rigorous interval:         708 <= n3 <= 4158
Conway-99 existence:            UNKNOWN
graph construction:             NONE
novelty and priority:           UNKNOWN
```
