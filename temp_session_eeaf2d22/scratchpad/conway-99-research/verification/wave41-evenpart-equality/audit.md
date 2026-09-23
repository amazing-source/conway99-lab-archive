# Wave 41 rank-26 verifier audit

Date: 2026-07-27 UTC

Verdict:

```text
seven even-part types exclude rank 25: VERIFIED_SCOPED
four all-odd types exclude rank 25:    VERIFIED_SCOPED (separate package)
universal rank_F7(M)>=26:              VERIFIED
```

## Independence and freeze

Before opening any Wave 41 discovery artifact, the verifier froze only the
independently verified Wave 39/40 local-rank, border-permutation, and rank
transport premises. It then independently wrote and ran the even-part
checker. The precomparison implementation was frozen at:

```text
d27d70af72df6f7824a0c32f15fb1f70ba32036564c903e36a991b1d88b0cf81  independent_check.py
dd0670b3d0b987f67a1b21d2cc4fb7365e1efb0f61a286d0b1f33e11827df659  test_independent_check.py
ec371dad71c794d57d4e27b21d17b08fac1d17e22167749ef797d950c18299e4  independent-results.json
```

Only after `implementation-freeze.sha256` was written were
`attempts/wave41-evenpart-equality/**` and the separately finalized all-odd
package opened.

## Mathematical audit

The full 39-block was checked in two independent normal forms:

1. a `27+12` singular symmetric block with equality core on the right kernel
   of the projected border matrix; and
2. the cubic 36-core Laplacian obtained after eliminating the triangle.

For the latter, normalize the first-fibre matching and the two cross
matchings to `P,I,I`. With second- and third-fibre matchings `Q,R` and
remaining cross permutation `F`,

```text
3I-A_core =
[ 3I-P  -I    -I  ]
[ -I    3I-Q -F  ]
[ -I    -F^T 3I-R].
```

Because `(3I-P)^-1=3I+P` over `F_7`, its Schur complement is, up to a global
sign,

```text
[ P+Q       F+3I+P ]
[ F^T+3I+P  P+R   ].
```

The direct triangle elimination separately gives

```text
rank(K39)=1+rank(3I-A_core),
```

so `rank(K39)=13+rank(H)`. For `A=P+Q`, `B=F+3I+P`, a kernel basis `N` of
`A`, and a right-kernel basis `W` of `N^T B`, equality in the Wave 40 rank-25
bound is exactly

```text
W^T R W=W^T(B^T A^- B-P)W.
```

This is the requested singular-`P+Q` equality condition. The verifier's
independent `27+12` formula produces the same invariant zero test.

## Exhaustiveness

For every even type, all observed projective signature lines were generated.
All dimension-`e` spans were canonicalized by exact RREF, every supported
bipartite perfect matching was traversed, and every resulting permutation was
directly assigned its canonical projected row space. This proves completeness
of the 164,928 minimum-projection permutations.

For each of the 52 distinct right kernels, the checker generated all 10,395
labelled perfect matchings recursively. Their induced equality forms were
computed with exact integer arithmetic modulo seven and stored as a complete
multiset. All 164,278 canonical equality targets were tested for membership.
No target occurs.

Direct dense checks for every kernel reproduce both the Schur-core rank
formula and the 39-block/core-Laplacian identity. Fifty-two constructed
symmetric nonmatching lower-right blocks attain rank 25 as positive hostile
controls.

## Discovery comparison

The discovery result hash is

```text
8a9e58aaa1073ae4a87e183f904ce7f43eaa620bbac5a6f5d1f8445dd795dc85.
```

Its manifest validates and all twelve discovery tests pass. Independent and
discovery results agree for every partition on:

- the even-part count;
- every minimum-permutation count;
- every distinct right-kernel count;
- every equality-target count;
- all 540,540 matching evaluations; and
- zero rank-25 survivors.

No even-package discrepancy was found.

## Universal composition

The all-odd verifier manifest validates at its finalized hash. Its sixteen
hostile tests pass, and its exact results prove `rank(K39)>=26` for
`1^6,1^3+3,1+5,3+3`. The even verifier proves the same for the remaining
seven partitions. The two sets are disjoint and their union is the complete
set of eleven positive partitions of six.

Hence every edge normal form has a 39-point principal block of rank at least
26. Principal-block monotonicity and the verified identity
`rank_F7(NMN^T)=rank_F7(M)` prove:

```text
Every hypothetical srg(99,14,1,2) has rank_F7(M)>=26.
```

The earlier all-odd audit correctly rejected an ancillary discovery typo
that said there were five even-part types. The correct count seven is used
throughout this package.

## Tests and scope wall

The clean full `--verify` replay regenerated the seven types and matched
`independent-results.json` exactly. The final replay passed 25 local
verifier/composition tests, twelve discovery
tests, and sixteen all-odd verifier tests. Tests include missing-type,
matching-count, direct-rank, equality-survivor, field-status, endpoint-status,
and Conway-status hostile mutations, plus current-byte freeze and full-replay
gates.

No graph, endpoint exclusion, improvement of `n3<=4158`, or novelty result is
obtained. Those claims remain `UNKNOWN` or `NOT PROVED`.
