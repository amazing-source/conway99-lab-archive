# Wave 37 branch-15 OPB adversarial audit

Verdict: **PASS for the formula artifact only**.

The 29.8 MB OPB file is canonical, metadata-bound, deterministically
compressed, accepted by the pinned Exact parser, and byte-for-byte equal to an
independent semantic reconstruction. It represents only refined branch 15,
one of 33 endpoint-compatible cases. No SAT or UNSAT conclusion exists.

## Artifact identity

```text
raw bytes:       29,827,704
raw SHA-256:     4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5
gzip bytes:      3,854,306
gzip SHA-256:    7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e
variables:       289,338
constraints:     574,615
refined branch:  15
parent branch:   4
```

The gzip has timestamp zero, empty optional fields, normalized OS byte 255,
and decompresses exactly to the raw OPB hash and byte count.

## Independent semantic reconstruction

Without importing the discovery exporter, the verifier reconstructed the
named edge and wedge variable orders, branch-15 units, branch-4 prism catalog,
coordinate equalities, and residual common-neighbor upper bounds. Every line
matched the submitted formula exactly:

| formula group | constraints | group SHA-256 |
|:---|---:|:---|
| wedge implications | 285,852 | `7c05cfb955514322eaeb730603a9434b08138fa9509e27e753a3e3a23b50f99f` |
| endpoint and refined units | 151 | `3c9dc4b41332fa09aba4f4e0db6206be1acec67b855d43e0a5b8575723c4fa54` |
| fixed-triangle prism clauses | 282,774 | `2b513f8b4f2ae4e5373a7eccd9fb08b950bcbdfb318154b9739bcf7dfae73c52` |
| coordinate equalities | 2,352 | `299a2c622eb3b04ec7fa0f4ee3bdc1bce2ae326552a01b6b911b9fc9357da3ba` |
| common-neighbor upper bounds | 3,486 | `cc191eedcafecc79d60a77ccaca17bf5640f23bebfdd65276b93be656e831870` |

The branch reconstruction independently recovers parent 4, refinement edge
`(0,2)`, and refinement literal 2. No completed-graph automorphism is assumed.

The syntax census also reproduces the submitted histograms:

```text
term lengths: {1:151, 3:286458, 5:282168, 11:336, 12:2016, 83:3486}
right sides:  {1:569113, 2:840, 10:1008, 11:168, 81:2562, 82:924}
```

## Parser replay and hard boundary

The pinned Exact binary has SHA-256
`842ac70b4e938d24f537a56513ff64ea845206c714ce34da467ce146c5c5c928`.
Running

```text
Exact --onlyparse branch-15.opb
```

returned exit code zero and identified the input as OPB. The retained
transcript is `exact-parser-evidence.txt`.

`--onlyparse` is syntax acceptance only. There is no proof log, proof-checker
verdict, assignment, decoded graph, SAT result, or UNSAT result. Even a
future checked UNSAT result for this artifact would close only one of the 33
endpoint-compatible refined cases.

The independent suite passed five tests in 10.000 seconds.

Final scoped status:

```text
branch-15 formula artifact: VERIFIED
Exact parser acceptance:    VERIFIED
branch-15 satisfiability:    UNKNOWN
remaining refined cases:    32 NOT REPRESENTED
n3=4158 endpoint:           UNKNOWN
upper bound on n3:           4158
Conway-99:                   UNKNOWN
```
