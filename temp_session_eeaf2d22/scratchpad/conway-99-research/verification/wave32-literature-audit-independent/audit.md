---
role: verifier
date_utc: 2026-07-24T09:14:35Z
git_commit: NOT_USED_PER_NO_GIT_INSTRUCTION
claim_label: VERIFIED
scope: Corrected-byte replay of the frozen Wave 32 v2 statement and literature package; verification is limited to the stated branch boundary, exact elementary consequences, source applicability, correction chronology, and bounded search accounting.
inputs:
  - path: input-freeze.sha256
    sha256: bd215eefbaa32ec1a07662fff7d5141aff91d960da8e57d77457da50861fe1da
method: Freeze corrected v2 candidate and supporting bytes; verify the correction ledger preserves v1 hashes and objections; inspect the prose and JSON records; rederive endpoint, root-complement, incidence-spectrum, and modular-determinant calculations without submitted code; replay an independent standard-library checker and tests.
command: python -B -m unittest -v test_independent_check.py && python -B independent_check.py --output independent-results.json
outputs:
  - path: independent_check.py
    sha256: 7ca5e1328f1bbc6aed83d2069b89195c08dc5e6ee67cc6499e2e9424ca7b01a1
  - path: test_independent_check.py
    sha256: 1963cffa05b26148f3d51ffd8871a893453546a964d330819aeed5026f95e8f5
  - path: independent-results.json
    sha256: f884699b464a8b1b46b63cc15546f01b72c492ae54530750fcf00226b13d913b
limitations: No complete literature database, private correspondence, unpublished manuscript, or exhaustive mathematical classification was available. No raw Wave 32 search payload was retained. A bounded no-hit is not a novelty or nonexistence certificate.
---

# Independent Wave 32 corrected-byte replay

## Verdict

`PASS_CORRECTIONS_INTEGRATED`.

I found no fatal mathematical, source-applicability, branch-exhaustion, or
status-inflation defect in the corrected v2 package. The v1 objections remain
recorded in `correction-ledger.md` and are resolved, not erased. The following
are independently verified within their stated scopes:

| Item | Verdict | Exact scope |
|---|---|---|
| eight determinant rows | `PASS` | exhaustive under the already-frozen endpoint arithmetic |
| actual-incidence branch split | `PASS` | rooted or rootless integrally indecomposable survives; rootless decomposable is excluded |
| matrix-only separation | `PASS` | Wave 31 does not exclude a decomposable free-standing matrix package |
| primitive root, divisibility, index, complement determinant | `PASS` | for an even rank-44 endpoint lattice of odd determinant |
| Petro--Phillips spectrum | `PASS` | conditional on a putative `srg(99,14,1,2)` and its actual triangle incidence |
| modular determinant veto | `PASS` | conventional `N`-modularity and strong `21`-modularity only |
| query and metadata accounting | `PASS` | the retained JSON records, not unretained search-engine responses |
| v1 correction chronology | `PASS` | five v1 hashes and all three objections retained; 15th source marked post-audit |
| current-status language | `PASS_CONSERVATIVE` | current searched record only |
| exact endpoint prior-art no-hit | `NOT_FOUND_IN_SEARCHED_SOURCES` | bounded no-hit |
| global Conway-99 status | `UNKNOWN` | unchanged |
| novelty and priority | `UNKNOWN` | unchanged |

Here `VERIFIED` labels this audit's scoped checks. It does **not** promote a
rooted endpoint, a rootless indecomposable endpoint, an actual graph, the
global existence question, or novelty.

## Frozen inputs and independence

The candidate's eight files and five supporting repository files were frozen
by SHA-256 in `input-freeze.sha256`. The independent checker validates those
bytes and the candidate's own six-entry manifest before checking any
content. It makes no network request, imports no candidate or discovery code,
and uses only Python's standard library.

The candidate manifest was internally valid: every named digest matched its
file. Seventeen independent tests passed. Source prose was inspected separately
because an offline checksum checker cannot certify what a paper says.

The supporting inputs used for mathematical cross-checks were:

| Local input | SHA-256 |
|---|---|
| `verification/wave28-glue-discriminant/audit.md` | `5c1dc7978d571a9471837b45a36663c7c457b6434800776501e4967146956b86` |
| `verification/wave31-sign-commutant/audit.md` | `f6145a3c4f4e787b23440a6ea071d606477821abab0ab8e7e5fe52042d6528a0` |
| `verification/wave28-theta-modular/audit.md` | `adc90e404735ca147bc0a5418974d8af0bde71c4ddc2dc62a8c07dee670dbfeb` |
| `verification/wave28-literature-audit/audit.md` | `ef18079970e410d114ab24752d4b738bc26ff4e6266a8cc775a4e14813fe1128` |
| `SOURCES.bib` | `3c93b322ee4b0a61cf1407fdf5b082dbb90801459300289c7097b56833914a8e` |

