---
role: verifier
date_utc: 2026-07-23T20:06:45Z
git_commit: NOT_USED_PER_TASK_INSTRUCTION
claim_label: VERIFIED
audit_verdict: PASS
scope: >-
  Narrow independent audit of the ancillary hostile-ledger correction
  supplied as candidate commit 006b348. The already-closed Wave 23 proof
  audit and its artifact manifest are immutable inputs, not outputs.
inputs:
  agents/2026-07-23-wave23-endpoint-crosscheck.md: 11b0af31813748c903d67304d019c474a3d8660997744484d33f5d4c9c48c072
  attempts/wave23-endpoint-crosscheck/exact_check.py: 92c480e4b4c45f528f41f825d522982cd273c952104a7fe134b1b4acc161b2da
  attempts/wave23-endpoint-crosscheck/test_exact_check.py: 24ae053c2508e8e30c9118d9a58e90b2cf445b536df0de6066ec43143e850bb6
  attempts/wave23-endpoint-crosscheck/exact-results.json: 1b31074d0fe4872c14caf1e25842377e4ddab9860f241d87d2814a350ac100a4
  attempts/wave23-endpoint-crosscheck/failed-routes.md: 86e14750167d09ec330a801af5f81e5d1f3bc7f8ed4b56866de5d9ff5bb62abe
  attempts/wave23-endpoint-crosscheck/failed-runs.md: ca5f7078e352a1406c9260ead56f2f5cb9c775e1c9099e0ef5b2746190ecc8bb
  attempts/wave23-endpoint-crosscheck/run-report.yaml: b641ff06e810723f9ab0b6eec3a7ccf2eae17b53b8cce04c1b6535fb0c22f972
  verification/wave23-endpoint-crosscheck/submitted-regenerated.json: 68fbf3f4e8ee0510b4585a7d455f33c154cb2be173760f86303ae372a8c2db6d
  verification/wave23-endpoint-crosscheck/2026-07-23T195158Z-audit.md: 56cf0b8c14f9af50a58e60a8a6a273726a79d15782527ff8ea46194e9dea5d8c
  verification/wave23-endpoint-crosscheck/artifact-manifest.sha256: ad2e8811eb598fb37c67c28515e9f755ab8728165c379afb23670098786c7575
method: >-
  Blind seven-file byte/hash freeze; direct ledger and source inspection;
  independent finite enumeration of retained determinant constraints;
  structural JSON comparison against the preserved pre-correction result;
  25-test replay; in-memory deterministic regeneration; and validation of
  every file hash embedded in the corrected report and candidate run report.
command: |-
  python -B -m unittest discover -s attempts/wave23-endpoint-crosscheck -p test_exact_check.py -v
  python -B -  # independent stdlib JSON comparison and determinant enumeration recorded below
outputs:
  verification/wave23-endpoint-crosscheck/correction-freeze.sha256: 9b5954a3ce178c086e15b7b2f2835509b2b199579f0320c9d0520f3ab1bbe606
limitations:
  - The supplied correction commit identifier 006b348 was not queried with
    Git because this verifier was expressly forbidden from using Git.
  - This addendum verifies the correction only; it does not reopen novelty,
    construction, or target-existence status.
---

# Wave 23 endpoint-crosscheck correction audit

## Verdict

`PASS`.

The correction removes the false single-relaxation status of `(9,3,27)`,
retains that triple as a refuted historical control, and replaces it with the
valid witness `(9,1,9)`.  The executable mathematical result is byte-for-byte
reproducible and is semantically identical to the pre-correction result outside
`hostile_relaxations`.

The main endpoint proof remains `VERIFIED`.  This addendum changes no claim
about construction, target existence, or novelty.

## 1. Preinspection freeze and immutability

The seven corrected candidate files were hashed and byte-counted before their
contents were inspected.  The freeze was written at
`2026-07-23T20:04:01Z` to:

```text
verification/wave23-endpoint-crosscheck/correction-freeze.sha256
```

All seven entries matched again after inspection.  The closed verifier audit
and manifest retained their prior hashes:

```text
original audit     56cf0b8c14f9af50a58e60a8a6a273726a79d15782527ff8ea46194e9dea5d8c
original manifest  ad2e8811eb598fb37c67c28515e9f755ab8728165c379afb23670098786c7575
```

Neither closed artifact was edited.

## 2. The invalid control is preserved and refuted

Both `failed-routes.md` and `failed-runs.md` retain the historical triple

