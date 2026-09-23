# Wave 29 orchestrator correction and acceptance ledger

Date: 2026-07-24

Project status: `EXPLORATORY`

Target result: `UNKNOWN`

Accepted scoped claim:

```text
S0=K12 orthogonal_sum LAMBDA(F) cannot be the S-form of the
frozen full n3=708 projector/Schur endpoint package.
```

This claim is `VERIFIED` internally and the corresponding `S0` endpoint
origin is `REFUTED`. No other determinant-729 lattice is excluded.

## 1. Independent mathematical acceptance

The discovery package passes 18 tests. The blind verifier used a separately
written checker, passes 27 tests, regenerates its JSON byte identically, and
reconstructs every essential implication:

1. minimum-four support splitting gives the exact `63/168` row split;
2. the definitions force matching `M,W,Q,B` block decompositions;
3. the endpoint determinant constraints give `det(Q)=5`;
4. the rank-12 even-unimodular signature veto fixes
   `(det(Q_K),det(Q_L))=(5,1)`;
5. the row alphabet makes both block traces positive multiples of six;
6. exact AM--GM forces `(tr(B_K),tr(B_L))=(24,36)`;
7. `C_K=(B_K-I)/2` has trace six and an integral characteristic
   pseudodeterminant; and
8. the full-domain logarithmic inequality gives
   `det(B_K)<=3^6=729`, contradicting `det(B_K)=3645`.

All 14 entries in the mathematical discovery and verifier manifests match
their current files.

## 2. `C_K` positivity wording

An early shorthand described `C_K` as positive. That statement is too strong
and is not used. The accepted statement is:

```text
C_K is integral and G_K-self-adjoint;
B_K=I+2C_K has positive spectrum;
therefore every eigenvalue mu(C_K) is real and greater than -1/2.
```

Negative eigenvalues in `(-1/2,0)` are allowed. The discovery and verifier
both give a separate strict proof of the pointwise logarithmic inequality on
that interval.

## 3. Frozen-base metadata

The verifier's preinspection protocol inherited
`d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b`, the prior public Wave 27 head.
After opening the already hash-frozen inputs, it identified
`74b6f3adcee19ca2b0480258bb7bf51198bd085a` as the applicable local
mathematical base. The original entry remains visible in the protocol, with
the correction appended. The audit and run report use the corrected base.
No preinspection input hash or derivation changed.

## 4. Determinant rounding

The real inequality is

```text
det(Q)<=6525/729<9.
```

Only after using that `det(Q)` is a positive integer may this be written as
`det(Q)<=8`. Together with `det(Q)>=5` and `det(Q)=1 mod 4`, this leaves
`det(Q)=5`. Both accepted proofs use this order.

## 5. Publication-byte normalization

The pre-commit whitespace gate found one extra terminal blank line in the
verifier audit, one in its failure ledger, and one in the literature protocol.
Those blank lines were removed. The verifier run report and manifest and the
literature run report and manifest were repaired to the current hashes. The
literature run report preserves both the originally inspected verifier-audit
hash and the current normalized hash. No mathematical or source conclusion
changed.

Current verifier hashes:

```text
dbdcb88bf309cbfa47a42b9fb63dd7cf483e07cac8b92c475094c96be3723b7d  audit.md
c0418cec88915089d6cc2e29735ca3e7bc425cfcd2b3ce09a78a707e36e0aa04  independent-results.json
d6ddcbdb2c6141ff1731e4913c6436d9b6fd6cc3c5f2bdf6454cb38d85cc9764  run-report.yaml
6a62209abbca6403dee7b9ebf83edbdccd5466a278957ab9d63f37bcd3f08cf8  artifact-manifest.sha256
```

Current literature-package hashes:

```text
b6946969ac2337ff5e0f02afe78ec19ae96f62d1af0a7a9c5c57298a75fb863f  audit.md
923837b13066fdfe6db9362f5209ba722993e231ce7f0efbbc299be7cb0af970  query-ledger.json
c8f98b437cb14d8d87b66d3b3ebeb4f1fbd9c176c94314fcc5119f929df50e13  source-metadata.json
a1a55f8223810fab8602bf8ac59c6f18d3751064dbe58c73d04f8f0139944b4d  run-report.yaml
76898c9ecdcaba86bf14469700110f4ad45ea70ba576c7ebea73d725d0de9177  artifact-manifest.sha256
```

## 6. Literature boundary

The independent literature lane froze the exact combined proof signature
before searching. It logged 81 query strings in 21 batches and retained 16
primary or authoritative source records. It found standard sources for the
lattices, tight frames and spherical designs, the even-unimodular signature
veto, and pseudodeterminants, but no source for the exact combined
`63/168 -> 3645/1 -> 24/36 -> 729` exclusion.

The correct conclusion is:

```text
exact prior-art match: NO_MATCH_FOUND_IN_SEARCHED_SOURCES
novelty: UNKNOWN
recent target status: NO_RESOLUTION_FOUND_IN_SEARCHED_SOURCES
broader Conway-99 claim: UNKNOWN
```

The search retained no PDF, raw HTML, raw API response, or copyrighted full
text. One Crossref query was rate-limited, and Google Scholar, MathSciNet, and
zbMATH were not comprehensively machine-audited.

## Publication wall

The accepted Wave 29 result excludes exactly one previously retained
rootless bare-lattice control from carrying the full endpoint package. It
does not classify another `h=729` lattice, exclude the determinant-729 row,
exclude `n3=708`, improve `n3>=708`, construct a graph, resolve Conway-99,
or establish novelty. Every broader status remains `UNKNOWN`.
