# Wave 42 integration audit

Date: 2026-07-27 UTC

Base commit: `ef49b60aafd67f9007f6c218c39fd50392453a1b`

Verdict: **PASS for the universal theorem `rank_F7(M)>=27` and two scoped
conditional endpoint reductions. Conway-99, `n3=4158`, a strict upper bound
below 4158, and novelty/priority remain `UNKNOWN` or `NOT PROVED`.**

## Separation and replay

Wave 42 used separate discovery, clean-room verification, and orchestration
lanes. Discovery did not certify itself.

The rank verifier froze its Wave 39--41 inputs, protocol, implementation,
hostile tests, and preliminary mathematical result before opening Wave 42
discovery artifacts. It independently reconstructed all eleven local types.
For seven even-part types it explicitly checked 1,714,426,560 labelled
permutation/matching pairs. For four all-odd types it used a structurally
different pivot/mate CSP covering 19,916,886,528,000 labelled pairs.

The first rank-verifier byte replay failed because its JSON contained
nondeterministic wall-clock timing fields. `freeze-repair.md` preserves this
chronology. Only timing metadata and unused timing statements were removed;
every mathematical field stayed fixed. The repaired result then passed a
fresh byte-exact full replay.

The joint-incidence and branch-15 verifiers likewise froze independent
implementations before discovery comparison. The joint verifier generated a
distinct positive two-fibre concurrence certificate. The branch-15 verifier
replayed the 574,615-row OPB closure and reconstructed both complete clause
sets without importing discovery code.

The focused Wave 42 suites execute 88 mathematical, hostile, and scope tests:

| Package | Discovery | Independent |
| --- | ---: | ---: |
| Rank-26 equality / universal rank 27 | 10 | 19 |
| Canonical mask-51739 joint incidence | 9 | 15 |
| Branch-15 seventh-triangle clauses | 18 | 17 |
| **Total** | **37** | **51** |

All pass. Six package manifests contain 88 entries, all hash-correct.

## Universal rank-27 theorem

For every edge-local 39-point block,

```text
rank(K39)=rank(S)+2 rank(F)+rank(D).
```

For a local partition with `e` even parts, `rank(S)=25-2e` and
`rank(F)>=e`. Thus rank 26 requires `rank(F)=e` and symmetric residual
`D` of rank one.

The independent finite searches find zero rank-at-most-one residuals in all
eleven types. Discovery and verification agree on every partition count,
1,714,426,560 explicit even pairs, 19,916,886,528,000 all-odd CSP-covered
pairs, 164,928 minimum-`F` permutations, 52 right kernels, zero survivors,
and every complete even-type permutation-stream hash.

Principal-block monotonicity and the previously verified transport therefore
prove

```text
Every hypothetical srg(99,14,1,2) satisfies rank_F7(M)>=27.
```

At `n3=4158`, exact arithmetic leaves 297 pairs
`(r3,r7)` with `12<=r3<=44`, `27<=r7<=44`, and even rank sum. In particular,
`r3=12` forces even `r7>=28`.

## Scoped canonical joint-incidence reduction

Conditional on `n3=4158`, `r3=12`, all edges type `222`, and occurrence of
canonical rank-33 mask `51739`, the 36-vertex core has components `12+24`,
balanced `4+8` per fibre. Exact Gram moments and Cauchy equality force every
outside column to use two small-component and four large-component vertices.

Every fibre's 60 nonmatching pairs is used exactly once. The unknown outside
incidence matrix is therefore a three-way matching of three labelled
60-element pair sets. Unrestricted exact filters give

```text
216000 -> 118718 -> 49736 -> 45032.
```

Two distinct exact certificates satisfy the full two-fibre concurrence
projection. No full three-fibre `B` is supplied. If one exists, its overlaps
are `458/1004/308`, and a compatible outside graph requires `96/144/0` edges
by overlap, 32 triangles, and 181 four-cycles. No compatible `H` is supplied.

## Scoped branch-15 clause reduction

The frozen branch-15 OPB forces `x2=1`, completing rooted triangle
`[1,15,17]`. Prism-freeness adds 64,932 exact negative clauses. Independent
closure simplification leaves 33,778 active clauses. The complete normalized
raw and active clause streams agree exactly between discovery and verifier.

There is no active unit or empty clause. The discovery package's 64 additional
failed-literal probes are retained as null diagnostics and are not needed for
the promoted scoped clause theorem.

## Status wall

```text
rank_F7(M)>=27:                     VERIFIED
conditional endpoint rank pairs:   297
r3=12 endpoint consequence:        even r7>=28
canonical mask-51739 reduction:     VERIFIED SCOPED
branch-15 seventh-triangle delta:   VERIFIED SCOPED
branch 15 / endpoint coverage:      UNKNOWN / 0 of 33
upper bound below 4158:             NOT PROVED
rigorous interval:                  708 <= n3 <= 4158
n3=4158 / Conway-99:                UNKNOWN
novelty and priority:               UNKNOWN
```