```text
(h,det(Q),det(B))=(9,3,27).
```

Both ledgers identify it as invalid under the claimed single relaxation.  The
independent residue check is immediate:

```text
h       = 9  = 1 mod 4,
det(Q)  = 3  = 3 mod 4,
det(B)  = 27 = 3 mod 4.
```

Thus the triple violates both retained determinant residues, including the
frozen consequence `det(B)=1 mod 4`.  It can arise only after dropping more
than the stated signature obstruction, and it is not used by the repaired
executable ledger or the main proof.

Status: `VERIFIED AS REFUTED CONTROL`.

## 3. The replacement is a valid single-relaxation witness

The new witness is:

```text
(h,det(Q),det(B))=(9,1,9).
```

Independent checks give:

```text
9 = 1 mod 4,  1 = 1 mod 4,  9 = 1 mod 4,
9 = 9*1,
9 = 3^2 is 3,7-smooth,
9 <= 42.
```

With the full endpoint constraints, the signature obstruction excludes
`det(Q)=1`, so an odd determinant congruent to one modulo four must satisfy
`det(Q)>=5`.  Independent enumeration with this lower bound, the determinant
cap 42, 3,7-smooth `h`, `h=1 mod 4`, the retained scaled-dual exclusion
`h!=1`, and all determinant residues leaves no pair.

Omitting only the even-unimodular signature obstruction permits `det(Q)=1`
while retaining the residue `det(Q)=1 mod 4`.  The same independent
enumeration then gives:

```text
(9,1,9), (21,1,21).
```

Therefore `(9,1,9)` is a valid survivor of exactly that relaxation.  It is not
the unique survivor, and neither corrected candidate artifact claims
uniqueness.

Status: `VERIFIED`.

## 4. Main result is unchanged outside the hostile ledger

The preserved pre-correction result has SHA-256
`68fbf3f4e8ee0510b4585a7d455f33c154cb2be173760f86303ae372a8c2db6d`.
The corrected result has SHA-256
`1b31074d0fe4872c14caf1e25842377e4ddab9860f241d87d2814a350ac100a4`.

After removing the top-level key `hostile_relaxations` from each parsed JSON
object, the objects compare exactly equal.  In particular, all frozen inputs,
endpoint data, scaled-dual facts, trace-square arithmetic, Maclaurin data,
determinant/index exhaustion, modular boundary, and conditional conclusions
are identical.

The corrected report's proof sections retain the already-verified chain and
add only the hostile-control correction and its provenance.  The main result
still says:

```text
n3=705 is conditionally excluded,
n3>=708,
induced C6 count >=209994,
target status UNKNOWN.
```

Status: `VERIFIED`.

## 5. Reproduction and hash audit

The submitted suite passed:

```text
Ran 25 tests in 0.516s
OK
```

Fresh deterministic serialization of `build_results()` was byte-identical to
the corrected submitted JSON:

```text
sha256 = 1b31074d0fe4872c14caf1e25842377e4ddab9860f241d87d2814a350ac100a4
bytes  = 5082
byte-identical = true
```

The YAML front matter of the corrected report and the candidate
`run-report.yaml` both parse.  Every declared input, output, and verifier-audit
hash was recomputed against the named file:

```text
embedded hash references checked = 25
mismatches = 0
```

## 6. Obligation table

| Obligation | Result |
|---|---:|
| Seven corrected files frozen before inspection | PASS |
| `(9,3,27)` retained in both ledgers | PASS |
| `(9,3,27)` explicitly refuted | PASS |
| `(9,1,9)` has all three residues equal to one modulo four | PASS |
| `(9,1,9)` satisfies factorization, smoothness, and cap | PASS |
| Witness arises by omitting only the `det(Q)=1` signature obstruction | PASS |
| Corrected JSON unchanged outside `hostile_relaxations` | PASS |
| Main proof and conditional bounds unchanged | PASS |
| Candidate tests | 25/25 PASS |
| Corrected JSON regeneration | BYTE-IDENTICAL |
| Corrected report/run hash references | 25/25 PASS |
| Construction or target nonexistence | NOT CLAIMED |
| Novelty | NOT ASSESSED |

Final scoped status:

```text
correction addendum: PASS
main endpoint cross-check: VERIFIED
historical (9,3,27) control: REFUTED AND RETAINED
replacement (9,1,9) control: VERIFIED
conditional n3 bound: >=708
conditional induced-C6 bound: >=209994
Conway-99 existence/nonexistence: unchanged / UNKNOWN
```
