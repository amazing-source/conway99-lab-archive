# Independent audit of the Wave 17 \(n_3=54\) exact census

Verdict: **the frozen 457-case fixed-\(F\) census is `VERIFIED`,
conditional on the Wave 17 structural reduction and the official catalog
coverage premise.**

All 455 connected order-18 cases are excluded by an independently rebuilt
GF(2) relaxation: 443 kernels are trivial, and exhaustive enumeration of all
262,204 vectors in the 12 nontrivial kernels finds no vector with integer
degree two at every one of the 27 point-edges.  Including the zero vectors of
the 443 trivial cases, 262,647 kernel vectors were checked in total.  The two
mixed \(K_{3,3}+F_{12}\) cases are independently excluded by a direct degree
count: nine internal \(F_{12}\) support edges are forced, while the two cases
have only one and zero compatible internal candidates.

The official House of Graphs bytes, all 457 graph6 records, every certificate
row, every matrix/RREF/basis digest, the frozen certificate file hash, and the
discovery result were reproduced without a mismatch.  The raw 457 SAT
`UNSAT` statuses have no proof traces and were not used.

This audit does **not** establish existence or nonexistence of
`srg(99,14,1,2)`, and it does not establish novelty.  Both remain `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T12:38:29Z
git_commit: 932c620e4cf2a8e1dac02a0c95a3c1eac15a9bd4
claim_label: VERIFIED
scope: independent verification of the complete fixed-F exact-coverage obstruction for the frozen conditional Wave17 n3=54 residual
inputs:
  verification/n3-54-census/00-preinspection-freeze.md: fe0277949d9555882d29391395e9bc035d737e5f67056d8e6afd98f7ae34f574
  agents/2026-07-23-wave17-n3-54-structural.md: ffae576057617b6d8e32f7df4a1cd9627c63bdfe40fb58f394fd2640d1d82d18
  agents/2026-07-23-wave17-n3-54-census.md: 8ab3521ed116852bfe8f68db5826199c668c29bfec456e69c3a6204c985f1021
  attempts/wave17-n3-54-census/census.py: bf0954abed0d6a032aa7dd255a6b73d96f1c166fca5354958aa211ca57f22afc
  attempts/wave17-n3-54-census/build_certificate.py: d2add3ff676deeed1b3381f6e22c4da0cdafc38634a2a6f722d5e49ae6a3dc55
  attempts/wave17-n3-54-census/verify_certificate.py: 175263f8ed89203b86689ee78985232d347b913668c2cb9196d5ccb34ada7265
  attempts/wave17-n3-54-census/test_certificate.py: b6fcfa9c5dfc7c3fd340d15a9d3eeec34d18aa3844f3a9269fb60bba646dba4f
  attempts/wave17-n3-54-census/census-results.json: f81158e9dacbb4b83bdbc3f19724c304b9dc10a550297661f68272f0d83cdeb2
  attempts/wave17-n3-54-census/exact-certificate.json: f5c66a2ba6ee0c8b0d4ea4a15411366000faf03fdcb431e19f26747d117ced12
  attempts/wave17-n3-54-census/verification-result.json: be120ef86f8e58ce3072d085c74101e41165500af00f38db626fd5145ceaf42a
  house_of_graphs_cub18_gir5_gz:
    url: https://houseofgraphs.org/data/cubics/cub18-gir5.g6.gz
    compressed_bytes: 2470
    compressed_sha256: 95ff5ca833f3a1361d652e8f585d8aed21af61d73d135abf366570dcbddfcf7e
    decompressed_bytes: 12740
    decompressed_sha256: 39fb8633418927da9f5e3bd9fe81c83070a05ff65bfc532719618471a267f7fd
    records: 455
  house_of_graphs_cub12_gir5_gz:
    url: https://houseofgraphs.org/data/cubics/cub12-gir5.g6.gz
    compressed_bytes: 55
    compressed_sha256: c63e83c1b6c27af375c1f44f4dedfb5aa3f4f2abf01b6e68ba131942f72a6226
    decompressed_bytes: 26
    decompressed_sha256: ddf1582755db62e06d8072b7dfffb48357b56c677c11890eb14d9aeeb1ba55d4
    records: 2
method: strict independent graph6 decoding into adjacency bit masks; in-memory HTTPS catalog validation; column-syndrome GF(2) kernel construction; exhaustive Gray-code kernel enumeration with integer degree tests; direct mixed-component degree count; separate compatibility-only reproduction of discovery digests; hostile unit tests
command: |
  .venv\Scripts\python.exe -B -m unittest -v verification\n3-54-census\test_independent_verifier.py
  .venv\Scripts\python.exe -B verification\n3-54-census\independent_verifier.py --output verification\n3-54-census\independent-result.json
  .venv\Scripts\python.exe -B verification\n3-54-census\independent_verifier.py --output verification\n3-54-census\independent-result.json
  .venv\Scripts\python.exe -B -m unittest -v attempts\wave17-n3-54-census\test_certificate.py
  .venv\Scripts\python.exe -B attempts\wave17-n3-54-census\verify_certificate.py attempts\wave17-n3-54-census\exact-certificate.json
  .venv\Scripts\python.exe -B -c "import hashlib,subprocess,sys,pathlib; p=subprocess.run([sys.executable,'-B','attempts/wave17-n3-54-census/build_certificate.py'],check=True,capture_output=True); normalized=p.stdout.replace(b'\r\n',b'\n'); frozen=pathlib.Path('attempts/wave17-n3-54-census/exact-certificate.json').read_bytes(); print(hashlib.sha256(normalized).hexdigest(), normalized==frozen)"
  rg -n -i --glob 'verification/n3-54-census/*' '(ghp_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]+|authorization\s*:|bearer\s+[A-Za-z0-9._-]+|password\s*[:=]|token\s*[:=]|C:\\Users\\RESEARCHER .
outputs:
  verification/n3-54-census/independent_verifier.py: 07c747221cd117c75911246208701457cac82508d1ba0409b56c78f58c6ddd43
  verification/n3-54-census/test_independent_verifier.py: e13ab1903f23d60e1652178dc1120971f34acdf3853ac7f09d3aafb23712ab90
  verification/n3-54-census/independent-result.json: 159903af624a2df1975dd490ea5c267e453b5a96fe9744a9aa7a7be28390b056
  independent_full_runs: "2/2 PASS; result byte-identical"
  independent_hostile_tests: "17/17 PASS"
  discovery_focused_tests: "6/6 PASS"
  catalog_records_semantically_checked: 457
  connected_kernels_checked: 455
  nontrivial_connected_kernels_exhausted: 12
  total_connected_kernel_vectors_examined: 262647
  point_degree_two_vectors_found: 0
  mixed_degree_obstructions_checked: 2
  discovery_certificate_fields_exactly_matched: 457
  discovery_matrix_rref_basis_hashes_matched: true
  discovery_result_certificate_hash_matched: true
  security_scan: NO_MATCHES
  fixed_F_census: VERIFIED
  conditional_n3_54: EXCLUDED_VERIFIED_CONDITIONAL_ON_STRUCTURAL_AND_CATALOG_PREMISES
  prospective_conditional_n3_lower_bound: 57
  prospective_conditional_induced_C6_lower_bound: 209343
  conway_99: UNKNOWN
  novelty: UNKNOWN
limitations:
  - The census consumes, but does not re-prove, the frozen Wave17 structural reduction from an arbitrary putative SRG to the listed F/R residual.
  - Catalog completeness and one-representative-per-isomorphism-class are official external premises; this audit validates the pinned bytes and all supplied records but does not replay the catalog generators.
  - The 3K3,3 branch is consumed as excluded by the structural report; it is not part of the 457 catalog cases.
  - Raw SAT UNSAT statuses carry no evidentiary weight.
  - The stronger conditional n3 and induced-C6 bounds also consume prior audited divisibility, lower-bound, and cycle-count identities.
  - No unconditional target or novelty conclusion is claimed.
```

