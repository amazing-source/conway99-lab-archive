# Wave 19 alternate frontier: conditional `n3=60`

Release state: **FROZEN CANONICAL-NEWLINE V3 /
DERIVED_PENDING_INDEPENDENT_AUDIT.**  This revision supersedes v2 manifest
`558a0cc0450058c6cd58092ac63510ae8fe20c1ac7e1cd0121302494b9c9bfc1`
for provenance-only newline normalization.  V2 had superseded v1 manifest
`adc025f3020f992f6077c8d6006031688db424aa9ffbe5f33618679f95cfd37c`
for path hygiene only.  Generation and byte-identical replay completed all
four checkpoints with empty stderr; the focused suite passed 7/7.  This lane
does not promote its own result to `VERIFIED`.

## Result boundary

This lane independently targets the equality `n3=60`.  It imports the frozen,
audited `H/L`, indexed-point, endpoint-crossing, fixed-point, and dense-subset
semantics used through Wave 18.  It does not inspect or import another Wave 19
discovery.

The proposed conclusion is conditional:

```text
n3=60:                         EXCLUDED / DERIVED
prospective n3 lower bound:    63
prospective induced C6 bound:  209349
Conway srg(99,14,1,2):         UNKNOWN
novelty:                       UNKNOWN
```

This discovery lane cannot promote its own result to `VERIFIED`.  The exact
artifacts are intended for a verifier frozen before their release.

## 1. Frozen structural reduction

At `n3=60`,

```text
sum q(T)=40,
q(T)>=2 on active labels,
d_K(T)=r-1-3q(T)>=4.
```

Exact partitioning leaves thirteen profiles.  The dense-subset argument
excludes every profile through `r=17`.

For `r=18`, equality forces all 27 indexed points to have size two and
`G[X]` to be 6-regular.  A size-two point has four meeting neighbors and
`(q(i)+q(j))/2` positive nonmeeting neighbors.  Degree six therefore forces
`q(i)=q(j)=2` at every point, contradicting each surviving `r=18` profile,
which contains a `q>2` label.

For `r=19`, `|X|` is 27 or 28.  At 27, the only nontrivial point-size profile
is `2^24 3^3`; every size-three point has its six meeting neighbors already,
but its fixed crossing sum 12 cannot be supplied by only the other two
size-three points.  At 28 the profile is `2^27 3`; the unique triple has
degree at least nine, forcing even degree sum at least 172, while the exact
spectral upper bound permits at most 170.

Thus the only remaining active profile is

```text
r=20, q=2^20, 27<=|X|<=30.
```

## 2. The `|X|=27` equality case

Spectral equality makes `G[X]` 6-regular.  The point-size profile is
`2^21 3^6`.  Each size-three point must receive its fixed crossing sum 12
from three positive meeting size-three points.  Their positive intersection
graph `J` is cubic on six vertices.  The complete labeled census has 70
members:

```text
10 copies of labeled K3,3,
60 copies of the labeled triangular prism.
```

If `J` is a prism, each of its two triangles consists of three points with a
common label, say `alpha` and `beta`.  Both labels remain after deleting the
shared label on each of the three matching edges of the prism.  The three
positive `2`-by-`2` rectangles therefore cover `alpha-beta` three times,
contradicting exact coverage zero or two.

If `J=K3,3`, name its nine shared labels by a `3`-by-`3` grid.  The nine
positive meeting rectangles cover every pair in different rows and different
columns exactly twice.  Each grid label consequently has exactly two
remaining `L`-neighbors.  Its unique size-two point has two distinct
2-factor neighbors; their rectangles give four remote endpoint appearances.
Exact twofold coverage forces both remote point-edges to have the same two
endpoints, contradicting point linearity (equivalently, the simplicity of
the indexed point family).  This closes both possible `J`.

## 3. The `|X|=28,29` cases

At 28 the point profiles are

```text
2^25 3^2 4,
2^24 3^4.
```

The first saturates the spectral degree-sum bound.  The size-three points
would have to obtain crossing sum 12 from only two large meeting partners,
whose maximum total contribution is eight.

For `2^24 3^4`, the size-two fixed sums and the spectral edge cap permit at
most one additional disjoint big-point support, or two size-two-to-big
supports.  The positive meeting relation on the four triples must therefore
contain `K4` or `K4-e`.  The common-point rule forbids both: every triangle of
pairwise-meeting points has one common label; overlapping triangles in
`K4-e` force its missing pair to meet as well, and `K4` would put one active
label in four indexed points.

