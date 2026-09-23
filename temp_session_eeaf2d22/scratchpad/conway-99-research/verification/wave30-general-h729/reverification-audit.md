# Wave 30 repaired general-`h=729` independent re-verification

```yaml
role: verifier
date_utc: 2026-07-24T05:23:50Z
git_commit: a7be6b8ae70d8b44e88db8dfd6804f8d946ca382
claim_label: VERIFIED
audit_verdict: PASS_SCOPED_CONDITIONAL_THEOREM
publication_gate: PASS_SCOPED_CONDITIONAL_THEOREM
scope: >-
  Re-verification of the repaired Wave 30 conditional classification for
  rootless, even, integral, positive-definite rank-44 determinant-729 S-forms
  with a nontrivial integral orthogonal decomposition and the frozen full
  n3=708 projector/Schur endpoint package. Fourteen of fifteen aggregate
  block types are excluded; only the rank-20 determinant-729 plus rank-24
  even-unimodular type survives this reduction.
inputs:
  repaired_commit: a7be6b8ae70d8b44e88db8dfd6804f8d946ca382
  original_discovery_commit: 091d0a458ab1f96e3b3f491b677c84824bbf8f44
  original_verifier_veto_commit: 0bc6dc9b90dff6589cfaf9db1a84e2d8242b6321
  attempts/wave30-general-h729/exact_check.py: b3c2b4c79b23f418cb63876560236d62e0be2c6cac69979106e03e5a8247d6a5
  attempts/wave30-general-h729/test_exact_check.py: 9075d5fd77253850ba09c4655d9cbab135eb32fdd36638dc4aa9051fa49898a2
  attempts/wave30-general-h729/exact-results.json: cb0a58195506a51ca6a39aaab197a3592344f7aef8b5b0c2af51770c7069ad6c
  attempts/wave30-general-h729/repair-ledger.md: 1cf8aa09a65b552e7d81d2d9e46df6e59ce67222be6469094e9d788f99959cbd
  verification/wave30-general-h729/independent_check.py: 2ad3594e975853143f7bacf7f97589e10ae18c50fa78747b67cee176e4895cbb
  verification/wave30-general-h729/test_independent_check.py: 701c2c8af0eb746c735004cc3ff41dd9ab57d9da807e82205acebe97ef01df79
  verification/wave30-general-h729/test_hostile_controls.py: d7aeea72cea60c345ecd979a5a5771d050c466c6972708b4f94c3e2a29a784dc
  verification/wave30-general-h729/independent-results.json: 2b948591611e9c984985f7bacc5a77c714332fbe42ed5305b84039c621358416
method: >-
  Exact repaired-commit byte freeze and diff audit; hermetic replay of the
  repaired submitted package; hermetic reproduction of the original replay
  failure; hermetic replay of the unchanged historical independent verifier
  at its veto commit; fresh adversarial inspection of every scope wall,
  determinant/rank reduction, row equation, AM-GM and logarithmic inequality,
  equality split, tensor bound, and hostile control; and an additional
  no-import micro-enumeration.
command: |-
  git archive --format=tar --output=<temporary-directory>/repo.tar a7be6b8ae70d8b44e88db8dfd6804f8d946ca382
  cd <temporary-directory>/attempts/wave30-general-h729
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output <temporary-directory>/exact-regenerated.json
  git archive --format=tar --output=<temporary-directory>/repo.tar 091d0a458ab1f96e3b3f491b677c84824bbf8f44
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output <temporary-directory>/original-regenerated.json
  git archive --format=tar --output=<temporary-directory>/repo.tar 0bc6dc9b90dff6589cfaf9db1a84e2d8242b6321
  cd <temporary-directory>/verification/wave30-general-h729
  python -B -m unittest -v test_independent_check.py test_hostile_controls.py
  python -B independent_check.py --output <temporary-directory>/independent-regenerated.json
outputs:
  repaired_exact_results_sha256: cb0a58195506a51ca6a39aaab197a3592344f7aef8b5b0c2af51770c7069ad6c
  historical_independent_results_sha256: 2b948591611e9c984985f7bacc5a77c714332fbe42ed5305b84039c621358416
  audit_record: verification/wave30-general-h729/reverification-audit.md
limitations:
  - The theorem remains conditional on the frozen full endpoint package.
  - The rank-20 plus rank-24 survivor is neither constructed nor excluded.
  - Rooted and integrally indecomposable determinant-729 forms are untreated.
  - Tensor counts are necessary conditions, not a frame, lattice, M, X, or graph.
  - n3=708, Conway-99, and novelty remain UNKNOWN.
```

