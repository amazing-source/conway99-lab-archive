# Wave 30 orchestrator correction and acceptance ledger

Date: 2026-07-24

Project status: `EXPLORATORY`

Target result: `UNKNOWN`

Accepted scoped results:

```text
rootless integrally orthogonally decomposable h=729 endpoint reduction:
  VERIFIED, conditional on the full frozen n3=708 projector/Schur package

exact bare T20 and T20 orthogonal_sum LAMBDA24 S/G construction:
  VERIFIED at the lattice layer only

n3=708 / Conway-99 / novelty:
  UNKNOWN
```

## 1. Original general-package veto

The first discovery package is preserved at
`091d0a458ab1f96e3b3f491b677c84824bbf8f44`. Its checker froze the
transient SHA-256

```text
4101a394252807fb9de8c39fb32b780bc88410d99e47dfe698da251b49f3e061
```

for `verification/wave29-s0-frame-exclusion/audit.md`, while the applicable
committed bytes have

```text
dbdcb88bf309cbfa47a42b9fb63dd7cf483e07cac8b92c475094c96be3723b7d.
```

The independent verifier therefore recorded `V30-GEN-001` and a publication
veto at `0bc6dc9b90dff6589cfaf9db1a84e2d8242b6321`:

```text
submitted tests run: 0
submitted generator: FAIL before output
scoped independent mathematical reconstruction: 32/32 PASS
```

The failure remains a failure for that exact revision. It was not rewritten
as a successful run.

## 2. Provenance-only repair

Commit `a7be6b8ae70d8b44e88db8dfd6804f8d946ca382` substitutes only the
applicable committed Wave 29 audit hash, regenerates the dependent JSON and
checksum metadata, and adds an explicit repair ledger. The test source and
failed-routes record are byte-identical to the original discovery revision.
No lemma, arithmetic constant, aggregate type, tensor count, scope wall, or
status boundary changed.

The repaired package has:

```text
20/20 submitted tests: PASS
regenerated JSON: byte-identical
JSON SHA-256:
  cb0a58195506a51ca6a39aaab197a3592344f7aef8b5b0c2af51770c7069ad6c
8/8 discovery-manifest entries: PASS
5/5 input-freeze entries: PASS
```

## 3. Independent re-verification

The fresh GPT-5.6/Sol verifier at max reasoning froze the exact repaired
commit before inspection. Its revisioned verdict is preserved at
`9d579856fdb1b903e42a70307b1d9ea45a8785d4`:

```text
V30-GEN-001:
  FAIL_ORIGINAL_REVISION_PRESERVED

V30-GEN-015:
  PASS_SCOPED_CONDITIONAL_THEOREM_REPAIRED_REVISION
```

It hermetically replayed three distinct states:

1. repaired discovery `a7be6b8...`: 20/20 tests and byte-identical JSON;
2. original discovery `091d0a4...`: zero tests and generator failure; and
3. historical independent verifier `0bc6dc9...`: 32/32 tests and
   byte-identical JSON with SHA-256
   `2b948591611e9c984985f7bacc5a77c714332fbe42ed5305b84039c621358416`.

The historical verifier code and its eight-entry manifest remain unchanged.
The new twelve-entry re-verification manifest is separate, with container
SHA-256
`8f6cba4e72ac38c73852ed3c7b549df8c123fa87e59fffbd1a6569eb235bbefe`.

The verifier retained two harmless command self-corrections:

- `V30-GEN-016`: an initial PowerShell archive helper failed to parse before
  creating a temporary directory or producing evidence;
- `V30-GEN-017`: an unavailable UTC parameter produced no timestamp, after
  which UTC was captured by a compatible command.

Neither failed command supports any mathematical claim.

## 4. Accepted conditional classification

Assume the full frozen `n3=708` endpoint package and let `S` be rootless,
even, integral, positive definite, rank 44, determinant 729, and nontrivially
integrally orthogonally decomposable. Minimum four forces the 231 norm-four
frame rows to be block supported. The induced `M,W,Q,B,C` data split, and
exact determinant, signature, trace-residue, AM--GM, logarithmic-cap, and
equality/idempotent arguments exclude fourteen of fifteen aggregate
rank/determinant types.