The commit above was read directly from `.git/HEAD` and its referenced ref;
no Git command or Git mutation was used.

## 1. Preinspection separation

Before opening `attempts/wave17-n3-54-census/*`, I wrote and hashed
`00-preinspection-freeze.md`.  Its SHA-256 is

```text
fe0277949d9555882d29391395e9bc035d737e5f67056d8e6afd98f7ae34f574.
```

That freeze committed to strict catalog validation, an independent
representation, exhaustive kernel enumeration, a separate mixed-case proof,
hostile tests, and refusal to use raw solver `UNSAT` as evidence.  The frozen
checks were not weakened after inspection.

The discovery implementation constructs parity rows and performs
left-to-right row reduction.  The independent proof implementation instead:

1. stores each graph as a tuple of integer neighbor masks;
2. stores each support variable as one 180-bit **column syndrome**;
3. streams columns into a highest-equation-pivot XOR basis while carrying
   variable dependencies;
4. independently validates every resulting nullspace vector; and
5. enumerates every kernel with a Gray-code walk.

A row-oriented routine exists only to reproduce the discovery's
algorithm-specific hash commitments after the independent decision has been
made.  Agreement of those hashes is an additional integrity check, not the
proof engine.

## 2. Catalog and reduction coverage

Both official files were fetched twice over HTTPS.  Each response was HTTP
200, remained on the exact `houseofgraphs.org` URL, and matched the pinned
compressed and decompressed lengths and SHA-256 hashes.  The independently
computed length-prefixed record-sequence hashes were:

