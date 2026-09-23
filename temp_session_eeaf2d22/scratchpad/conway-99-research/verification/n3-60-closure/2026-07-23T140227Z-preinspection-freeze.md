# Wave 19 conditional `n3=60` closure preinspection freeze

```yaml
role: verifier
date_utc: 2026-07-23T14:02:27Z
git_commit: f16ec3d49e5e7f7fde0a8f20ea324d6f49c5b24c
claim_label: UNKNOWN
scope: adversarial verification standard for any prospective closure of both conditional n3=60 residuals, frozen before inspecting any alternate-lane artifact
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  agents/2026-07-23-wave19-n3-60-structural.md: b2f90af07f34a6525ea35cdf4d392d95aea10fc319633cd17037d00145690744
  verification/2026-07-23-wave15-global-lift-audit.md: edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036
  verification/2026-07-23-wave16-n3-51-structural-audit.md: 99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6
method: freeze source separation, independently derive exact local and block-matrix constraints, build standard-library hostile checks, and require complete labeled-case certificates before accepting either residual as excluded
command: pending independent verifier implementation
outputs:
  this_freeze: hash recorded in a sibling sha256 file after this write
limitations: this is a preinspection protocol, not a proof; no Wave 17, Wave 18, alternate-frontier file, alternate report, prospective catalog, or solver artifact has been inspected; status remains UNKNOWN
```

The `git_commit` value above was read directly from `.git/HEAD` and its
referenced file.  No Git command was run.  This verifier will run no Git
command and make no Git write.

## 1. Source boundary and frozen target

Before this file was written I read only:

1. `AGENTS.md`;
2. the frozen public Wave 19 structural submission;
3. the audited Wave 15 global subset argument; and
4. the audited Wave 16 local crossing and indexed-point premises.

I have not opened, searched inside, imported, executed, or otherwise
inspected Wave 17, Wave 18, `attempts/wave19-alternate-frontier`, any
prospective alternate report, or any prospective closure catalog.  Filename
or directory inventories will not be used to learn their contents.  This
boundary remains in force until the orchestrator explicitly releases the
alternate artifacts.

The public Wave 19 submission ends, correctly, at:

```text
Residual A: m=27, point-size multiset 2^21 3^6.
Residual B: m=30, point-size multiset 2^30.
conditional n3=60: UNKNOWN.
```

The object of a closure audit is not to reproduce the Wave 19 moment counts.
It is to decide whether a proposed new argument supplies a complete exact
exclusion of every realization allowed by those residual descriptions.

## 2. Independent derivations required before comparison

Without importing discovery code or prose, I will derive and executable-check:

1. the SRG matrix equation
   `A^2=12I-A+2J` and the four-index rectangle identity obtained by applying
   it to differences of adjacency rows;
2. the exact refinement that cross edges between the relevant independent
   local objects must form a matching, with every distinctness and
   `lambda=1` hypothesis stated rather than inferred from a drawing;
3. the component classification forced by that matching refinement,
   including all small exceptional components and all parity cases;
4. the local consequences for a point, its meeting neighbors, its positive
   disjoint crossing neighbors, its zero-crossing neighbors, and all possible
   overlap-deleted crossing sizes;
5. for a proposed induced graph `D=G[X]`, the exact outside Gram matrix

   ```text
   BB^T = 12I-D+2J-D^2,
   ```

   where `B` is the binary `X`-to-outside incidence matrix, together with its
   diagonal, off-diagonal, row-sum, column-sum, rank, positive-semidefinite,
   integrality, and binary-factorization consequences; and
6. the remaining block equations

   ```text
   DB+BC = 2J-B,
   B^TB+C^2 = 12I-C+2J,
   ```

   whenever a proposed certificate claims a full lift rather than only a
   top-left Gram obstruction.

The four-index identity will be checked in its general Kronecker-delta form,
not only for four distinct vertices.  Hostile tests will include repeated
indices, reversed orientations, a mutated sign, and patterns with zero, one,
two, three, and four cross edges.

## 3. Residual A completeness boundary (`m=27`)

An exclusion of residual A must cover every labeled linear point family on
twenty active labels having exactly twenty-one size-two points and six
size-three points, with:

- every active label occurring in exactly three indexed points;
- no repeated point index, no repeated label within a point, and pairwise
  point intersections of size at most one;
- the audited no-Berge-triangle condition;
- all mandatory original-graph meeting edges;
- every allowed overlap-deleted crossing pattern;
- the positive-meeting graph on the six size-three points, including both
  `K3,3` and triangular-prism isomorphism classes and every labeled
  realization compatible with the point family;
- every admissible positive-disjoint two-factor placement on the twenty-one
  size-two points, not merely each cycle-length partition;
- every remaining induced edge permitted by the local rules; and
- every binary outside-incidence factor and outside graph compatible with
  the exact SRG block equations, unless an earlier exact obstruction is
  certified.

A list of cycle-length multisets is not a catalog of two-factors.  A catalog
of abstract point-family isomorphism types is not complete unless an
independent canonical-labeling or orbit-stabilizer certificate proves that
every labeled family maps to exactly one official representative and that
all placements of subsequent structures are transported soundly.

Residual A passes as excluded only if each official case has either:

1. a short, independently replayable mathematical contradiction whose
   hypotheses are parser-checked against that case; or
2. a complete exact search proof with a checkable per-case proof object.

One missing point family, one omitted labeling/orbit, one omitted two-factor
placement, or one unsupported solver result leaves residual A `UNKNOWN`.

## 4. Residual B completeness boundary (`m=30`)

For residual B, every candidate begins with:

