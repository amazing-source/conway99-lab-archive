# Wave 34 external-source audit: status and designs

Date: 2026-07-24

Role: verifier

Claim label: `CITED`

Overall assessment: `PASS_WITH_BOUNDED_CAVEATS`

## Outcome

The three bounded source-characterization claims in the Wave 34 discovery
ledger are supported by current direct sources:

1. Brouwer's maintained strongly regular graph table marks
   `(99,14,1,2)` with `?`, and Brouwer and Van Maldeghem's publisher-hosted
   parameter index says that `?` means none is known.
2. McKay's slides state that there are about `1.5 x 10^21`
   `2-(15,3,2)` designs. The deck's project and construction slides put that
   estimate in an isomorphism-reduced, nonisomorphic-design context.
3. Rijeka Folder 2 is a derived `2-(15,3,2)` corpus whose Folder 1 parents
   are explicitly restricted to `2-(71,15,3)` designs having an automorphism
   of order 6.

These are source-scope findings only. The following all remain `UNKNOWN`:

```text
Conway-99 existence/nonexistence
n3 = 708
non-discovery
novelty
priority
```

## Frozen local claims

The verifier used the following files only to identify the claims under audit:

| File | Bytes | SHA-256 |
|---|---:|---|
| `attempts/wave34-current-literature/source-ledger.json` | 5,438 | `5fa6f75abcfc8d3033c9715f3977722e99fcb238ca1b74d2db255e759a58b100` |
| `attempts/wave34-current-literature/audit.md` | 5,327 | `1be6c6904314763031968c47dde8b4187caf1118ca4c2a1c9cf5f93d9496abc3` |
| `agents/2026-07-24-wave34-current-literature.md` | 4,606 | `b470c62d657686779f22154872e19d7db002f1abde1bc173ae747f9e2ad86b95` |

The remote sources below were then inspected independently. No discovery
agent interpretation was treated as evidence.

## C01: Brouwer maintained status

Assessment: `CONFIRMED_MAINTAINED_STATUS`

Claim label: `CITED`