```text
order 18: b79539ec49c20ee22858ad0706c944c649b27c895f28218ecd453c0eb5797c8b
order 12: 4cf61a5320deed550f1d854eff6c34548324ded891f36a2bb768c44cf8d0fcc6
```

The strict parser rejects headers, extended/non-short records, bad bytes,
truncation, trailing bytes, and nonzero padding.  Every one of the 455
order-18 and two order-12 records was checked for:

- the declared order and a canonical short-record length;
- simple symmetric adjacency;
- degree three at every vertex;
- exactly \(3n/2\) edges;
- connectivity;
- absence of triangles; and
- absence of 4-cycles.

The records are pairwise distinct as byte strings.  The two order-12 graphs
were independently relabeled onto vertices 6 through 17 and combined with a
fresh \(K_{3,3}\) on vertices 0 through 5.  Each union was checked as cubic
with component sizes 6 and 12, triangle-free, and with no nonadjacent pair of
codegree exactly two.

The frozen structural report reduces the residual component patterns to:

```text
connected cubic girth>=5, order 18;
K3,3 + connected cubic girth>=5, order 12;
3K3,3, already excluded by a structural parity proof.
```

Consequently the supplied official catalogs instantiate 455 plus two, or 457,
remaining \(F\)-types.  The audit confirms this reduction-to-catalog mapping.
The assertion that the official files are complete and contain exactly one
representative of each isomorphism class remains an explicitly named external
premise rather than a locally generated certificate.

## 3. Necessary support equations

For a fixed \(F\), its 27 edges are the point vertices on which \(R\) must be a
simple 2-factor.  The frozen structural rules force

```text
K0 = E(F) union {label pairs with a common F-neighbor}
```

to lie in \(K\), hence outside \(L\).  A support edge can therefore pair only
two disjoint \(F\)-edges whose four endpoint pairs all avoid \(K_0\).  The
independent implementation reconstructs exactly that compatible-support set
from neighbor masks.

Let \(x_s\) select a compatible support candidate.  Every valid residual must
satisfy

```text
sum_{s incident with point p} x_s = 2
```

at every one of the 27 point-edges, while every label-pair rectangle count is
either zero or two.  Modulo two, these are 27 point equations plus 153
label-pair equations:

```text
M x = 0 over GF(2), with M of size 180 by m.
```

This is a relaxation: it retains only even rectangle coverage, not the upper
bound two.  Therefore absence of a kernel vector with all integer point
degrees two is already a sound obstruction.  No matching, common-neighbor,
spectrum, or later binary filter is needed.

## 4. Exhaustive connected-case obstruction

The independent column-kernel ranks and nullities agree case-by-case with the
frozen certificate:

| nullity | connected cases | vectors per case |
|---:|---:|---:|
| 0 | 443 | 1 |
| 1 | 4 | 2 |
| 2 | 5 | 4 |
| 4 | 2 | 16 |
| 18 | 1 | 262,144 |

All 12 nontrivial kernels were exhausted.  For every enumerated vector, the
27 point degrees were computed as ordinary integers.  The totals are:

