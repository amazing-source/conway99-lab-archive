# Independent re-audit: Wave 38 complete endpoint

Status: `VERIFIED_CONSTRUCTION_SCOPE_ONLY`; target status remains `UNKNOWN`.

## Verdict

The orchestrator hardening fixes all four findings from the first audit.
Candidate-bound catalog verification, source-bound pool verification, strict
schema and status checks, and pre-write OPB path containment each survived
independent hostile regression tests.

The discovery package's own `package-manifest.sha256` and construction
`run-report.yaml` were refreshed during the re-audit. The 16-entry manifest has
exact file coverage and every digest now matches; all eight run-report output
hashes also replay. The temporary evidence-integrity mismatch is therefore
closed as W38-CE-V5.

This package still does not decide the endpoint. No target OPB was generated,
no solver was run, no SAT witness or UNSAT proof exists, and no complete lazy
cut iteration was performed.

## W38-CE-V1: fixed

The original catalog validator rederived each listed clause but could not prove
that every prism in the named candidate was listed.

The hardened completeness path now requires candidate edges and reconstructs
the entire canonical catalog. Independent attacks confirmed that it:

- accepts the unmodified fixture catalog with its fixture candidate;
- refuses completeness verification when candidate edges are absent;
- rejects an omitted prism witness;
- rejects forged candidate digest, edge-count, and triangle-count metadata;
- rejects status, scope, and limitations inflation.

The public `prism_oracle.py --verify-only` command now requires `--candidate`
and reports `PASS_COMPLETE_CATALOG_BOUND_TO_CANDIDATE` only after this complete
comparison.

The lower-level unbound validator intentionally remains usable to check the
soundness of individually listed cuts. It will not establish catalog
completeness, and `require_complete=True` fails without candidate evidence.

## W38-CE-V2: fixed

The original pool validator rederived retained clauses but did not bind source
digests and counts back to source catalogs.

The hardened provenance path now requires all source catalogs, reconstructs
their deterministic merge, and compares the submitted pool to that canonical
result. Independent attacks confirmed that it:

- accepts the fixture pool with its exact source catalog bytes;
- refuses provenance verification when source catalogs are absent;
- rejects a forged source digest and source counts;
- rejects missing or altered pool status, scope, and limitations.

The public `cut_pool.py --verify-only` command now requires one `--catalog`
argument for every source and reports `PASS_SOURCE_BOUND_POOL` only after the
source-bound comparison.

As with catalogs, an unbound library call remains a deliberately weaker
individual-cut soundness check. It is not pool-provenance verification.

## W38-CE-V3: fixed

The hardened schemas use exact integer type checks. Boolean aliases such as
`false == 0` and `true == 1` are rejected in witness, variable-edge, literal,
and count fields. Canonical clause ordering, exact claim labels, exact scopes,
and frozen limitations are enforced.

The prior Boolean, label, scope, limitations, count, literal, variable-edge,
matching, and duplicate-clause attacks all failed.

## W38-CE-V4: fixed

Both branch and static exporters now resolve OPB and metadata outputs inside
the repository before formula construction or filesystem writes. They also
reject identical OPB and metadata destinations.

Black-box tests confirmed that:

- outside-repository branch outputs are rejected without creating files;
- outside-repository static outputs are rejected with the correct size
  acknowledgement and without creating files;
- colliding in-repository OPB and metadata paths are rejected before writes;
- a wrong static-size acknowledgement is rejected before writes.

The static route still accepts no cut pool and streams the complete clause
iterator. A partial-pool formula remains labelled
`CANDIDATE_FORMULA_ONLY` with strategy `lazy_exact_separation`.

## W38-CE-V5: fixed

During the re-audit, seven stale discovery-manifest rows and four stale
construction-report output hashes were detected after hardening. The
orchestrator regenerated both records.

The final independent replay confirms:

- all 16 discovery package-manifest paths exactly cover the package;
- all 16 package-manifest SHA-256 values match;
- all eight construction-report output SHA-256 values match;
- all six upstream input-freeze hashes match;
- strict JSON/YAML and privacy checks pass.

The hardened discovery package is now hash-bound.

## Mathematical and oracle regression

The previous clean-room mathematics was rerun unchanged:

```text
root triangles                          7
coordinate plus two residuals     14*C(12,2) = 924
residual-only triangles             C(84,3) = 95,284
total                                         96,215
```

For six residual vertices there are `C(6,3)/2 * 3! = 60` distinct labelled
prism patterns, giving exactly:

```text
60*C(84,6) = 24,388,892,640
```

residual-only clauses before branch simplification.

All 64 supergraphs of one nine-edge prism pattern were retested under the
adjacent-pair common-neighbor bound; only the prism itself survives. The
independent and discovery prism oracles again agreed on all 32,768 simple
six-vertex graphs and five hostile larger fixtures.

The normalized endpoint scope remains exactly 33 refined cases under parents
`4,5,8,10,12`, with no completed-graph automorphism assumption.

## Test summary and evidence boundary

- Discovery tests: 12 passed, 0 failed.
- Independent tests: 15 passed, 0 failed.
- Six-vertex graphs checked: 32,768.
- Labelled prism patterns checked: 60.
- Lambda supergraphs checked: 64.
- V1 through V5: `FIXED`.

No target formula, solver result, proof, or graph certificate was produced.
The endpoint `n3=4158`, any bound `n3<=4155`, Conway-99, and novelty remain
`UNKNOWN`.
