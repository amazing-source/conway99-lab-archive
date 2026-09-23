# Wave 40 integration audit

Date: 2026-07-27 UTC

Base commit: `6b28af70c67f062d687251494a047debe70a246f`

Verdict: **PASS for the independently verified universal rank theorem and
the scoped edge-coupling identities; the endpoint, general upper bound,
Conway-99, novelty, and priority remain `UNKNOWN` or `NOT PROVED`.**

## Integrated evidence

The Wave 40 replay executed 90 mathematical and adversarial tests:

| Package | Discovery | Independent |
| --- | ---: | ---: |
| Rank-22 equality stepping stone | 13 | 15 |
| All-type third-fibre rank completion | 18 | 16 |
| Global edge-type and one-quotient lift coupling | 15 | 13 |
| **Total** | **46** | **44** |

Every test passed. The exact result files and finite certificates regenerated
byte-identically. Seven discovery/verifier package manifests bind 53 files:
six mathematical packages plus the bounded literature package. Strict JSON
and YAML parsing, unique claim and obligation identifiers, evidence-path
resolution, local Markdown links, privacy markers, and `git diff --check`
are part of the final publication gate.

The final integration sweep over files selected by
`git ls-files --cached --others --exclude-standard` parsed 298 JSON files and
131 YAML files with duplicate-key rejection, found 119 unique claim identifiers
and 105 unique obligation identifiers, resolved every evidence path, checked
24 Wave 40 and central Markdown files for local-link targets, found no Wave 40
cache directories or privacy markers, and passed `git diff --check`.

## Promoted universal theorem

For an arbitrary edge, the Wave 39 27-point block has one of eleven types
indexed by a partition of six. If `e` is the number of even parts, its rank
over `F_7` is `25-2e`.

The twelve vertices in the third triangle fibre give border columns indexed
by a permutation between the two endpoint fibres. If `H` is a kernel basis
for the 27-point block and `U` is the border matrix, a symmetric congruence
proves

```text
rank([[S,U],[U^T,W]]) >= rank(S)+2 rank(H^T U)
```

for every lower-right block `W`. A discovery implementation and a clean-room
verifier independently cover all third-fibre permutations through complete
projective-subspace enumeration and exact bipartite matching. Both obtain

```text
min rank(H^T U)=e
```

for all eleven types. Therefore every hypothetical Conway graph satisfies

```text
rank_F7(M)>=25.
```

The earlier endpoint-only `rank_F7(M)>=22` stepping stone is separately
verified but numerically superseded. At `n3=4158`, the rank-25 theorem leaves
330 arithmetic `(r3,r7)` pairs instead of 429; if `r3=12`, then `r7` is even
and at least 26.

## Verified scoped endpoint coupling

At the prism-free endpoint, the opposite-edge and triangle-relation graphs
have a natural edge bijection. The four edge-local types form faces of a
closed two-dimensional incidence complex. The exact face counts are

```text
F4=3a+b, F6=2c, F8=b, F12=d.
```

The Euler identity permits negative characteristic and does not contradict
the all-`222` case.

Around one all-`222` base triangle, an independent normalized enumeration
reconstructs all 4,050 quotient forms and the exact ternary rank distribution

```text
11:8, 12:1, 13:400, 14:46, 15:2616, 16:979.
```

For the cubic 36-vertex neighbor core `A_X`, exact Schur elimination gives

```text
rank_F7(K_39)=1+rank_F7(3I-A_X).
```

For one canonical rank-11 quotient, all `2^18` endpoint-pairing masks are
checked. Exactly 37,378 are triangle-free. Their raw cubic-core ranks are
`32:264,33:7348,34:29766`, hence their 39-block ranks are
`33:264,34:7348,35:29766`. This is a complete census for one quotient only,
not a universal rank-33 theorem.

## Literature boundary

The source audit identifies Gray Taylor's pinned 2020 notebook as exact prior
art for the 27-point edge-neighborhood scaffold and its eleven types. General
`p`-rank/Smith-form methods for `aA+bJ+cI` are also prior art. No exact
equivalent of the universal rank-25 theorem was located in the bounded corpus
searched through 2026-07-27. This nonhit does not establish novelty or
priority; both remain `UNKNOWN`.

## Status wall

No graph, complete SAT assignment, endpoint-wide UNSAT proof, completed
solve--cut--check sequence, prism-forcing theorem, or general upper-bound
improvement exists. Hence:

```text
rank_F7(M)>=25:                    VERIFIED
conditional endpoint rank pairs:   330
branch 15 / endpoint coverage:      UNKNOWN / 0 of 33
upper bound below 4158:             NOT PROVED
rigorous interval:                  708 <= n3 <= 4158
n3=4158 / Conway-99:                UNKNOWN
novelty and priority:               UNKNOWN
```