```text
connected cases checked:                 455
trivial kernels:                         443
nontrivial kernels exhausted:             12
total kernel vectors enumerated:      262,647
maximum in one case:                  262,144
vectors with all 27 point degrees 2:         0
```

Every independent nullspace basis vector was checked against the original
column syndromes, basis independence was checked, and rank plus nullity was
checked against the compatible-candidate count.  A separate transposition
back to 180 row masks reproduced all 455 discovery parity-matrix hashes,
deterministic reduced-row hashes, and deterministic nullspace-basis hashes.
The full connected certificate rows match exactly.

## 5. Independent mixed-case proof

In each mixed case, the 27 point vertices split into the nine edges of
\(K_{3,3}\) and the 18 edges of \(F_{12}\).  The independently reconstructed
candidate counts are:

| order-12 index | total | cross | inside \(K_{3,3}\) | inside \(F_{12}\) |
|---:|---:|---:|---:|---:|
| 0 | 163 | 162 | 0 | 1 |
| 1 | 162 | 162 | 0 | 0 |

With no candidate internal to the nine-point side, its total required degree
\(9\cdot2\) forces 18 selected cross edges.  The 18-point side requires total
degree \(18\cdot2=36\); after the 18 cross incidences, its remaining degree
sum is 18, forcing nine internal support edges.  One or zero available
internal candidates cannot supply nine distinct simple edges.  This excludes
both cases without any parity-kernel or SAT inference.

## 6. Hostile tests and replay

The 17 independent tests cover:

- valid graph6 decoding;
- truncated, overlong, bad-byte, header-bearing, and noncanonical-padding
  records;
- compressed-byte and record-count catalog tampering;
- positive and negative compatible-support examples;
- the absence of an internal \(K_{3,3}\) support candidate;
- a column kernel checked against brute-force tiny systems;
- rank-nullity and basis-syndrome validation;
- a deliberately corrupted basis vector;
- positive integer-degree enumeration;
- row-commitment reproduction;
- the sharp mixed degree-count threshold; and
- certificate mutation rejection.

They pass `17/17`.  The network-backed 457-case verifier was run twice and
produced byte-identical
`independent-result.json` with SHA-256

```text
159903af624a2df1975dd490ea5c267e453b5a96fe9744a9aa7a7be28390b056.
```

Its stable semantic manifest hash is

```text
9a28f3278fcb6ddd28ecff854603b12b592773026bbd870a9d42431fd45f4b57.
```

The discovery's six tests also pass, and its standalone verifier returns
`PASS`.  Rebuilding the certificate through captured stdout on Windows first
produced SHA-256

```text
7011541c066dc4ae6014dcd1538db027055b61151d069e2cd1cd4d18ae1784ad
```

over 325,348 bytes.  This was a benign wrapper-level newline difference:
captured stdout contained 6,917 CRLF pairs, while the frozen `--output` file
uses LF.  Replacing CRLF by LF produced 318,431 bytes, exactly byte-identical
to the frozen certificate and its declared SHA-256

```text
f5c66a2ba6ee0c8b0d4ea4a15411366000faf03fdcb431e19f26747d117ced12.
```

This failed raw comparison is retained here rather than hidden.  It is not a
semantic or certificate mismatch.

The verifier uses CPython 3.13.14, OpenSSL 3.0.21, Windows
11 `10.0.26200`, PowerShell 5.1.26100.8875, and no external Python package.
The security/path scan with ripgrep 15.1.0 found no credential-like value or
absolute user path in the verifier artifacts.

## 7. Status boundary

The result supported by this audit is:

```text
raw SAT statuses:                         UNSAT_UNVERIFIED / no evidence
455 connected fixed-F exclusions:        VERIFIED
2 mixed fixed-F exclusions:              VERIFIED
complete 457-case fixed-F census:         VERIFIED
conditional n3=54 exclusion:              VERIFIED, conditional on the
                                           structural and catalog premises
prospective conditional n3 lower bound:   57
prospective conditional induced C6 bound: 209343
Conway srg(99,14,1,2):                    UNKNOWN
novelty:                                  UNKNOWN
```

The arithmetic \(209286+57=209343\) was checked.  Promotion of the stronger
global conditional bounds should occur only when this audit is combined with
the separate structural audit and the earlier audited divisibility,
lower-bound, and induced-cycle identities.