## Verdict

```text
repaired discovery revision a7be6b8...:                 PASS
scoped conditional mathematical classification:        VERIFIED
publication gate for repaired revision:                 PASS_SCOPED_CONDITIONAL_THEOREM

original discovery revision 091d0a4... replay:          FAIL
original verifier objection V30-GEN-001:                PRESERVED
rank-20 plus rank-24 survivor existence/nonexistence:    UNKNOWN
rooted or integrally indecomposable h=729 forms:         UNKNOWN
n3=708, Conway-99, and novelty:                          UNKNOWN
```

The repaired revision is publishable only with this exact conditional scope.
This verdict does not retroactively relabel the original failed submission.

## 1. Repaired submitted replay

The repaired package was extracted from the exact Git object
`a7be6b8ae70d8b44e88db8dfd6804f8d946ca382`, not executed from mutable
working-tree discovery files.

```text
python -B -m unittest -v test_exact_check.py
Ran 20 tests
OK

python -B exact_check.py --output <temporary-directory>/exact-regenerated.json
exit: 0
```

The regenerated file matched the checked artifact byte for byte:

```text
bytes:   16125
sha256:  cb0a58195506a51ca6a39aaab197a3592344f7aef8b5b0c2af51770c7069ad6c
result:  BYTE_IDENTICAL
```

The eight-entry discovery manifest and five-entry input freeze each validated
with zero syntax, missing-path, or hash findings.

## 2. Original failure reproduced and retained

The original package was separately extracted from
`091d0a458ab1f96e3b3f491b677c84824bbf8f44`.

```text
python -B -m unittest -v test_exact_check.py
Ran 0 tests
FAILED (errors=1)

python -B exact_check.py --output <temporary-directory>/original-regenerated.json
exit: 1
output written: false
```

The reproduced mismatch is exactly:

```text
submitted expected:
4101a394252807fb9de8c39fb32b780bc88410d99e47dfe698da251b49f3e061

committed observed:
dbdcb88bf309cbfa47a42b9fb63dd7cf483e07cac8b92c475094c96be3723b7d

path:
verification/wave29-s0-frame-exclusion/audit.md
```

Thus `V30-GEN-001` remains `FAIL` for the original submitted revision. The
repair receives a distinct disposition below.

## 3. Historical independent verifier replay

The files under `verification/wave30-general-h729` are byte-identical between
the historical veto commit and the repaired discovery commit. Their hard
freeze of the original discovery bytes is an intentional archive invariant,
so they were replayed hermetically at
`0bc6dc9b90dff6589cfaf9db1a84e2d8242b6321`.

```text
python -B -m unittest -v test_independent_check.py test_hostile_controls.py
Ran 32 tests
OK

python -B independent_check.py --output <temporary-directory>/independent-regenerated.json
exit: 0
```

The regenerated independent result matched byte for byte:

```text
bytes:   22020
sha256:  2b948591611e9c984985f7bacc5a77c714332fbe42ed5305b84039c621358416
result:  BYTE_IDENTICAL
```

Its eight-entry historical verifier manifest validated with zero findings.
The historical code, tests, result JSON, and their hashes remain unchanged;
they were not patched to make an old freeze accept new discovery bytes.

## 4. Adversarial theorem inspection

The re-verifier inspected the implementation and reconstructed each step
without importing either checker.

### Integral split and determinant census

- A unimodular integral orthogonal decomposition preserves integral row
  coordinates. Minimum four forces every norm-four row into exactly one
  block. Therefore `X`, `M`, `W`, `Q`, `B`, and `C` split.
- `4 n_J = 21 rank(J)` forces each original block rank to be divisible by
  four.
- `det(Q)=5` and positive integral block determinants put determinant five on
  exactly one block; every other `Q` block is even unimodular and has rank
  divisible by eight.
- The exceptional rank is consequently one of `4,12,20,28,36`. The standard
  odd-determinant congruence and the even-unimodular signature theorem leave
  exactly exponents `2,4,6` for its `3`-power determinant. These are the
  complete fifteen aggregate types.
- An independent unordered-partition enumeration found 18 complement
  partitions into positive multiples of eight. Grouping multiple complement
  blocks therefore hides no aggregate type.

### Row alphabet, trace pairs, and caps