The only surviving necessary type is:

```text
S = A20 orthogonal_sum U24

rank(A20), det(A20) = 20,729
rank(U24), det(U24) = 24,1
frame rows = 105,126
det(Q_A), det(Q_U) = 5,1
det(B_A), det(B_U) = 3645,1
tr(B_A), tr(B_U) = 36,24
B_U = I24.
```

Here `A20` is only a local label for the rank-20 determinant-729 block. It is
not the ADE root lattice `A_20`, and the theorem does not identify it with
the separately constructed `T20`.

The 62 surviving row-count profiles are necessary arithmetic profiles, not
frames or realizations. Rooted, integrally indecomposable, rationally split,
and minimum-two cases are outside this theorem.

## 5. Exact bare construction

The construction package at `f8a123708d3286a09fa8ba47d0a8ac18d6d2a0d6`
and independent verifier at
`5a5eebfc888d7e3f278390a165de66b0c07235b4` establish:

```text
rank(T20)=20
det(T20)=729
min(T20)=4
number of norm-four vectors=5076
exact level=3
3*T20^(-1) and 21*T20^(-1) are even integral
Gram SHA-256:
  1890fe1973eed47850c307d0975ae393f2a8ab32a9d0b16b35ebcab7012445d6
root counts:
  240 -> 112 -> 48 -> 20 -> 6 -> 0
```

The exact direct sum

```text
S44=T20 orthogonal_sum LAMBDA24
G44=21*S44^(-1)
```

is rootless, even, integral, positive definite, rank 44, and determinant
729, with `S44*G44=21*I44`.

The discovery suite passes 16 tests and the independently written verifier
passes 24 hostile tests. Both deterministic JSON regenerations are
byte-identical.

The construction verifier's publication-byte normalization and its
`V30-C-F004` record are retained in
`verification/wave30-h729-construction/failure-ledger.md`. No mathematical
claim changed during that normalization.

## 6. Orchestrator replay failures retained

One preliminary construction-suite wrapper used a 60-second process timeout.
The suite printed all 16 tests and `OK` at 61.6 seconds, but the wrapper
returned a timeout code. That run supplied no evidence. A nonblocking rerun
completed with process exit code zero in 60.6 seconds and is the accepted
root replay.

The first root historical-archive helper used
`New-Item -LiteralPath`, unavailable in the installed Windows PowerShell. It
failed before creating an archive or running a test. The compatible rerun
used `New-Item -Path`, passed all 32 historical verifier tests, and reproduced
the independent JSON byte for byte. The failed helper supplied no evidence.

## 7. Literature boundary

The independent Wave 30 source audit froze both exact signatures before
searching. It logged 96 query strings in 24 batches across web search, arXiv,
OpenAlex, and Crossref, and retained 21 primary or authoritative metadata
records with no raw source payloads. One Crossref query returned HTTP 429.

The correct conclusion is:

```text
exact prior result for either frozen signature:
  NOT FOUND IN SEARCHED SOURCES

novelty / priority / globally complete openness claim:
  UNKNOWN
```

Current primary records inspected still treat Conway-99 as unresolved, but a
bounded search cannot certify global status.

## Publication wall

Wave 30 classifies only the rootless, integrally orthogonally decomposable
`h=729` endpoint category and constructs one exact bare lattice of the
surviving rank/determinant shape. It supplies no determinant-five `Q`,
compatible `B`, 105/126 frame, `X`, `M`, `W`, Schur-square certificate, or
graph for `T20 orthogonal_sum LAMBDA24`. The surviving decomposable type is
not excluded, rooted and integrally indecomposable forms remain untreated,
the `h=729` row remains open, `n3=708` remains open, the lower bound remains
`n3>=708`, and Conway-99 and novelty remain `UNKNOWN`.