## 1. Exhaustive branch boundary over all eight `h`

The endpoint arithmetic gives

```text
det(B) <= 6525,  det(Q) >= 5  =>  h <= 1305,
h = 3^a 7^b,  h = 1 (mod 4),  h != 1.
```

Independently enumerating every pair `a,b >= 0` under these conditions gives
exactly

```text
{9, 21, 49, 81, 189, 441, 729, 1029}.
```

No automorphism, transitivity, or `h=729` specialization was used.

For each row, a positive-definite even integral endpoint lattice has either a
norm-2 vector or no norm-2 vector. In the latter case it is either a
nontrivial integral orthogonal direct sum or it is integrally orthogonally
indecomposable. These cases are mutually exclusive and exhaustive:

```text
rooted
or rootless decomposable
or rootless indecomposable.
```

Under **actual vertex--triangle incidence**, Wave 31 excludes the rootless
decomposable case. Therefore the two surviving actual-incidence branches,
for every one of the eight determinants, are:

1. rooted;
2. rootless and integrally orthogonally indecomposable.

The qualifier "actual incidence" is essential. The Wave 31 contradiction
uses the incidence realization to turn an integral split into a proper
coordinate sign block and then into a forbidden commuting diagonal sign
matrix. A free-standing package consisting only of `S,G,X,M,W,Q,B` has no
`N,A,Gamma` incidence layer, so that implication is unavailable. A
decomposable matrix-only realization remains `UNKNOWN`.

The v2 agent report and audit preserve this distinction in their integration
status rows. The immutable v1 protocol freeze still contains its original
short form, while `correction-ledger.md` explicitly records the required
replacement:

```text
rootless integrally decomposable actual-incidence endpoint:
VERIFIED IMPOSSIBLE
```

The replay therefore marks the v1 scope-hardening objection `RESOLVED` while
retaining its chronology.

## 2. Rooted branch: primitive, divisibility one, index two

Let `L` be an even positive-definite lattice with odd determinant `h`, and let
`r in L` satisfy `(r,r)=2`.

### Primitivity

If `r=m x` with an integer `m>=2` and `x in L`, then
`2=m^2(x,x)`. Evenness and positive definiteness give `(x,x)>=2`, which is
impossible. Thus `r` is primitive.

### Divisibility

The divisibility `div(r)=gcd{(r,x):x in L}` divides `(r,r)=2`. If it were
`2`, then `r/2` would define an element of order two in the discriminant
group `L*/L`. That group has order `det(L)=h`, which is odd. Hence
`div(r)=1`.

### Index and determinant

Put `K_r=r^perp intersect L`. The homomorphism

```text
L -> Z,  x |-> (r,x)
```

is surjective because `div(r)=1`, has kernel `K_r`, and maps `Zr` onto
`2Z`. Therefore

```text
[L : Zr direct-sum K_r] = 2.
```

The determinant-index formula then gives

```text
2 det(K_r) = [L : Zr direct-sum K_r]^2 det(L) = 4h,
det(K_r)=2h.
```

Thus a root need not split off an integral `A1`; the index-two glue is
structural, not optional.

| `h` | `det(K_r)` |
|---:|---:|
| 9 | 18 |
| 21 | 42 |
| 49 | 98 |
| 81 | 162 |
| 189 | 378 |
| 441 | 882 |
| 729 | 1458 |
| 1029 | 2058 |

This verifies the elementary rooted statements. It does not classify the
primitive ADE closure, its rootless complement, the isotropic glue, or the
marked 231-coordinate realization.

## 3. Petro--Phillips spectrum and exact hypotheses

