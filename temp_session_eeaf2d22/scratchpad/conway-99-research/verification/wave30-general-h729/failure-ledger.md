# Wave 30 general-h729 verifier failure and objection ledger

## Active objection

### V30-GEN-001: submitted frozen-input hash is stale

Status: `FAIL`, publication-blocking for the submitted discovery package.

The submitted checker expects SHA-256
`4101a394252807fb9de8c39fb32b780bc88410d99e47dfe698da251b49f3e061`
for
`verification/wave29-s0-frame-exclusion/audit.md`; the current committed file
and its only tracked historical blob have SHA-256
`dbdcb88bf309cbfa47a42b9fb63dd7cf483e07cac8b92c475094c96be3723b7d`.
Therefore:

```text
submitted unit tests: 0 tests, setUpClass ERROR
submitted generator: ERROR before output
```

Disposition: do not repair discovery files in the verifier lane. The
orchestrator must preserve the failed revision, record a new repair, regenerate
dependent outputs and manifests, and request re-verification.

This objection does not falsify the mathematical implication. The independent
checker uses the current committed audit and reconstructs the theorem without
importing discovery code.

## Verifier corrections retained

### V30-GEN-002: fifth complement equality initially omitted from one test

The first independent test incorrectly expected exactly the four
publication-table equality vetoes. The surviving `(rank(A),a)=(20,6)` type
also has complement log equality, with `C_U=0`, image rank zero, and kernel
rank 24. It is permitted rather than vetoed.

The failing test was preserved in command output, then corrected to distinguish:

```text
five complement equality cases,
four forbidden positive image ranks,
one permitted zero image rank.
```

The classification code already handled the survivor correctly; only the
verifier assertion was wrong.

### V30-GEN-003: protocol hash transcription corrected before inspection

While writing the blind protocol, the SHA-256 line for `OBLIGATIONS.yaml` was
transcribed once with an extra digit. It was immediately corrected from the
already captured command output before any discovery content was opened. No
discovery hash, file content, or blindness boundary changed.

### V30-GEN-012: first byte-comparison helper used an unavailable method

The first post-generation PowerShell helper attempted to call
`SequenceEqual` as an instance method on a byte array. That host method is
unavailable, so the helper printed no Boolean comparison. Both regenerated
files and the checked-in result nevertheless had the identical SHA-256
`2b948591...`; the Python test suite also performs a direct byte comparison
and passed. No artifact was changed by the failed helper.

### V30-GEN-013: first manifest-validator command had a PowerShell parse error

The first manifest-validation command interpolated colon-delimited variables
without braces, and PowerShell rejected the command before executing any
validation. A corrected format-string version then checked all eight manifest
entries, all nine package files, YAML/JSON parsing, LF/NUL/trailing whitespace,
and privacy patterns with zero findings.

### V30-GEN-014: orchestrator publication-byte normalization

The final read-only package audit found that `audit.md` ended with two LF
bytes and that this ledger abbreviated the two hashes in the active
provenance objection. Before the verifier package was committed, the
orchestrator removed the extra terminal blank line, expanded both hashes in
full, and refreshed the dependent run report and manifest.

The pre-normalization hashes remain recorded here:

```text
b1eb875095c7f7e81752b1c0dc5d28234f52be86b0913389eff446a3e9ae35ff  audit.md
facc57b90542caf4e2b1c004ebfe894e91dbd784a47ecad3eea1860138c29a71  failure-ledger.md
a7a7394b2ad641632e5fde8ba9a8b440120ad7e39b30ac31fcfb535ede4505ca  run-report.yaml
5cdd1532ceb18a6cedd3669996f9017394b6f54ea07a8ae4efc0bd8f263e4941  artifact-manifest.sha256
```

No discovery byte, mathematical conclusion, replay outcome, or status
boundary changed.

## Adversarial objections discharged

### V30-GEN-004: grouping many complement blocks might hide a type

Disposition: `PASS`.

The checker independently enumerates every unordered partition of each
complement rank into positive multiples of eight. All original determinant-one
`Q` blocks are even unimodular; grouping them preserves `det(Q_R)=1`,
integrality, evenness, positivity, self-adjointness, and the log-cap
hypotheses. Every actual decomposition maps to one of the fifteen aggregate
types.

### V30-GEN-005: a rational orthogonal split might be mistaken for an integral one

Disposition: `PASS`, premise confirmed essential.

The rootless form `4I_2` and rational orthogonal lines spanned by `(1,1)` and
`(1,-1)` give `(1,0)` two half-integral nonzero projections. The proof uses a
unimodular integral decomposition and does not apply to this control.

### V30-GEN-006: minimum four might be used only cosmetically

Disposition: `PASS`, premise confirmed essential.

Two nonzero orthogonal components of norm two make a norm-four mixed row.
Without minimum four, block support and every downstream Schur split fail.

### V30-GEN-007: the logarithmic cap might assume `C` is PSD

Disposition: `PASS`.

No PSD assumption is used. All eigenvalues are real and greater than
`-1/2`; the negative interval is treated separately and strictly. Integrality
enters only through the nonzero characteristic coefficient.

### V30-GEN-008: equality might not give an integral direct split

Disposition: `PASS`.

Equality makes every nonzero eigenvalue one. Real diagonalizability gives an
idempotent. For integral `C`,
`v=Cv+(I-C)v` splits every integer vector into integral image and kernel
parts, with zero intersection. Self-adjointness makes them `G`-orthogonal.

### V30-GEN-009: the rank veto might be applied to a nonintegral or odd block

Disposition: `PASS`.

In the adapted unimodular basis, `Q=GB/21` is block diagonal and remains even
integral. Its positive block determinants multiply to one, so each nonzero
block is even unimodular. An odd rank-two identity matrix is retained as a
control showing why evenness is essential.

### V30-GEN-010: AM-GM equality may give only the spectrum of `B_U`

Disposition: `PASS`.

`B_U` is similar to a symmetric positive-definite matrix, hence
diagonalizable. Product one and trace 24 in rank 24 force all eigenvalues one,
and diagonalizability then forces the matrix itself to be `I_24`.

### V30-GEN-011: tensor counts might be promoted to existence

Disposition: `PASS`, scope wall retained.

The 62 aggregate profiles and directed totals are necessary arithmetic only.
No symmetric alphabet matrix, frame, Schur-square package, lattice
realization, or graph is inferred from them.

## Non-evidentiary routes rejected

- The scalar spectrum `{2,1^6,0^13}` is not a lattice or frame.
- Parity-compatible directed counts are not an existence certificate.
- The absence of another scalar contradiction is not evidence that the last
  decomposition type exists.
- No Leech/Niemeier classification was needed or used.
- No conclusion was transferred to rooted or integrally indecomposable forms.
- No failed search was treated as nonexistence.