The [maintained table index](https://aeb.win.tue.nl/graphs/srg/srgtab.html)
identifies its first column as `existence`, followed by `v`, `k`, `lambda`,
and `mu`. In the [51--100 table](https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html),
the exact row for the target parameters is:

```text
? 99 14 1 2 3^54 -4^44
```

As independent notation corroboration, the publisher-hosted
[parameter index for *Strongly Regular Graphs*](https://assets.cambridge.org/97813165/12036/index/9781316512036_index.pdf)
says on PDF page 1 of 12 (printed page 451) that a question mark means none is
known. The same page lists `(99,14,1,2)?`.

This confirms the maintained-source status at the recorded access time. It
does not prove that no unindexed, unpublished, or later result exists, and it
does not construct or exclude the Conway 99-graph.

### Remote byte records

| Resource | Accessed UTC | Bytes | SHA-256 | HTTP metadata |
|---|---|---:|---|---|
| Maintained table index | `2026-07-24T21:32:48.487Z` | 2,388 | `a69348ace958a14d7541e69db8d6c8b6186eec0eb7ab883bd518a66acf9ec13c` | `200`; `text/html`; Last-Modified `Mon, 27 Jan 2025 03:20:11 GMT`; ETag `W/"954-62ca78dd570c0"` |
| Parameters 51--100 | `2026-07-24T21:32:49.189Z` | 24,003 | `db88468cc47bb5aa9108d488596557de3a68ec80dcf5f7ffea9f2e16d3f60f89` | `200`; `text/html`; Last-Modified `Mon, 27 Jan 2025 03:20:10 GMT`; ETag `W/"5dc3-62ca78dc62e80"` |
| Cambridge parameter-index PDF | `2026-07-24T21:32:49.400Z` | 113,058 | `dd41d51287da84c74bc362a7b41fec402b16a8c9e3de603958fa766e4fb0d0dc` | `200`; `application/pdf`; Last-Modified `Thu, 11 Nov 2021 09:01:07 GMT`; ETag `"1b9a2-5d07f9542eee8"` |

## C02: McKay's approximate design count

Assessment: `CONFIRMED_CONTEXTUAL_APPROXIMATE_QUOTE`

Claim label: `CITED`

McKay's author-hosted slide deck,
[*Some Examples of Combinatorial Generation*](https://45acc.github.io/slides/McKay.pdf),
contains the following relevant passages:

- PDF page 30 of 46, slide footer `combinatorial generation 18`: the project
  aims to compile complete lists of nonisomorphic `2-(v,k,lambda)` designs.
- PDF page 31 of 46, slide footer `combinatorial generation 19`: partial
  designs are reduced by isomorphism class.
- PDF page 46 of 46, slide footer `combinatorial generation 22`: the results
  slide says `2-(15,3,2): about 1.5 x 10^21 designs`.

The discovery wording “about `1.5 x 10^21` nonisomorphic
`2-(15,3,2)` designs” is therefore supported as a contextual reading of the
deck. A precision caveat is necessary: the numerical line itself says
`designs`, not `nonisomorphic designs`. The nonisomorphic qualifier comes from
the deck's explicitly stated project scope and isomorphism-class reduction.

The word `about` is also substantive. The inspected deck provides no exact
count, derivation, error bar, or enumeration certificate for this estimate.
It is an approximate scale statement only.

### Remote byte record

| Accessed UTC | Bytes | SHA-256 | HTTP metadata |
|---|---:|---|---|
| `2026-07-24T21:32:50.643Z` | 675,232 | `49f4652c4ea0617f1294b981047e4b5ab30875392347ee399f1cfedc806009ed` | `200`; `application/pdf`; Last-Modified `Sat, 13 Jan 2024 04:07:53 GMT`; ETag `"65a20c99-a4da0"` |

## C03: Rijeka corpus scope

Assessment: `CONFIRMED_RESTRICTED_DERIVED_CORPUS`

Claim label: `CITED`

The University of Rijeka
[top-level data index](https://www.math.uniri.hr/~sanjar/structures/) links
Folder 1 as `2-(71,15,3) designs` and Folder 2 as `2-(15,3,2) designs`. Its
[README](https://www.math.uniri.hr/~sanjar/structures/0_README_the_content_of_folders_and_references.txt)
states:

- Folder 1 contains `2-(71,15,3)` designs having an automorphism of order 6.
- Folder 2 contains `2-(15,3,2)` designs derived from the Folder 1 designs.

An in-memory parse of the live directory indexes found:

| Index | Exact link pattern | Count | Sequence check |
|---|---|---:|---|
| [Folder 1](https://www.math.uniri.hr/~sanjar/structures/FOLDER1%202-%2871%2C15%2C3%29%20designs/) | `D1.MAT` through `D146.MAT` | 146 | no gaps; no duplicates |
| [Folder 2](https://www.math.uniri.hr/~sanjar/structures/FOLDER2%202-%2815%2C3%2C2%29%20designs/) | `d1.mat` through `d590.mat` | 590 | no gaps; no duplicates |

This confirms a restricted derived corpus, not an unrestricted catalogue.
There are two additional boundaries:

- The README places the order-6 automorphism restriction on the Folder 1
  parents. It does not state that every Folder 2 derived design itself has an
  order-6 automorphism.
- The index does not claim that the 590 files form a complete list of all
  nonisomorphic `2-(15,3,2)` designs. This audit counted index entries but did
  not download, parse, deduplicate, or validate individual matrices.

### Remote byte records

| Resource | Accessed UTC | Bytes | SHA-256 | HTTP metadata |
|---|---|---:|---|---|
| Top-level index | `2026-07-24T21:32:52.013Z` | 5,648 | `2b3233c145ef84a54756e540e74864086eb79ade296a78e078ba8e5f3f77e06e` | `200`; `text/html;charset=UTF-8` |
| README | `2026-07-24T21:32:52.700Z` | 7,845 | `744d9065e93bc157aaa022f2aad0cf3cd5ccf832fc4079ae8fdd79211538f797` | `200`; `text/plain;charset=WINDOWS-1250`; Last-Modified `Thu, 10 Apr 2025 19:31:27 GMT`; ETag `"1ea5-63271a1d24556-gzip"` |
| Folder 1 index | `2026-07-24T21:32:52.944Z` | 29,675 | `09b0ab651f6a1bd59b0937ec37c3a32b0b66c17781ea2442dd33a7635455c1e3` | `200`; `text/html;charset=UTF-8` |
| Folder 2 index | `2026-07-24T21:32:53.154Z` | 117,139 | `f9954bfc7f4e283617814e5e75907ef201a1c84bf754cddd441f629a07e67ec9` | `200`; `text/html;charset=UTF-8` |

## Evidence handling

The byte counts and SHA-256 values are for the response-body bytes returned by
the direct in-memory HTTP fetches. They allow later drift detection; they are
not substitutes for the source text. The workspace contains no copied
third-party HTML, PDF, archive, or matrix payload from this audit.

An immediate second pass from `2026-07-24T21:39:46.576Z` through
`2026-07-24T21:39:51.753Z` used `recheck_live_sources.ps1`. All eight resources
again returned HTTP 200, and every response-body byte length and SHA-256
matched the recorded first pass. The second pass independently reproduced the
146 and 590 matrix-link counts.

Only metadata, bounded paraphrases, short locators, and hashes are retained.
The machine-readable details are in `results.json`.

## Final boundary

The audited Wave 34 wording is acceptable if its qualifiers remain intact:

- “Brouwer's maintained table marks ...” rather than a proof of global
  openness or nonexistence;
- “McKay's slides estimate about ...” rather than an exact enumerated count;
- “derived from parents restricted by an order-6 automorphism” rather than
  claiming every derived object has that automorphism or that the corpus is
  unrestricted and complete.

No claim in this audit changes Conway-99, `n3=708`, non-discovery, novelty, or
priority from `UNKNOWN`.
