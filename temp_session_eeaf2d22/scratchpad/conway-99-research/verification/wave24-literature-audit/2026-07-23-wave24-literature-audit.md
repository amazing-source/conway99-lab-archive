# Wave 24 source-first literature and status audit

Cutoff: `2026-07-23`

## Bottom line

Current specialized and maintained sources inspected through the cutoff still
treat the existence of `srg(99,14,1,2)` as unresolved. One 2022 JSAI
technical report was located that purports to prove nonexistence, but its
displayed proof does not establish the theorem as written: the derivation of
its equation (88) assumes that two common neighbors of a pair of
distance-two-layer vertices both remain in that layer, while a common
neighbor may instead lie in the first layer. Later specialized sources
continue to call the problem open.

No inspected source or enumerated exact query produced the Wave 24
conditional restriction

```text
n3=708
  ==>
det(B)<=6561=3^8
and
h in {9,21,49,81,189,441,729,1029}.
```

Nor was the exact pointwise logarithmic inequality or the complete
characteristic-pseudodeterminant-to-index chain located. This is
`BOUNDED NON-DISCOVERY`, not a novelty certificate. General prior art does
cover two ingredients separately: pseudodeterminants as products of nonzero
eigenvalues/first nonzero characteristic coefficients, and integral lattices
constructed from rational association-scheme idempotents. Consequently both
the target status and literature novelty remain `UNKNOWN`.

| Audited proposition | Result |
|---|---|
| Current inspected specialized sources treat Conway-99 as open | `CONFIRMED`, with indexing caveat |
| A 2022 source purports to prove nonexistence | `CONFIRMED`; displayed proof has a concrete gap |
| Exact `n3=708` / `det(B)<=3^8` / eight-value `h` match | `BOUNDED NON-DISCOVERY` |
| Exact logarithmic inequality or complete target-specific method match | `BOUNDED NON-DISCOVERY` |
| General characteristic-pseudodeterminant ingredient | `CITED CONCEPTUAL ANALOGUE` |
| General rational-idempotent/projector-lattice ingredient | `CITED CONCEPTUAL ANALOGUE` |
| Wave 24 mathematical validity in this role | `NOT ASSESSED` |
| Conway-99 existence or nonexistence | `UNKNOWN` |
| Wave 24 novelty or priority | `UNKNOWN` |

## Proof separation and frozen search

Before opening the Wave 24 discovery report, checker output, or proof notes,
the literature role wrote
`verification/wave24-literature-audit/preinspection-query-plan.md`. Its
frozen SHA-256 is:

```text
9e4d1cff10092aa1fd171ad0c94dc17e8d4cd08fd6463fbb83bdd2374329ddd1
```

Only after freezing that plan was the discovery package opened to transcribe
the exact notation and eight values. The compared project inputs were:

```text
agents/2026-07-23-wave24-n3-708-index-boundary.md
sha256 461bbcff6399ae18c2764f68ea498b7eebba9780af0032b8e2e8fa18ca26af28

attempts/wave24-n3-708-index/exact-results.json
sha256 a4241cdeea64a8f6073037d564e72fb7ef545287d45aca4759cec6c31d26a463
```

This role used those files only to define the post-freeze comparison target.
It did not replay or verify the Wave 24 derivation and cannot promote it to
`VERIFIED`.

## Exact comparison target

The Wave 24 report makes a conditional necessary-restriction claim for a
putative target at `n3=708`; it does not exclude that endpoint. In its
notation,

```text
B=I+2C,
rank(L)=44,
tr(C)=8,
det(B)=h det(Q),
h=3^a 7^b,
det(Q)>=5.
```

The new route uses integrality of the characteristic polynomial of `C` to
obtain a nonzero characteristic coefficient with absolute value at least
one. It then applies

```text
log(1+2x)
  <= x log(3) - (log(3)-2/3) log|x|
```

to the nonzero real eigenvalues of `C`, deriving `det(B)<=3^8`. The remaining
arithmetic conditions leave exactly

```text
h = 9, 21, 49, 81, 189, 441, 729, 1029.
```

The report also gives an abstract `h=9` coordinate-lattice survivor, so the
claimed result is a restriction rather than a contradiction. The audit
searched the endpoint, determinant cap, each individual `h`, the complete
ordered list, the displayed logarithmic inequality, and equivalent
pseudodeterminant/projector-lattice formulations.