```text
F: a simple cubic triangle-free graph on 20 active labels;
L(F): its 30-vertex line graph on indexed size-two points;
R: a spanning 2-factor on those 30 points, disjoint from L(F), whose edges
   obey the exact positive-disjoint crossing rule;
Z: every remaining induced zero-crossing edge.
```

Completeness requires every labeled `F`, or a certified complete set of
isomorphism representatives; for each `F`, every allowed labeled `R`
placement, not only its cycle-length multiset; and for each `(F,R)`, every
allowed labeled `Z` placement.  `Z` must be simple, edge-disjoint from
`L(F) union R`, and each endpoint pair must satisfy the exact disjoint-point
and zero-crossing predicates.

The public moment bound permits `e(Z)<=3`.  Therefore the official coverage
ledger must explicitly include every placement of every one of these nine
unlabeled types:

| edges | required `Z` type |
|---:|---|
| 0 | empty graph |
| 1 | `K2` |
| 2 | `2K2` |
| 2 | `P3` |
| 3 | `3K2` |
| 3 | `P3 + K2` |
| 3 | `P4` |
| 3 | `K1,3` |
| 3 | `K3` |

The type name alone is not coverage.  All injective embeddings into the
thirty indexed points that pass the endpoint predicate must be included or
mapped to a checked orbit representative under the actual automorphism
group of the already fixed `(F,R)` structure.  An automorphism of `F` that
does not preserve `R` cannot identify `Z` placements.  An automorphism
assumption that was imposed for search convenience is a restriction and
cannot support an unrestricted exclusion.

For each `(F,R,Z)` case, the proposed induced graph
`D=L(F) union R union Z` must be reconstructed from the certificate rather
than trusted as serialized.  Its outside Gram matrix must be recomputed.
Degree histograms or first/second moments of outside columns are necessary
conditions only; they do not establish a binary factor `B`, much less an
outside adjacency matrix `C`.

One omitted cubic graph, one omitted `R` placement, one omitted allowed `Z`
embedding, one unsound orbit quotient, or one unverified certificate leaves
residual B `UNKNOWN`.

## 5. Official bytes and exact-certificate requirements

No raw `SAT`, `UNSAT`, `UNKNOWN`, solver exit code, wall-clock log, catalog
count, or model confidence is evidence of exclusion.  A proposed official
bundle must provide:

- immutable official bytes with relative path, byte length, and SHA-256 for
  every input, generator, catalog, proof object, checker, and result;
- a versioned, documented machine-readable schema;
- strict parsing that rejects duplicate keys/IDs, extra fields where
  meaningful, malformed integers, out-of-range labels, loops, parallel
  edges, noncanonical encodings, truncated data, trailing garbage, and
  checksum mismatches;
- property checks that reconstruct all derived graphs and verify every
  declared degree, incidence, crossing, component, orbit, and SRG equation;
- a deterministic completeness generator or a separately checkable
  coverage proof;
- a per-case ledger linking every official case ID to exactly one checked
  contradiction or exact proof object;
- byte-identical regeneration where claimed; and
- an independent standard-library verifier that does not import the
  discovery implementation or trust its cached counts.

If SAT is used for discovery, publication requires a pinned exact proof
format and an independently replayed proof checker, or a deterministic
backtracking certificate whose branch coverage and leaf contradictions are
fully checked.  A CNF hash plus `UNSAT` is not enough.  If an isomorphism
catalog is imported, its provenance and completeness theorem/certificate
must be pinned and checked; a familiar catalog size is not self-authenticating.

## 6. Hostile tests frozen in advance

The independent suite will deliberately test:

1. a sign mutation in the rectangle identity;
2. dropping Kronecker terms for repeated indices;
3. enforcing a matching condition at only one endpoint;
4. permitting two cross edges sharing an endpoint;
5. silently identifying indexed points having equal set values;
6. retaining instead of deleting a shared active label;
7. imposing a global `{0,4}` crossing degree rule;
8. accepting a six-edge `3`-by-`3` crossing where a size-two endpoint was
   required, and rejecting it where it is genuinely legal;
9. substituting outside degree moments for a binary Gram factor;
10. accepting a positive-semidefinite integral matrix that has no verified
    binary factor;
11. quotienting `Z` by `Aut(F)` instead of `Aut(F,R)`;
12. omitting one of the nine `Z` types above;
13. omitting a single allowed labeled `Z` embedding;
14. accepting an `R` cycle-length multiset without its placements;
15. accepting a catalog count with one duplicated case and one missing case;
16. accepting malformed, truncated, reordered, or trailing-garbage
    certificate bytes;
17. accepting an unpinned solver result or an unverified `UNSAT` claim; and
18. promoting a necessary local obstruction to a full residual exclusion.

## 7. Pass, fail, and publication boundary

```text
PASS / residual A excluded:
  every residual-A realization is covered and every per-case exact
  contradiction independently replays.

PASS / residual B excluded:
  every F, every R placement, and every allowed placement of all nine Z
  types is covered and every per-case exact contradiction independently
  replays.

PASS / conditional n3=60 excluded:
  both preceding passes hold under exactly the audited premises.

REFUTED closure:
  an official case survives a claimed contradiction, a certificate is
  invalid, a coverage map is false, or a verified full SRG lift is produced.

UNKNOWN:
  every other outcome, including partial catalogs, necessary conditions,
  unverified counts, timeouts, missing official bytes, raw SAT/UNSAT, or
  even one uncovered residual or Z placement.
```

The verifier may veto a closure but will not silently repair it.  Any defect
and any later correction must be recorded with new bytes and new hashes.
Until all requirements above are met, conditional `n3=60`, the Conway-99
target, and novelty remain `UNKNOWN`.
