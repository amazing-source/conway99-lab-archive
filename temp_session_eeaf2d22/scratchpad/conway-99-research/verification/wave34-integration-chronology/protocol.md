# Wave 34 integration-chronology protocol

Date frozen: 2026-07-24

The Wave 34 rooted structural comparison verifier freezes `STATUS.yaml` at
the continuation base:

```text
commit:
0fa5b8161baf8b2a5404a67051b7d61cbc906da3

STATUS.yaml SHA-256:
feda17934162602804015e17130c029ffdba7bf0307cdf234f4a7d8979298864
```

Central Wave 34 integration necessarily changes `STATUS.yaml`. Directly
running the unchanged comparison verifier against the later integrated root
must therefore fail closed. That failure is an input-chronology event, not a
mathematical discrepancy.

The accepted replay procedure is:

1. resolve an exact integrated Git commit;
2. export its complete tracked tree with `git archive`;
3. export only `STATUS.yaml` from the frozen base commit;
4. replace that one file in the isolated exported tree;
5. verify the replacement's exact SHA-256;
6. run the unchanged 11-test rooted structural comparison suite with the full
   census enabled;
7. retain the test count, exit status, exact commits, input hash, and global
   `UNKNOWN` wall; and
8. prove that the source checkout's Git status is unchanged by the replay.

No verifier code, candidate artifact, comparison result, or other central
input may be replaced. The replay may not update a frozen hash or bypass the
verifier's own checks.

The replay verifies historical reproducibility under the verifier's exact
input contract. It does not independently certify later prose and does not
change binary solvability, `n3=708`, Conway-99, novelty, or priority.
