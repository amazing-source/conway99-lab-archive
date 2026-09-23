# Wave23 source-first literature and status audit

Cutoff: `2026-07-23`

## Bottom line

The inspected current primary and authoritative sources still treat the
existence of `srg(99,14,1,2)` as open. This is current-source status evidence,
not a proof that no unindexed resolution exists; both existence and
nonexistence therefore remain `UNKNOWN`.

For the exact `n3` used in the project, the literature audit confirms:

```text
n3 = the number of induced N3 six-vertex subgraphs,
N3 = two vertex-disjoint triangles joined by exactly two independent
     cross-edges,
induced_C6 = n12 = 209286 + n3.
```

`n3` is not the total number of triangles. A putative target has exactly
`99*14/6=231` triangles.

The strongest explicit inequality in the inspected Reimbayev lower-bound
paper is only `n3>=0`. An older Makhnev result excludes the `n3=0` condition
for the target; combining that cited result with the published relation
`3n1+n3=4158` gives the derived prior necessary bound `n3>=3`. The number
`3` is an audit synthesis, not a theorem stated in `n3` notation.

No inspected source or enumerated exact search produced `n3>=708`,
`induced_C6>=209994`, or the complete Wave23 endpoint route. That finding is
only `BOUNDED NON-DISCOVERY`. Literature novelty remains `UNKNOWN`.

| Frozen claim | Result |
|---|---|
| S1: exact target is existence of `srg(99,14,1,2)` | `CONFIRMED` |
| S2: inspected current sources still list/treat it as open | `CONFIRMED`, with indexing caveat |
| S3: prior `n3` lower-bound chronology | `CONFIRMED` as described above |
| S4: `induced_C6=209286+n3` | `CONFIRMED` |
| S5: prior `n3>=708` or `induced_C6>=209994` | `BOUNDED NON-DISCOVERY` |
| S6: prior full determinant/index, exact eigenvalue-product, even-unimodular endpoint argument | `BOUNDED NON-DISCOVERY` |
| Global novelty of the Wave23 result or method | `UNKNOWN` |

## Separation and frozen input

Before opening the Wave23 proof report, the literature role wrote and hashed
`preinspection-query-plan.md`. Its preinspection SHA-256 is:

```text
9e75b30797064af8d9dc04ba27afa555fc5ec8214809756ffc7eddba65fb637f
```

Only after the source-first search and primary-source inspection was the
Wave23 report opened for exact-claim comparison. The inspected report bytes
were:

```text
agents/2026-07-23-wave23-index-pranks.md
sha256 7c62f9eb1d61a036c3dc415572a4ada58046410cb40e4455f7ec8256ec9c1a00
```

This role did not verify the Wave23 proof and does not promote its claim.

## Exact identity and object normalization