The primary source is Robert R. Petro and Connor M. Phillips,
[*On Clique Graphs and Clique Regular Graphs*](https://arxiv.org/abs/2502.17845),
*Discrete Mathematics* 349(3) (2026), article 114862,
[DOI 10.1016/j.disc.2025.114862](https://doi.org/10.1016/j.disc.2025.114862).
Corollary 4.9 is the general spectrum transformation, and Example 4 explicitly
lists the conditional spectrum for `(99,14,1,2)`.

The hypotheses really are available from a putative target graph:

- it is 14-regular;
- `lambda=1`, so each edge lies in a unique triangle and the graph is locally
  linear;
- the number of triangles is `99*14/6=231`;
- for the vertex--triangle incidence matrix `N`,
  `NN^T=7I+A`;
- if `Gamma` joins triangles sharing a vertex, then
  `N^TN=3I+Gamma`.

The adjacency spectrum of the putative strongly regular graph is

```text
14^1, 3^54, (-4)^44.
```

Consequently `NN^T` has positive spectrum
`21^1,10^54,3^44`, so `rank(N)=99`. The nonzero eigenvalues of
`N^TN` are the same, with `231-99=132` additional zero eigenvalues.
Subtracting `3I` independently yields

```text
Spec(Gamma) = 18^1, 7^54, 0^44, (-3)^132.
```

This matches Petro--Phillips exactly. It is a **conditional
actual-incidence** result. The paper supplies no rank-44 integral lattice,
root, ADE glue, marked scale-21 frame, Schur realization, construction, or
nonexistence theorem.

Connor Phillips's
[*A Comprehensive Study of Clique Graphs and Clique Regular Graphs*](https://arxiv.org/abs/2605.22867)
was submitted to arXiv on 2026-05-19. Its introduction likewise gives the
231-triangle count and says the bounty had not been claimed. This is
supporting chronology and status evidence, not an endpoint certificate.

## 4. Modularity veto versus weak containment

The [Nebe--Sloane author-maintained modular-lattice
catalogue](https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/modular.html)
uses the conventional similarity-based definition: an integral lattice `L`
is `N`-modular only if it is isometric to `sqrt(N)L*`.

In rank 44 with Gram determinant `h`,

```text
det(sqrt(N)L*) = N^44/h.
```

An isometry therefore forces

```text
h = N^44/h,  so h=N^22.
```

The endpoint's exact levels are:

| `h` | exact level |
|---:|---:|
| 9, 81, 729 | 3 |
| 49 | 7 |
| 21, 189, 441, 1029 | 21 |

None has determinant `3^22`, `7^22`, or `21^22`. Ordinary modularity at
the exact level is therefore impossible.

Nebe's
[*Strongly modular lattices with long shadow*](https://arxiv.org/abs/math/0211232)
requires isometries to rescaled partial duals; in particular strong
`21`-modularity includes ordinary `21`-modularity and is also vetoed.
Rains--Sloane's
[*The Shadow Theory of Modular and Unimodular Lattices*](https://arxiv.org/abs/math/0207294)
likewise requires genuine modular hypotheses.

By contrast,

```text
21L* subset L
```

is only a containment. It controls the discriminant exponent but supplies no
similarity `L ~= sqrt(21)L*`, no partial-dual isometries, and no modular
automorphism. The determinant veto cannot be upgraded into a classification
of lattices satisfying the weak containment, and modular theta/shadow bounds
cannot be imported.

## 5. Query, metadata, chronology, and access accounting

The retained `query-ledger.json` has exactly 17 consecutively identified
batches, four exact strings per batch, hence 68 strings. All 68 strings are
distinct. It also records 17 lanes and eight direct-inspection events.

The corrected `source-metadata.json` has exactly 15 consecutively identified
records, `S01` through `S15`. Records `S01` through `S14` retain the original
bounded-search chronology. `S15` is explicitly identified as an inherited
pre-Wave-32 source added after the independent audit:

| chronology label | count |
|---|---:|
| `PRE_WAVE32_REPOSITORY_PRIOR_ART` | 4 |
| `PRE_WAVE32_REPOSITORY_PRIOR_ART_REINSPECTED` | 1 |
| `REUSED_FROM_WAVE28_PRIMARY_SOURCE` | 1 |
| `REUSED_FROM_WAVE28_AND_REINSPECTED_WAVE32` | 1 |
| `LOCATED_AS_EXACT_HYPOTHESIS_CONTROL_WAVE32` | 2 |
| `LOCATED_DURING_WAVE32` | 5 |
| `PRE_WAVE32_REPOSITORY_PRIOR_ART_ADDED_AFTER_INDEPENDENT_AUDIT` | 1 |

The 17-batch/68-query ledger was not rewritten. The metadata therefore
distinguishes `14` originally frozen records from `1` post-verifier inherited
addition instead of retroactively presenting the new record as part of the
original search. The counts and chronology are internally consistent. They
certify record accounting, not exhaustive coverage of the mathematical
literature.

The ledger records three access limits:

1. no authenticated MathSciNet or zbMATH connector;
2. no search-engine total-hit counts or complete ranked windows;
3. no comprehensive access to unpublished talks, private correspondence, or
   unindexed manuscripts.

Every one is marked `use_as_evidence: false`. That is correct. An access
failure or solver/search-engine limitation is not negative mathematical
evidence.

The retention declaration is also internally accurate: zero raw PDFs, zero
raw HTML, and zero raw API/search payloads were retained in the Wave 32
package. This makes the exact query list and selected-source metadata
auditable, but it prevents byte-for-byte replay of transient search results.
The package does not claim otherwise.

## 6. Source quality and applicability

The strongest positive claim is grounded in the primary Petro--Phillips
paper. The modularity boundary uses an author-maintained definition and
primary modular-lattice papers. The current-status statement is triangulated
with primary or authoritative records:

- Cesarz--Woldar,
  [*On the automorphism group of a putative Conway 99-graph*](https://alco.centre-mersenne.org/articles/10.5802/alco.418/),
  explicitly treats existence as elusive and proves conditional automorphism
  restrictions only;
- the [maintained strongly regular graph
  table](https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html) marks the
  parameter set with `?`;
- Phillips's May 2026 arXiv thesis still treats the problem as unresolved;
- Ali Keramatipour's
  [SAT report](https://arxiv.org/abs/2604.23037) reports that the tested SAT
  approach is infeasible in reasonable time, not a solution;
- the June 2026 [Shpectorov seminar
  notice](https://www.hebtu.edu.cn/a/2026/06/24/AD3624B468444197AA2464C61CBDEE63.html)
  concerns nonexistence work for `(85,14,3,2)` and only a possible analogous
  approach to Conway-99.

The scope controls on nearby lattice literature are also correct:

- [Nikulin](https://www.mathnet.ru/eng/im1677) supports standard primitive
  discriminant-form and glue machinery, not a positive-definite endpoint
  classification.
- [Reflective Integral
  Lattices](https://doi.org/10.1006/jabr.1996.0155) assumes a maximal-rank
  root system, which the rooted endpoint need not have.
- [Hemkemeier--Vallentin](https://arxiv.org/abs/math/0604320) gives an
  orthogonal-decomposition algorithm, not a rank-44 census.
- [Plesken--Souvignier](https://www.math.ru.nl/~souvi/papers/lattice.html)
  gives isometry/automorphism algorithms for supplied lattices, not an
  endpoint enumeration.
- [Wang](https://actamath.cjoe.ac.cn/Jwk_sxxb_en/EN/10.1007/s10114-025-2562-6)
  concerns the different, stronger notion of additive indecomposability and
  discriminants 2 through 5.

### V1 objections and v2 resolution

| V1 independent finding | V2 replay |
|---|---|
| `S06` reversed the published author order | `RESOLVED`: Rudolf Scharlau, then Britta Blaschke |
| `S10` compressed the decomposition algorithm's input premise | `RESOLVED`: complete generating system through the required bound is explicit |
| the 14-record metadata omitted Keramatipour | `RESOLVED`: added as `S15` with explicit post-audit chronology and no-solution boundary |

The correction ledger preserves the v1 report, metadata, audit, run-report,
and manifest hashes. The checker verifies all five historical digests and all
three objection descriptions before accepting the corrected fields. This is
a corrected-byte replay, not a silent repair.

Keramatipour remains an inherited source rather than a Wave 32 search hit.
Its addition does not change any endpoint conclusion because the report
supplies neither a construction nor a nonexistence certificate.

## 7. Current-status and novelty wall

The sentence

> No exact prior result for either surviving endpoint branch was found in the
> sources searched as of 2026-07-24.

is acceptably conservative because it is explicitly bounded by the sources
searched and by date. The exact positive prior-art hit is Petro--Phillips's
conditional triangle spectrum, which the package identifies as prior art
rather than claiming as new.

The searched record supports the statement that current inspected sources
continue to treat Conway-99 as unresolved. It cannot prove the absence of an
unindexed, inaccessible, unpublished, or extremely recent result. The three
documented access gaps and the absence of raw search payloads make a stronger
novelty claim especially unwarranted. Adding the previously omitted
Keramatipour record strengthens bibliographic accounting but cannot make the
search exhaustive.

The correct final wall is therefore:

```text
rooted endpoint:                                      UNKNOWN
rootless decomposable actual-incidence endpoint:      VERIFIED IMPOSSIBLE upstream
rootless indecomposable endpoint:                     UNKNOWN
decomposable or indecomposable matrix-only package:   UNKNOWN
actual graph realization:                             UNKNOWN
Conway-99 existence/nonexistence:                     UNKNOWN
bounded exact-endpoint literature no-hit:             NOT_FOUND_IN_SEARCHED_SOURCES
novelty and priority:                                 UNKNOWN
```

No candidate discovery was promoted by this audit.