At 29 the profiles are `2^28 4` and `2^27 3^2`.  Write `d_i` for induced
degrees and use the exact `-4` primitive projector

```text
E_-4=(27I-9A+J)/63.
```

For an `m`-set with `e` induced edges,

```text
sum_i z_i^2 = 63(m^2+27m-18e),
z_i = m+27-9d_i             inside,
z_i = m-9t_i                outside.
```

The size-four profile forces `e=90` and one inside coordinate `z=-52`, whose
square already exceeds the total 252.  For two triples, every branch except a
positive meeting edge forces degree at least nine at each triple and the same
`e=90` contradiction.  In the last branch `e=89`, both triple degrees are
eight.  The outside degrees give integers `y=t-3` with

```text
sum y=18, sum y^2=14,
```

impossible because `y^2>=y` for every integer `y`.

## 4. The `|X|=30` residual and zero-crossing edges

All thirty points have size two.  Let `F` be their simple cubic triangle-free
point graph on the twenty active labels.  Positive crossing edges form a
2-factor `R` on `E(F)` and obey the exact rectangle identity

```text
N A_R N^T = 2 A_L.
```

Extra induced edges with zero crossing form a graph `Z`.  They do not enter
the rectangle identity.  If `z=|E(Z)|`, the projector identity excludes
`z=5`.  At `z=4`, writing outside degrees as `t=3+y` forces

```text
sum d_Z^2 + sum y^2 = 25,
```

where the two terms are at least 8 and 25.  Hence

```text
z<=3.
```

This corrected scope is important: a girth-five-only catalog would not cover
all possible `Z`.  The final census instead uses the complete connected cubic
catalog at order twenty and every disconnected component partition.

## 5. Local hexagons and the complete cubic census

Fix a label `u`.  The three `F`-edges at `u` have two `R`-neighbors each.
Their six remote `F`-edges have endpoints in `N_L(u)`.  Exact coverage makes
those endpoints 2-regular on the six `L`-neighbors.  Independent cross-edge
matching forbids a repeated remote edge, and triangle-freeness of `F` rules
out two 3-cycles.  The remote edges therefore form a simple `C6`.

Every vertex of that cycle is at `F`-distance at least three from `u`: an
`F`-neighbor or a common-`F`-neighbor pair is forced into `K`.  Moreover the
six-neighborhood choices must be symmetric:

```text
v in N_L(u) iff u in N_L(v).
```

The pinned House of Graphs order-20 catalog contains 510,489 connected cubic
types.  Direct validation and filtering gives:

| stage | cases |
|---|---:|
| triangle-containing | 412,943 |
| triangle-free | 97,546 |
| no eligible local `C6` | 97,248 |
| local-`C6` survivors | 298 |
| no symmetric `L` selection | 295 |
| symmetric survivors | 3 |

Two symmetric survivors have twenty distinct codegree-two `K` pairs, each
forcing a different third cross-edge in `Z`; this contradicts `z<=3`.  The
last has ten point vertices with only one compatible positive support, while
`R` must be 2-regular.

For disconnected `F`, triangle-free connected component catalogs at orders
`6,8,10,12,14` give all 177 unordered unions of total order twenty.  Five
lack a local hexagon, 168 lack a symmetric `L`, and three surviving component
families again force twenty `Z`-edges.  The sole residual is two Petersen
components.

## 6. The 120 two-Petersen models

The symmetric-hexagon search yields exactly 120 `L` choices for two Petersen
graphs.  For each, the compatible support graph on the thirty point-edges is
already 2-regular, so `R` is unique; exact twofold coverage and independent
matching are checked directly.

The Petersen graph has 120 automorphisms.  The full point-graph automorphism
group has order `2*120^2=28,800`; the base `(L,R)` stabilizer has order 240.
The orbit of one base model has size 120 and equals the complete model list.
It is therefore enough to analyze `Z` up to this 240-element stabilizer.

## 7. Exact outside-Gram obstruction, including every `Z`

For the base active graph define

```text
B=12I-A_X-A_X^2+2J.
```