Reimbayev's 2024 paper, [The Lower Bound for Number of Hexagons in Strongly
Regular Graphs with Parameters lambda=1 and
mu=2](https://arxiv.org/abs/2409.10620v1), defines `n_i` as counts of the
induced six-vertex types in its Figure 6, identifies `n12` as a hexagon, and
derives

```text
n12 = (1/12) n k (k-2) (2k^2-21k+53) + n3.
```

Its theorem then uses only `n3>=0`. The current
[six-vertex classification v2](https://arxiv.org/abs/2508.03377v2) repeats
the identity, explicitly keeps `n3` as a free variable, and depicts `N3` as
two disjoint triangles joined by a two-edge matching. Thus `n12` is an
induced-`C6` count and `n3` is the count of the displayed induced pattern,
not a triangle count.

At `(n,k)=(99,14)`,

```text
(1/12)(99)(14)(12)(2*14^2-21*14+53)
  = (99)(14)(151)
  = 209286.
```

Therefore

```text
induced_C6 = n12 = 209286+n3,
209286+705 = 209991,
209286+708 = 209994.
```

## Prior lower-bound chronology

### Makhnev (1988): exclusion of the zero case

The authoritative MathNet record for A. A. Makhnev,
[Strongly regular graphs with lambda=1](https://www.mathnet.ru/eng/mzm4220),
records the 1988 Mathematical Notes article and DOI
`10.1007/BF01158426`. Its indexed scope treats graphs in which no two
triangles are joined by exactly two edges and excludes the target under that
condition. For a `lambda=1` graph, cross-edges between disjoint triangles
form a matching, so this is the `n3=0` case.

Reimbayev's six-vertex relation gives, for the target,

```text
3n1+n3 = (1/4)(99)(14)(12) = 4158,
```

hence `3|n3`. Makhnev's conditional zero-case exclusion and this divisibility
yield the derived prior necessary bound

```text
n3>=3
```

for any putative target. This audit could inspect the authoritative
bibliographic record and indexed abstract scope, but the MathNet page failed
direct opening with a Unicode-decoding error; the full text was not
machine-readable here. The `n3>=3` wording is an inference from cited results,
not a quotation from Makhnev.

### Reimbayev (2024): explicit lower-bound theorem

The 2024 paper's stated proof uses `n3>=0`, producing

```text
induced_C6>=209286
```

for the target parameters. Its [journal
PDF](https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf) and arXiv
v1 agree on the identity used here.

### Reimbayev (2025): six- and seven-vertex continuations

The [six-vertex v2 paper](https://arxiv.org/abs/2508.03377v2) leaves `n3`
free and states no positive lower bound. The [Hamiltonian order-seven
paper](https://arxiv.org/abs/2511.06572v1) retains `n3` and `h11` as free
parameters and obtains

```text
2n3 <= h11 <= 4n3.
```

That relation does not force a positive `n3` lower bound. Neither source
contains `705`, `708`, `209991`, or `209994` in the target sense.

### Project results are not literature priors

The repository's Wave20 `n3>=705` result and Wave23 proposed exclusion of the
`705` endpoint are project derivations, not prior literature. The literature
role records their exact claims only to define the comparison target.

## Current open-status evidence

The status conclusion is triangulated, rather than inferred from a search
engine snippet:

- Cesarz and Woldar's peer-reviewed 2025 article,
  [On the automorphism group of a putative Conway
  99-graph](https://alco.centre-mersenne.org/articles/10.5802/alco.418/),
  calls existence an elusive open problem. Its results restrict possible
  automorphism groups and do not impose an automorphism on an arbitrary
  putative graph.

- Keramatipour's [arXiv v2 of
  2026-04-28](https://arxiv.org/abs/2604.23037v2) explicitly defines
  Conway-99 as an open problem and reports that the studied SAT approach does
  not settle it.

- Phillips's [2026-05-19 thesis
  v1](https://arxiv.org/abs/2605.22867v1) says the bounty has yet to be
  claimed and again poses the existence question.

- Brouwer's maintained
  [51-100 parameter table](https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html)
  marks the row `(99,14,1,2)` with `?` and lists restricted eigenvalues
  `3^54` and `-4^44`.

No inspected primary source supplied a construction, a nonexistence
certificate, or an unrestricted proof resolving the exact target. The
defensible statement is therefore:

> As of the cutoff, current inspected primary and authoritative sources
> continue to treat the target as open; the underlying existence question
> remains `UNKNOWN`.

## Exact Wave23 comparison

The Wave23 report claims, conditional on a putative target and its audited
Wave20/Wave21 premises:

```text
n3 != 705,
therefore n3>=708,
therefore induced_C6>=209994.
```

The compared structural route is:

1. a rank-44 projector lattice and a positive integral self-adjoint
   endomorphism `B`;
2. endpoint trace and congruence information at `n3=705`;
3. a lower bound on `tr(B^2)`;
4. a two-moment optimization of the product of the positive eigenvalues,
   described through KKT/two-value spectra and rational endpoint checks;
5. determinant/index reduction; and
6. elimination of the last index by an even positive-definite unimodular
   rank/signature obstruction.

The exact-number searches and in-document searches found none of
`n3>=708`, `209994`, `209,994`, the target-specific `tr(B^2)` endpoint, a
target `det(B)` endpoint, or the complete determinant/index plus
eigenvalue-product plus even-unimodular chain.

Nearby concepts do occur in the literature:

- Petro and Phillips's [clique-graph
  paper](https://arxiv.org/abs/2502.17845v1) conditionally derives the
  putative triangle-graph spectrum
  `18^1,7^54,0^44,(-3)^132`.

- Ducey et al.'s [critical-group
  paper](https://arxiv.org/abs/1910.07686v1) uses Smith normal form and
  unimodular matrix operations around the target parameters.

These are ingredient-level neighbors, not the exact Wave23 endpoint
argument. Their existence also means that broad words such as `lattice`,
`determinant`, or `unimodular` cannot establish novelty.

The correct conclusion is:

```text
exact numerical/method match: BOUNDED NON-DISCOVERY
global novelty:               UNKNOWN
Wave23 mathematical validity: NOT ASSESSED BY LITERATURE ROLE
```

## Citation trail and bounded coverage

The citation-API trail from the 2024 hexagon paper identified three primary
follow-ups:

```text
arXiv:2508.03377  six-vertex classification
arXiv:2511.06569  nonexistence of srg(19,6,1,2)
arXiv:2511.06572  Hamiltonian order-seven subgraphs
```

Each was inspected. The order-19 paper concerns a different parameter set;
the other two are covered above. Citation queries for the six-vertex paper,
Hamiltonian paper, and Keramatipour v2 returned no citing records at retrieval.
The Cesarz-Woldar trail returned two unrelated works and no target result.

Semantic Scholar was used only as a discovery aid. Its citation data can lag
and is incomplete. Exact arXiv searches, exact-phrase web searches, source
TeX searches, an official conference abstract, and maintained-table checks
were also used. The complete exact query list, source versions, URLs, byte
lengths, and SHA-256 values are in `source-query-ledger.json`.

## Acquisition limitations and cache policy

Two acquisition failures were retained in the evidence trail:

- An initial `2511.06572v1` PDF fetch was observed as zero bytes and was not
  retained. A fresh official fetch succeeded at 467,585 bytes, SHA-256
  `d98d474ef277b6a32fc4125690c75d3808450225b0657dbd46290673b7a014f7`;
  the independent e-print/source acquisition succeeded at 272,578 bytes,
  SHA-256
  `10f8d9ea09dc72f4ca6bce4e9427ff1df32718d2978bb35a16db1af3c27cc39a`.

- An incorrect EJAAM `/volumes/...` route returned 880 bytes of HTML,
  SHA-256
  `1a85d6a1254fdb12a489ee8d3cf1b0c08c62d3a1582e88a7d039d7662cfabf3f`.
  The official `/articles/...` PDF succeeded at 372,641 bytes, SHA-256
  `484ff4bbcf13ea26d478baa4c24b97f6996ac3fc35ef8459c15fb61b61b98521`.

The entire `verification/wave23-literature-audit/sources/` tree is a
**disposable audit cache**. It includes third-party PDFs, source archives,
extracted trees, API responses, and table snapshots. It is not required in a
publication commit. The authored preinspection plan, this report, the
source/query ledger, the run report, and their hash manifest provide
sufficient publication provenance and integrity targets for reacquisition.
Replay remains contingent on the cited sources remaining available at the
same bytes.

## Publication-safe conclusion

The strongest wording supported by this audit is:

> Through 2026-07-23, current inspected sources continue to treat
> `srg(99,14,1,2)` as unresolved. Reimbayev's exact identity gives
> `induced_C6=209286+n3`; the located explicit theorem uses only `n3>=0`,
> while Makhnev's zero-case exclusion plus published divisibility yields the
> derived older necessary bound `n3>=3`. No inspected source or enumerated
> query contained the Wave23 values `n3>=708`, `induced_C6>=209994`, or the
> complete endpoint argument. This is bounded non-discovery, not a novelty
> certificate. Target existence, Wave23 validity in this role, and novelty
> remain `UNKNOWN`.
