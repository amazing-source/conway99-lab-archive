# Wave 37 integration audit

Verdict: **PASS for the scoped Wave 37 public checkpoint**

The three discovery suites and three independent suites pass 42 tests. The
finite-polar result and all three independent result files reproduce exactly,
the branch-15 OPB exporter and auditor pass their deterministic tests, and an
independent implementation reconstructs all 574,615 OPB constraints
byte-for-byte. Structured metadata, hashes, evidence paths, local links,
privacy patterns, and Git whitespace also pass.

```yaml
role: verifier
date_utc: 2026-07-27T00:39:35Z
git_commit: a45592a91a34d2f2bb7ee4c266f3b979e86e399d
claim_label: VERIFIED
scope: >-
  Integration and publication-metadata audit of the Wave 37 rooted
  fixed-triangle clauses, finite-polar restrictions, and branch-15
  proof-formula artifact. This is not a satisfiability result or an endpoint
  exclusion.
inputs:
  - "README.md, REPRODUCING.md, and STATUS.yaml"
  - "CLAIMS.yaml and OBLIGATIONS.yaml"
  - "agents/2026-07-26-wave37-polar-strengthen.md"
  - "agents/2026-07-27-wave36-rooted-branches.md"
  - "attempts/wave36-rooted-branches/"
  - "attempts/wave37-polar-strengthen/"
  - "attempts/wave37-proof-producing-endpoint/"
  - "verification/wave37-rooted-branches/"
  - "verification/wave37-polar-strengthen/"
  - "verification/wave37-proof-producing-endpoint/"
  - "logs/2026-07-27-wave37-public-checkpoint.json"
method: >-
  Freshly replay the six test suites and four deterministic result
  verifications; reconstruct and compare the full branch-15 OPB constraint
  stream with an implementation that does not import discovery code; check
  Exact parser acceptance separately from satisfiability; strictly parse YAML
  and JSON; check status, freeze, and run-report hashes; resolve Wave 37
  evidence paths and local Markdown links; scan the intended publication set
  for credential-shaped data and private local paths; and inspect status
  boundaries and Git whitespace.
command: |-
  Run the Wave 37 commands listed in REPRODUCING.md.
  .\.venv\Scripts\python.exe -B - <strict structure, hash, evidence, and link audit>
  rg -n -i <credential and private-path patterns> <intended publication paths>
  git diff --check
outputs:
  - path: verification/2026-07-27-wave37-integration-audit.md
    sha256: "Recorded externally after this self-referential report is frozen"
limitations:
  - "Every mathematical conclusion is conditional on n3=4158."
  - "The rooted catalogs encode only prisms meeting one of six fixed triangles, not every prism."
  - "The published OPB formula covers one of 33 endpoint-compatible refined cases."
  - "Exact parser acceptance is a syntax check, not a SAT or UNSAT certificate."
  - "Nonterminal solver sweeps and the incomplete block-completion lane are excluded."
  - "A finite privacy-pattern scan cannot prove arbitrary prose contains no sensitive information."
audit_verdict: PASS_SCOPED_WAVE37_PUBLIC_CHECKPOINT
```

## Replay results

| Package | Discovery | Independent | Deterministic comparison |
|---|---:|---:|---|
| rooted fixed-triangle clauses | 8 passed | 5 passed | five catalogs reproduced |
| finite-polar restrictions | 13 passed | 6 passed | both JSON results reproduced |
| branch-15 OPB artifact | 5 passed | 5 passed | 574,615 constraints matched |
| **Total** | **26** | **16** | **42/42 tests passed** |

The compressed branch-15 formula was also accepted by the pinned Exact binary
under `--onlyparse`. That exit status is retained only as syntax evidence.
There is no assignment, contradiction proof, or solver conclusion.

## Structural and metadata checks

The strict integration audit found:

```text
strict JSON files parsed:                  11
strict YAML files parsed:                   9
claim IDs:                                103 unique
obligation IDs:                            93 unique
Wave 37 evidence references:               29
STATUS path/hash bindings:                 11
run-report path/hash bindings:             58
input-freeze entries:                       7
local Markdown links checked:             342
hash or link mismatches:                     0
credential/private-path pattern hits:        0
git diff --check:                          PASS
```

Strict JSON and YAML parsing reject duplicate mapping keys. Hash checks compare
the actual file bytes. A first privacy pass found local machine paths in parser
records; those records were corrected to portable `$EXACT` and `$FORMULA`
tokens, their hashes were updated, and the final scan had zero hits. Three
verifier run reports were also corrected so their test counts use the
top-level schema required by the research protocol.

## Status discipline

The integrated status wall preserves these boundaries:

```text
partial fixed-triangle prism clauses: VERIFIED scoped
finite-polar restrictions:            VERIFIED scoped
branch-15 OPB bytes and structure:     VERIFIED artifact-only
branch-15 satisfiability:              UNKNOWN
complete 33-case endpoint result:      UNKNOWN
n3=4158 endpoint:                      UNKNOWN
rigorous interval:                     708 <= n3 <= 4158
upper bound below 4158:                NOT OBTAINED
Conway-99 and novelty:                 UNKNOWN
```

The explicit finite-field counterexample refutes the attempted shortcut from a
singular Gram matrix to collinearity. The corrected statement counts
rank-one degenerate three-spaces and does not claim those triples are
collinear.

## Excluded live work

Two bounded solver sweeps remained nonterminal at the publication cutoff.
Their partial logs and output targets are ignored and absent from the
checkpoint. The separate simultaneous block-completion lane supplied no
publication-ready theorem or artifact before the cutoff. No mathematical
inference is made from elapsed solver time or the absence of a result.

## Final classification

```text
Wave 37 integration metadata:       VERIFIED scoped
six mathematical/artifact suites:   42/42 PASS
publication evidence and links:     PASS
privacy and whitespace gates:       PASS
endpoint exclusion:                 NOT OBTAINED
improved general upper bound:       NOT OBTAINED
Conway-99 and novelty:              UNKNOWN
```
