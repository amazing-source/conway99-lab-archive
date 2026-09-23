# Wave 34 external-source verifier: Harrison Lane E2

Date: 2026-07-24

Role: verifier

External pin: `harrisonpedrero/conway-99-graph@26b36c540611fa02c95a5a4bd78cd4a582257195`

## Handoff verdict

The honest rooted model and its bridge from an arbitrary
`srg(99,14,1,2)` root are `VERIFIED`. The tracked honest CNF builder does not
call the retracted R204 forced-edge routine. The all-21-C4 endpoint does imply
the R204 table, so the conditional R230 cap is connected correctly without
restoring the old unconditional claim.

Independent exact checks passed for:

- all S7 orbit partitions from k20 through k13;
- every Part-A leaf-stripping target (122 k18-k14 orbit types, plus k20,
  k19, and 75 k13 types);
- all 830 k>=14 and 472 k13 CNF recipe hashes; and
- the exact `-4` eigenspace Gram identities
  `w0=1`, `w1=-2/7`, `w2=1/28`.

No complete exclusion rung can be promoted:

- the 830 ladder CNFs and all ladder DRAT/LRAT bodies are absent from Git;
- the 14 claimed exact-rational certificates and checker are absent from Git;
- the six non-Gram cores have author logs but no bodies;
- R230 has 48 matching Git LFS pointers and consistent logs, but the bodies
  were not pulled or checked; and
- k13 `res1` is still cloud-verdict-only.

The first verifier result serialized wall-clock time and therefore failed an
orchestrator byte-reproducibility rerun. That release failure is retained in
the
[`reproducibility correction`](../verification/wave34-external-source-audit/harrison/reproducibility-correction.md).
After removing only the timing field, two exact isolated-venv reruns produced
the identical `results.json` SHA-256
`0d9ea150bb86e33c00f46e72620dec61e0a2b84c130597596299d80ab8e8baf2`.
No mathematical or status field changed.

Final labels:

```text
rooted bridge and Part-A structure: VERIFIED
CNF recipe identity:                VERIFIED
R230 UNSAT:                         UNKNOWN
k>=14 exclusion:                    UNKNOWN
k=13 exclusion:                     UNKNOWN
Conway-99:                          UNKNOWN
n3=708:                             UNKNOWN
external import:                    NONE
```

The full audit package is
[`verification/wave34-external-source-audit/harrison/audit.md`](../verification/wave34-external-source-audit/harrison/audit.md).
Machine-readable results are in
[`results.json`](../verification/wave34-external-source-audit/harrison/results.json),
with the 1,302-instance ledger in
[`certificate-ledger.json`](../verification/wave34-external-source-audit/harrison/certificate-ledger.json).

One reproducibility defect is recorded: direct execution of the tracked
`theorem_k19/scripts/honest_flip_cnf.py` fails with
`ModuleNotFoundError: No module named 'source'`. The tracked
`rebuild_and_verify.py` repairs the path before import and all 830 hashes still
match, so this is an entry-point defect rather than formula drift.