## Current target-status evidence

The current-status conclusion is triangulated from specialized primary and
maintained sources:

- Patrick G. Cesarz and Andrew J. Woldar,
  [On the automorphism group of a putative Conway 99-graph](https://alco.centre-mersenne.org/articles/10.5802/alco.418/),
  Algebraic Combinatorics 8 (2025), DOI `10.5802/alco.418`, calls existence
  an open problem and proves automorphism-group restrictions only.

- Ali Keramatipour,
  [Approaching the Conway-99 problem using SAT solvers](https://arxiv.org/abs/2604.23037v2),
  arXiv v2 dated 2026-04-28, explicitly calls the target open and says the
  studied SAT approach does not settle it.

- Connor Phillips,
  [A Comprehensive Study of Clique Graphs and Clique Regular Graphs](https://arxiv.org/abs/2605.22867v1),
  arXiv v1 dated 2026-05-19, says the Conway bounty has yet to be claimed and
  again poses the existence question.

- A. E. Brouwer's maintained
  [strongly regular graph table for 51-100 vertices](https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html)
  marks `(99,14,1,2)` with `?`.

- Reimbay Reimbayev's current
  [six-vertex classification v2](https://arxiv.org/abs/2508.03377v2)
  continues to leave `n3` free. Its official PDF contains neither `708` nor
  `6561` in the Wave 24 sense. The related
  [order-seven paper](https://arxiv.org/abs/2511.06572v1) likewise does not
  provide the Wave 24 endpoint restriction.

An official June 2026 lecture announcement about a different strongly
regular graph mentioned only that a similar approach might be applicable to
Conway-99; it supplied no Conway-99 resolution or Wave 24 result.

These sources do not prove that no unindexed or private resolution exists.
They support only the bounded current-status statement:

> Through the cutoff, current inspected specialized sources still treat the
> target as unresolved.

## The located 2022 nonexistence claim

Hideto Ishihara's
[Theory of the pain of humans etc.](https://www.jstage.jst.go.jp/article/jsaisigtwo/2022/AGI-021/2022_01/_article/-char/en),
JSAI Technical Report, Type 2 SIG, Volume 2022, issue AGI-021, DOI
`10.11517/jsaisigtwo.2022.AGI-021_01`, contains Theorem 28 claiming that an
`srg(99,14,1,2)` does not exist.

The source metadata labels the item a research/technical report, gives a
publication date of 2022-07-14, gives no received or accepted date, and lists
zero references and zero citing items on the landing page. Source type alone
is not the decisive issue; the displayed argument has a specific mathematical
gap.

The proof fixes `w0`, writes `L1=N(w0)` and `L2` for the distance-two layer,
takes a component `Hk` of the graph induced by `L2`, selects `wk` in it, and
lets `Hk1=N(wk) intersect L2` and `Hk2` be the remaining vertices of that
component. It then asserts that every `y` in `Hk2` has exactly two neighbors
in `Hk1`, leading to

```text
10 s_k + 11 t_k = 2 b_k.                       (88)
```

For nonadjacent `wk,y`, the strongly regular parameters imply only that they
have exactly two common neighbors in the whole graph. Both `wk` and `y` have
two neighbors in `L1`. If they share an `L1` neighbor, that vertex already
counts as one of their two common neighbors, leaving at most one corresponding
common neighbor in `Hk1`. The paper gives no lemma excluding shared `L1`
neighbors. Thus the assertion used to double-count the edges between `Hk1`
and `Hk2`, and hence equation (88), is not established.

The defensible source assessment is:

> The displayed proof does not validate Theorem 28 as written. Later
> specialized sources continue to treat Conway-99 as open, and no
> authoritative accepted resolution was located.

This audit therefore does not convert the 2022 claim into `REFUTED` target
status or into a resolution; target status remains `UNKNOWN`.

## Exact-number and method search

The frozen query families were executed on general web search, exact
site-qualified searches, arXiv's API, and OpenAlex. The literal queries and
retrieval hashes are recorded in `source-query-ledger.json`.

The searches covered:

1. `n3=708`, TeX/subscript variants, the induced-six-cycle equivalent, and
   target-qualified occurrences of `708`;
2. `det(B)`, `6561`, `3^8`, and target-qualified determinant/index phrases;
3. all five frozen templates for each of
   `9,21,49,81,189,441,729,1029`, plus the entire list in comma-separated
   and brace notation;
4. characteristic pseudodeterminants, first nonzero characteristic
   coefficients, `det(I+2C)`, fixed-trace determinant bounds, and exact
   fragments of the pointwise log inequality; and
5. rational spectral idempotents, integral Gram lattices, projector lattices,
   Smith form, discriminants, and index obstructions for strongly regular
   graphs.

No responsive exact target match was found. The arXiv API query for
`"99,14,1,2"` returned only the known Reimbayev lower-bound paper and the
Cesarz-Woldar automorphism paper. The arXiv API query for `"Conway 99"`
returned five known target-adjacent works, none containing the Wave 24
endpoint. Exact OpenAlex searches for the endpoint/determinant phrase, the
eight-value list, and the displayed logarithmic expression returned zero
records at retrieval.

Common integers produced unrelated noise. Such hits were rejected unless
they also matched the Conway-99 target and the claimed mathematical role.
No absence claim is made beyond the enumerated search.

## Ingredient-level prior art

Two primary sources are close enough conceptually that they must be recorded,
but neither is an exact Wave 24 match.

Oliver Knill,
[Cauchy-Binet for Pseudo-Determinants](https://arxiv.org/abs/1306.0062),
arXiv:1306.0062v3, defines a pseudodeterminant as the product of nonzero
eigenvalues and identifies it, up to sign, with the first nonzero coefficient
of the characteristic polynomial. It also gives graph-Laplacian applications.
This is prior art for the general characteristic-pseudodeterminant ingredient,
not for the `n3=708` endpoint, the exact log majorant, `det(B)<=3^8`, or the
eight `h` values.

Roland Bacher and Boris Venkov,
[Lattices and association schemes: a unimodular example without roots in dimension 28](https://www.numdam.org/item/AIF_1995__45_5_1163_0/),
Annales de l'Institut Fourier 45 (1995), DOI `10.5802/aif.1490`, show in
Proposition 2.1 that a rational minimal idempotent scaled to a symmetric
integral matrix is the Gram matrix of vectors spanning an integral lattice;
they also obtain a determinant-prime restriction and pose finite-index
questions. This is prior art for the general association-scheme
idempotent-to-lattice bridge, not for the target-specific Wave 24 endomorphism,
determinant cap, or index list.

These analogues prevent a broad claim that pseudodeterminants or
projector-derived lattices themselves are new. The exact synthesis may or may
not be new; this bounded audit cannot decide priority.

## Acquisition provenance and limitations

Third-party source bytes were fetched directly from official or author-hosted
URLs into memory for hashing and were not retained in the repository. The
ledger records URL, version/date where available, byte length, SHA-256, and
the claim for which each source was inspected. In particular, it records
current bytes for the Brouwer table, the 2025 publisher article, current arXiv
PDFs, the 2022 J-STAGE report, and both ingredient-level analogues.

Tooling retries were retained in the ledger. An initial PowerShell runtime
lacked `System.Convert.ToHexString`; hashes were recomputed with
`BitConverter`. A later shell initially lacked the loaded
`System.Net.Http.HttpClient` assembly, and one nullable response-header
conversion failed; both were corrected with an explicit assembly load and
null-safe metadata handling. These were local tooling failures, not source
access failures, and no failed response is treated as evidence.

Search engines and bibliographic indexes are incomplete and can lag. Exact
queries can miss alternate notation, and dynamically served source bytes can
change. No third-party cache was committed, so replay requires reacquisition
from the provenance URLs. Literature non-discovery cannot establish novelty.

## Publication-safe conclusion

The strongest supported wording is:

> Through 2026-07-23, current inspected specialized sources continue to treat
> `srg(99,14,1,2)` as unresolved. A located 2022 JSAI technical report claims
> nonexistence, but its displayed proof assumes an unjustified
> distance-layer common-neighbor count, so it does not establish that claim as
> written. No inspected source or enumerated exact query contained the Wave 24
> conditional `n3=708` restriction, `det(B)<=6561=3^8`, the ordered survivors
> `{9,21,49,81,189,441,729,1029}`, or the complete logarithmic
> characteristic-pseudodeterminant/index argument. General
> pseudodeterminant and rational-idempotent lattice ingredients have older
> prior art. Exact-match non-discovery is bounded; target status, Wave 24
> validity in this role, novelty, and priority remain `UNKNOWN`.
