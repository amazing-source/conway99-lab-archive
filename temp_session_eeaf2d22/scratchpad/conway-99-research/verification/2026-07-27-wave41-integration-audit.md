# Wave 41 integration audit

Date: 2026-07-27 UTC

Base commit: `4f1754a28723a8e0e4ea3025312cd264b1b117d2`

Verdict: **PASS for the universal theorem `rank_F7(M)>=26` and the scoped
conditional all-`222` theorem; the endpoint, an upper bound below 4158,
Conway-99, novelty, and priority remain `UNKNOWN` or `NOT PROVED`.**

## Separation and replay

Wave 41 used independent discovery, clean-room verification, and
orchestration. Discovery did not certify itself.

The primary rank-26 verifier froze its Wave 39/40 premises, implementation,
tests, and result before opening Wave 41 discovery artifacts. It independently
derived singular Schur equality, covered all seven even-part types, and then
composed its result with a separately frozen all-odd verifier. A secondary
verifier used a different pivot-branch/vectorized equality audit and covered
all eleven edge types.

The integrated Wave 41 suites execute 128 mathematical and hostile tests:

| Package | Discovery | Independent |
| --- | ---: | ---: |
| All rank-eleven all-`222` quotient lifts | 19 | 14 |
| All-odd full-matching equality and compact kernel | 10 | 16 |
| Seven even-part equality types | 12 | 25 |
| Secondary universal rank-26 audit | 0 | 20 |
| Two-triangle overlap relaxation | 3 | 0 |
| Proof-producing propagation audit | 9 | 0 |
| **Total** | **53** | **75** |

Every listed test passes. Discovery and verifier exact-result files
regenerate. All package manifests validate.

The primary verifier initially exposed two verifier-side artifact defects:

1. an incorrect synthetic positive-control lift; and
2. three stale atomic journals using an older, mathematically equivalent
   matching-core serialization.

Neither affected the finite incompatibility counts. Both were repaired before
promotion. A final full `--verify` replay regenerated all seven atomic cases
and the assembled result byte-exactly. The final test suite gates the
implementation freeze and the recorded replay success.

## Universal rank-26 theorem

For every edge, Wave 40 gives a 39-point principal block with rank at least
25 over `F_7`. Edge-local normal forms are indexed by the eleven positive
partitions of six.

For the four all-odd types, `P+Q` is invertible. Exact Schur equality either
has no diagonal-supported permutation or, in the `3+3` case, has one
permutation whose forced third-fibre target is not a perfect matching. The
clean-room all-odd verifier therefore proves rank at least 26 for all four
types.

For the seven types with an even part, the primary verifier independently
reconstructed the equality condition

```text
W^T R W = W^T(B^T A^- B-P)W,
```

where `A=P+Q`, `B=F+3I+P`, and `W` spans the right kernel of the projected
border. Its exact complete census is

```text
minimum-projection permutations: 164928
distinct right kernels:               52
distinct equality targets:        164278
grouped matching evaluations:      540540
rank-25 survivors:                       0.
```

The secondary verifier reconstructs the same conclusion with independent
canonical signatures. For one-even-part types it partitions all labelled
third-fibre matchings into eleven exact pivot branches; for the smaller
two- and three-even-part types it performs vectorized complete matching
censuses. Its final exact replay and twenty hostile tests pass.

All eleven types therefore have a 39-point block of rank at least 26.
Principal-block monotonicity and the independently verified transport

```text
rank_F7(N M N^T)=rank_F7(M)
```

prove

```text
Every hypothetical srg(99,14,1,2) satisfies rank_F7(M)>=26.
```

At `n3=4158`, this removes the sixteen pairs with odd `r3` and `r7=25`, so
the endpoint arithmetic census falls from 330 to 314 pairs.

## Scoped all-222 boundary theorem

Conditional jointly on

```text
n3=4158,
rank_F3(M)=12,
every graph edge having type 2+2+2,
```

the clean-room quotient verifier proves that all eight normalized
rank-eleven quotients form one strict fibre-coloured isomorphism class. Each
has exactly 37,378 triangle-free lifts, with

```text
rank_F7(K39): 33:264, 34:7348, 35:29766.
```

Thus every base-triangle block has rank at least 33, and endpoint parity
sharpens the branch to even `r7>=34`. The assumptions remain unproved.

The discovery-only lift counts for quotient ranks 12 through 16 were outside
the clean-room verifier's scope and are not promoted.

## Exact failed routes retained

Every graph vertex supplies a compact kernel vector

```text
h_v=(A+4I)e_v.
```

The three vectors for a base triangle are independent, supported in its
39-point block, and annihilated by all legal outside columns. This is a
structural obstruction to adding nominal local ranks.

One exact two-triangle individual-column relaxation glues two rank-33 blocks
on their forced 19-vertex overlap but has minimum kernel-signature span one,
giving only rank 35. It omits simultaneous `BB^T`, `BH`, outside regularity,
and full SRG equations.

The branch-15 generalized-unit closure forces 830 variables but leaves 3,312
of 3,486 primary edges unset. Both polarities of 32 high-pressure variables
reach noncontradictory fixed points. Endpoint proof coverage remains `0/33`.

## Status wall

```text
rank_F7(M)>=26:                    VERIFIED
conditional all-222, r3=12 floor: even r7>=34
conditional endpoint rank pairs:  314
branch 15 / endpoint coverage:     UNKNOWN / 0 of 33
upper bound below 4158:             NOT PROVED
rigorous interval:                  708 <= n3 <= 4158
n3=4158 / Conway-99:                UNKNOWN
novelty and priority:               UNKNOWN
```
