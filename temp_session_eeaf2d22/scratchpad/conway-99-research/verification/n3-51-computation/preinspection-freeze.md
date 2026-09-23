# Wave 16 `n3 = 51` computational audit: pre-inspection freeze

```yaml
role: verifier
date_utc: 2026-07-23T11:02:53Z
git_commit: NOT_QUERIED_VERIFIER_FORBIDDEN_FROM_GIT
claim_label: UNKNOWN
scope: independently audit the Wave 16 computational lane for the conditional n3 = 51 case
inputs:
  - assignment from the orchestrator; no discovery implementation or report inspected yet
method: freeze the audit contract and adversarial checks before reading discovery internals
command: N/A
outputs:
  - verification/n3-51-computation/preinspection-freeze.md
limitations:
  - the UTC timestamp was observed from the local shell before inspection
  - this freeze does not accept any profile count, formula, solver status, or candidate claim
```

## Claim boundary known before inspection

The assigned lane concerns a computational reduction under the already conditional
`n3 = 51` case.  The verifier must reconstruct rather than trust:

1. the integer/support-profile census and every inherited filter;
2. the translation of each residual profile into a Boolean formula;
3. the mapping from solver output to public status;
4. every claimed satisfying candidate and every deterministic artifact;
5. the test and hostile-mutation coverage.

This lane cannot by itself establish the existence or nonexistence of
`srg(99,14,1,2)`.  It also cannot promote any surrounding mathematical premise
that is not independently verified.

## Frozen acceptance criteria

- Reimplement the profile census and filters without importing discovery code.
- Derive the formula semantics from the mathematical constraints, then compare
  them with the emitted CNF at the clause level.
- Check that every emitted CNF header, variable map, clause count, and SHA-256
  digest matches its bytes and is deterministic under regeneration.
- Independently evaluate any candidate assignment against both the CNF and the
  higher-level constraints.
- Re-run submitted tests, add adversarial mutations, and ensure corrupted
  profiles, formulas, hashes, assignments, and summaries are rejected.
- Treat a satisfiable branch only as `SAT_CANDIDATE` unless it supplies the
  complete mathematical object required by the target statement.
- Treat an unsatisfiable solver response as `UNSAT_UNVERIFIED` unless an
  independently checked proof certificate is supplied.
- Preserve `TIMEOUT_UNKNOWN` and `BUDGET_UNKNOWN` as distinct unknown outcomes;
  neither is evidence of satisfiability or unsatisfiability.
- Record all failures and repairs.  A verifier may reject or qualify a claim but
  must not silently repair discovery artifacts.

## Frozen adversarial hypotheses

- Profile ordering or filtering may omit a branch.
- A high-level constraint may be encoded only in the checker, not the CNF.
- Cardinality constraints may contain an off-by-one error or auxiliary-variable
  collision.
- A solver status may be inferred from an exit code or stale output rather than
  proof/candidate bytes.
- Candidate literals may satisfy the CNF while violating the decoded graph
  semantics.
- Hash manifests may cover text-normalized rather than exact public bytes.
- Regeneration may be nondeterministic because of map/set iteration or timestamps.
- Mutation tests may mutate an unchecked field and still pass.

The verdict remains `UNKNOWN` until all inspected evidence has been attacked
under this contract.