- Direct enumeration of the row-sum, square-sum, and row-count equations
  found exactly the thirteen solutions
  `(a,b,c,z)=(32-c,36-3c,c,162+3c)`, `0<=c<=12`.
- The cubic row sum is exactly `60-6c`, so every positive block trace is a
  multiple of six.
- Exact integer AM-GM gives the same unique trace pair or exclusion for all
  fifteen types.
- For every real eigenvalue `x>-1/2` of integral, positive-form-self-adjoint
  `C`, the logarithmic proof treats positive, zero, and negative `x`
  separately. The nonzero characteristic coefficient is a nonzero integer,
  so its absolute pseudodeterminant is at least one. No positive-semidefinite
  assumption is smuggled in.
- Equality forces every nonzero eigenvalue of `C` to be one. Real
  diagonalizability gives an integral idempotent. Its image and kernel form a
  unimodular, form-orthogonal split, and the two nonzero `Q` restrictions are
  even unimodular.
- The four forbidden equality splits have image/kernel ranks
  `(4,36)`, `(2,30)`, `(4,12)`, and `(2,6)`. The surviving `(20,6)` case has
  `(0,24)` and is correctly retained.

The independent no-import micro-enumeration reproduced:

```text
det(Q) candidates:                    [5]
row-alphabet solutions:               13
rank/determinant types:               15
complement partitions checked:        18
unique surviving aggregate type:      (20,6)
forbidden equality image ranks:        4,2,4,2
```

### Surviving boundary and scope wall

For the unique survivor, exact AM-GM equality on the complement gives
`B_U=I_24` because `B_U` is real diagonalizable. The shell split is
`105/126`, and the Schur traces are `36/24`.

The tensor-isometry calculation was also rechecked:

```text
|sum_j <y_i,y_j>^3| <= 8
c_i in {9,10,11}
sum_i c_i = 1256
62 aggregate profiles
directed totals (+1,-1,-2,0) = (2776,768,1256,10950)
```

These are necessary arithmetic conditions only. They do not construct the
surviving lattice, a frame, `M`, `X`, or a graph. The scalar spectrum control
is likewise not a realization.

No mathematical objection survived this inspection.

## 5. Revisioned dispositions and self-corrections

### V30-GEN-001: original stale frozen input

Status: `FAIL`, preserved for
`091d0a458ab1f96e3b3f491b677c84824bbf8f44`.

The original suite still runs zero tests and its generator still writes no
output. This disposition is not changed.

### V30-GEN-015: repaired revision re-verification

Status: `PASS_SCOPED_CONDITIONAL_THEOREM`, applicable only to
`a7be6b8ae70d8b44e88db8dfd6804f8d946ca382`.

The corrected committed hash, dependent result bytes, input freeze, and
manifest all replay. The unchanged submitted test semantics pass 20 tests.
The unchanged historical independent verifier passes 32 tests in its frozen
context, and the repair diff changes no mathematics.

### V30-GEN-016: first repaired-archive helper parse error

The first PowerShell archive-replay helper used unsupported generic-method
syntax and ambiguous colon-delimited variable interpolation. PowerShell
rejected the script at parse time before creating a temporary directory,
extracting an archive, running a test, or writing an artifact.

The corrected helper used an exact Base64 representation comparison for byte
equality and format-string interpolation. All reported replay evidence comes
from the corrected successful command.

### V30-GEN-017: first UTC capture used an unavailable parameter

The first timestamp helper used `Get-Date -AsUTC`, which is unavailable in the
installed Windows PowerShell. It emitted no timestamp. The timestamp was
immediately recaptured with `(Get-Date).ToUniversalTime()`; no evidence or
artifact content depended on the failed command.

## 6. Final status wall

```text
conditional decomposable-rootless classification:       VERIFIED
publication gate for exact repaired commit a7be6b8...:  PASS_SCOPED_CONDITIONAL_THEOREM
original submitted replay at 091d0a4...:                 FAIL
surviving rank-20 plus rank-24 type:                     UNKNOWN
rooted h=729 forms:                                      UNKNOWN
integrally indecomposable h=729 forms:                   UNKNOWN
all h=729 endpoint forms:                                UNKNOWN
n3=708:                                                  UNKNOWN
Conway-99:                                               UNKNOWN
novelty:                                                 UNKNOWN
```

Verifier execution identity:

```text
model: gpt-5.6-sol
reasoning_effort: max
```
