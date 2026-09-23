# Wave 55 branch-15 remainder search

Status: `UNKNOWN`; the bounded run is complete and contributes zero proof
coverage.

This bounded proof-producing run targets the exact smallest open proof shard
identified and independently verified in Wave 53:

```text
branch15 AND x187=0.
```

It reused the byte-verified Wave 53 OPB and ran pinned Exact with a
120-second solver timeout setting. The run spent 116.3 seconds solving and
returned:

```text
status:             UNKNOWN
conflicts:          112,215
decisions:          807,666
propagations:       140,931,770
solutions:          0
complete cases shut: 0
```

The 488,832,021-byte partial proof is nonterminal and is excluded from
publication; `result.json` records its SHA-256. A terminal negative claim
would require strict VeriPB and CakePB replay, while a positive assignment
would require complete graph decoding and checking.

Until those gates pass, branch 15, the prism-free endpoint, and Conway-99 all
remain `UNKNOWN`.