A full SRG completion would supply a binary cut matrix `C` with `B=CC^T`.
Every nonzero binary column `c` must:

1. lie in `col(B)`;
2. avoid every pair with `B_ij=0`; and
3. obey `(A_X c)_i <= 2-c_i`, from the target `lambda/mu` common-neighbor
   counts.

For `Z=empty`, complete enumeration leaves 72 supports, with sizes

```text
2^15, 3^10, 4^15, 5^12, 6^20.
```

The 465 equations

```text
B = sum_S m_S 1_S 1_S^T
```

have coefficient rank 72 and a unique rational solution with multiplicities

```text
(-1)^15, 0^12, 1^20, 2^10, 4^15.
```

The negative entries contradict `m_S>=0`.

There are 165 eligible zero-crossing edges.  The complete `z=1,2,3` census
has 748,825 subsets.  Entrywise nonnegativity of `B` leaves 8,935 placements,
or 66 orbits under the stabilizer.  Exact positive semidefiniteness leaves 16
orbits.  Complete binary-column enumeration and exact Gram elimination make
15 systems inconsistent.

The one remaining orbit has representative

```text
Z={(0,23),(1,22),(2,17)}.
```

Here `rank(B)=28`, there are 232 candidate binary columns, and the coefficient
rank is 174.  Assign pair weights

```text
-(0,27) -(1,25) -(2,16) +(3,16) -(3,23)
+(3,25) -(3,28) +(6,16) -(6,22) +(6,27)
-(6,29) -(8,15) -(8,17) +(8,25) +(8,27).
```

Their weighted sum on the target matrix `B` is `-6`.  On every one of the 232
candidate columns the corresponding pair-weight sum is nonnegative, with
histogram

```text
0^211, 1^18, 2^3.
```

Thus no nonnegative multiplicities can sum their column outer products to
`B`.  This is a 15-term integer Farkas certificate and eliminates the final
corrected `Z` orbit.  The complete support-size histogram is
`1^6,2^21,3^80,4^81,5^36,6^8`, and the support-list SHA-256 is
`19100d7ee88ee7e7a9fb5bbf4546066ee889c131275b275dd96e07486eeac394`.
The checker transports the Gram matrix, all 232 supports, and the integer
separator across all ten images of this orbit.

An earlier exploratory coordinate claim
`Z={(0,20),(1,22),(2,23)}` is withdrawn.  In the final checker's labeled
model it is ineligible for every one of the 120 two-Petersen `L/R` models,
and under the selected model it canonicalizes to a different orbit.  The
hard assertion that exposed this mismatch, both canonical representatives,
and the failed replay are retained in `failed-runs.md` and `run5.stderr.log`;
no unproved relabeling was used.  The separator above was freshly derived
for the exact census representative and then checked using exact integers.

## 8. Reproducibility and limitations

The final package uses only the Python standard library.  It validates pinned
catalog bytes and every graph record, writes a one-byte disposition for each
connected order-20 record, records all 177 disconnected dispositions, and
reconstructs every arithmetic, orbit, support, Gram, and Farkas count.

Retained failed routes and packaging failures are in
`attempts/wave19-alternate-frontier/failed-runs.md`.  In particular, the
invalid `A_X+3I` / least-eigenvalue `-3` scout is explicitly discarded; the
target restricted eigenvalues are `3,-4`.  The old non-isomorphic
scout-coordinate Farkas witness is also explicitly withdrawn.

Before public release, local workspace prefixes in the retained failure
prose and five failed-run stderr traces were normalized to stable
`<workspace>` placeholders.  The normalization ledger is
`attempts/wave19-alternate-frontier/public-redaction-v2.json`.  Traceback
line numbers, exception messages, and every failed route remain intact.
The checker, tests, exact results, both disposition artifacts, and successful
generation/verification logs retained their v1 SHA-256 values in v2;
consequently no mathematical replay was required for that hygiene-only
revision.

For v3, the ten remaining CRLF-bearing diagnostic, success, and test logs
were normalized to canonical LF so working-tree bytes equal the bytes Git
will publish.  Their text and semantics are unchanged; only those log hashes
changed.  The ledger
`attempts/wave19-alternate-frontier/public-newline-v3.json` records every
before/after hash and preserves the v1/v2 chronology.  The checker, test
source, exact results, and both dispositions retain their prior hashes, so no
mathematical replay was required for this provenance-only revision.

