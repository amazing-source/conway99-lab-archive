# Wave 34 external-source audit protocol freeze

Date frozen: 2026-07-24T19:59:00Z

Orchestrator checkpoint:
`1be9b6f61136763ce77d3927984979205e7fb23a`

Global status at freeze:

```text
Conway-99 existence/nonexistence: UNKNOWN
n3=708:                           UNKNOWN
external result imported:         NONE
```

## Frozen discovery inputs

| input | SHA-256 |
|---|---|
| `verification/wave34-continuation-protocol.md` | `60e6c3aba152e924a51bd2503e82de3d05bb39fada258da4a2796e344ae23cd4` |
| `agents/2026-07-24-wave34-current-literature.md` | `b470c62d657686779f22154872e19d7db002f1abde1bc173ae747f9e2ad86b95` |
| `attempts/wave34-current-literature/query-ledger.json` | `ece460c54282b45ce013083756bc421ea2427d91800b65e16f9049734225843d` |
| `attempts/wave34-current-literature/source-ledger.json` | `5fa6f75abcfc8d3033c9715f3977722e99fcb238ca1b74d2db255e759a58b100` |
| `attempts/wave34-current-literature/audit.md` | `1be6c6904314763031968c47dde8b4187caf1118ca4c2a1c9cf5f93d9496abc3` |
| `attempts/wave34-current-literature/run-report.yaml` | `fb60da266720ecdb00486948ae3d2e02b599b5c8e02c2308732e1b9e318aead3` |

The auditor did not author the discovery package. Any mismatch between this
table and disk is a fail-closed stop.

## Lane E1: Lean formalization

Pin:

```text
repository: https://github.com/Kuberwastaken/conway99-c3-orbit-restriction
commit:     be7b0ae3394721a4c3a1375008a1dbfca44981fc
```

In a clean temporary clone:

1. verify the fetched commit and every dependency/toolchain pin;
2. record OS, Lean, Lake, elan, and dependency versions;
3. run the documented cache and `lake --wfail build` commands;
4. search the principal theorem dependency closure for `sorry`, `admit`,
   custom axioms, unsafe declarations, and native-evaluation shortcuts;
5. print or otherwise check the axiom set of the principal theorem;
6. map every field of `C3QuotientCertificate` to either a mechanically
   derived graph fact or an explicit unbridged hypothesis; and
7. state the strongest theorem actually formalized without upgrading a
   conditional matrix theorem to a graph theorem.

A successful build verifies that the pinned formal project compiles under
the recorded environment. It does not supply any missing graph-to-matrix
bridge.

## Lane E2: rooted-fiber certificate repository

Pin:

```text
repository: https://github.com/harrisonpedrero/conway-99-graph
commit:     26b36c540611fa02c95a5a4bd78cd4a582257195
```

Audit in dependency order:

1. identify and restate the exact "honest rooted counting model";
2. check whether every assumption follows from an unrestricted
   `srg(99,14,1,2)` rooted at an arbitrary vertex;
3. preserve the repository's earlier retracted forced-edge claim and verify
   that no surviving result imports it;
4. inventory every rung, residual, certificate hash, proof format, checker,
   and retained or missing proof body supporting `k>=14`;
5. independently replay all small exact-rational Gram/Euclidean certificates
   with a verifier reconstructed from their stated identities where
   practical;
6. enumerate the six reported SAT/LRAT-only cores and distinguish a checked
   proof from an author log, missing body, Git LFS pointer, or cloud verdict;
7. treat `k=13` separately and retain the disclosed `res1` evidence gap; and
8. state whether the strongest fully retained, independently replayed result
   is narrower than the author's claim.

Do not download multi-gigabyte proof bodies merely to avoid an `UNKNOWN`
entry. Record exact size, availability, hash, and checker requirements; a
missing or unchecked proof remains unverified. A solver verdict, CI badge,
log line, or manifest entry is not an UNSAT certificate.

## Lane E3: Selub metadata and scope

Inspect the institutional PDF:

```text
https://math.uchicago.edu/~may/REU2023/REUPapers/Selub.pdf
```

Check title, author, institutional context, date, page count, exact
edge/triangle/quadrilateral semantics, symmetry restrictions, rooted
preprocessing, and whether any completed solver run or certificate is
reported. Produce a proposed bibliography entry only if those facts agree.

## Comparison and labels

The auditor may use:

- `VERIFIED` only for a precisely scoped statement it independently
  reconstructs or replays;
- `CITED` for a source's statement with an exact applicability boundary;
- `REFUTED` for a checkable contradiction to a stated claim;
- `UNKNOWN` when artifacts, assumptions, or coverage remain incomplete.

The auditor may veto import but may not silently repair an external claim.
Corrections and failed replays must be retained.

No result in this audit changes the status of the unrestricted Wave 34
tracks, `n3=708`, or Conway-99 without a separate exact bridge and the normal
independent-verification gates.

## Required outputs

The verifier should write only:

```text
agents/2026-07-24-wave34-external-source-verifier.md
verification/wave34-external-source-audit/**
```

The output package must include:

1. the AGENTS.md run-report schema;
2. an input-hash check;
3. exact commands and environment versions;
4. a theorem/assumption map for the Lean project;
5. a rung-by-rung artifact and replay ledger for the rooted repository;
6. Selub metadata and a proposed BibTeX record or a recorded mismatch;
7. failed commands and unavailable artifacts;
8. machine-readable results;
9. SHA-256 manifests; and
10. a scoped verdict that leaves every unsupported implication `UNKNOWN`.