The semantic chain from the audited `H/L` framework to the local-C6
condition, the catalog completeness premise, and the implementation itself
still require independent audit.  No claim about target existence,
nonexistence, or novelty is made here.

The intended release set is frozen at the hashes below and in
`attempts/wave19-alternate-frontier/manifest.json`.  Neither the source nor
the artifacts should be edited without producing a new manifest; a
mathematical replay is additionally required if protected core bytes change.

```yaml
role: proof_b
date_utc: 2026-07-23T15:28:10Z
git_commit: a562e7e250ab99631a109d66dec62c07e27a22fb
claim_label: DERIVED
scope: conditional exclusion of n3=60 for a putative srg(99,14,1,2), including every zero-crossing Z with |E(Z)|<=3
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  agents/2026-07-23-wave18-n3-57-structural.md: fa1dde1f96aaaf2c9a90c73308afbc967fab892fe79246bf7eafa2831fea38f6
  verification/2026-07-23-wave18-n3-57-structural-audit.md: 8534456ac92fd704ad7b24f5d7d2c262ea31476132018e9d14a8e4779b27ae5d
  attempts/wave18-n3-57-structural/exact-checks.json: 76decce7f0af8e3bf2db483096a10a86321a9d7143e6123ad2081ec17d28604c
method: frozen audited H/L semantics; exact q-profile and point-size reductions; primitive-projector identities; complete pinned cubic catalogs; local-C6 and symmetric-L constraint propagation; exact automorphism orbits; exact rational PSD/Gram calculations; integer Farkas certificate
command: |
  .venv\Scripts\python.exe -B -m unittest -v attempts\wave19-alternate-frontier\test_exact_frontier.py
  .venv\Scripts\python.exe -B attempts\wave19-alternate-frontier\exact_frontier.py --output attempts\wave19-alternate-frontier\exact-results.json --connected-dispositions attempts\wave19-alternate-frontier\connected20-dispositions.txt --disconnected-dispositions attempts\wave19-alternate-frontier\disconnected20-dispositions.json
  .venv\Scripts\python.exe -B attempts\wave19-alternate-frontier\exact_frontier.py --verify attempts\wave19-alternate-frontier\exact-results.json --connected-dispositions attempts\wave19-alternate-frontier\connected20-dispositions.txt --disconnected-dispositions attempts\wave19-alternate-frontier\disconnected20-dispositions.json
outputs:
  attempts/wave19-alternate-frontier/exact_frontier.py: 960b3f85ea2bbdbf940c46875bac7520aa2b514a1068e75d419c8e489dedde7b
  attempts/wave19-alternate-frontier/test_exact_frontier.py: 5271fc8c2358872c435d68b1e0ba9c0274ea509eed261fddd6bd512b0427d427
  attempts/wave19-alternate-frontier/exact-results.json: 3e6c3016572c55aa15acc7b629a6a11b73cfce48f33e61ab1def2ebaf9b6f000
  attempts/wave19-alternate-frontier/connected20-dispositions.txt: ea4ce3e70e4e3dfc39befd952f633fc680642c5a6285d3ed08232d0d19f43cc6
  attempts/wave19-alternate-frontier/disconnected20-dispositions.json: 491e7dddd7a5d630b546faf3a86d0aedf34e80bf02bf70d9c52112082d5d1c9b
  attempts/wave19-alternate-frontier/failed-runs.md: 14ab37c9cfa928c91cf09290c990a89b040bcd56ef47aec98059d821b2e884a5
  attempts/wave19-alternate-frontier/run-metadata.json: 2e04f0c94ab017e6e36180145cdae0f119a3ce20515966eb29995b6672affd65
  attempts/wave19-alternate-frontier/public-redaction-v2.json: 5a4dc89f5d92472e36c9895a12807bc632479165a6b8378cd19813a2f66fe897
  attempts/wave19-alternate-frontier/public-newline-v3.json: 7f5f382e4f07ddb7f3e277d217b569c97ac23ebdb607c36134ede0a8a56ce9a6
limitations: conditional on the frozen audited project framework rather than a raw 99-by-99 adjacency derivation; discovery cannot verify itself; official House of Graphs completeness and nonisomorphism are external premises; no automorphism of a completed target, target resolution, or novelty conclusion
```
