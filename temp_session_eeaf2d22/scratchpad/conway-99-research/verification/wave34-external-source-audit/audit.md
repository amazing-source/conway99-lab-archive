# Wave 34 consolidated external-source audit

Date: 2026-07-24

Verdict: **PASS WITH SCOPED IMPORTS AND EXPLICIT NON-IMPORTS**

```text
current maintained target marker:             CITED
current design-scale/corpus scope:             CITED
Kuber pinned conditional Lean theorem:         VERIFIED scoped
Kuber graph-to-matrix bridge:                  NOT FORMALIZED
Harrison arbitrary-root honest model:          VERIFIED
Harrison formula recipe identities:            VERIFIED formula-only
Harrison theorem-ladder UNSAT results:          UNKNOWN
Selub historical SAT framework:                CITED
Selub printed quadrilateral equivalence:        NOT VERIFIED AS PRINTED
external graph-level result imported:           NONE
Conway-99 / n3=708 / novelty / priority:        UNKNOWN
```

## Separation and evidence

The audit was frozen by
`verification/wave34-external-source-audit-protocol.md`. Discovery reports
identified claims and sources; verifier lanes then inspected direct sources,
pinned repositories, exact formulas, retained artifacts, and reproducible
build boundaries. No discovery agent promoted its own result.

The three component packages are bound by these manifest hashes:

| component | manifest SHA-256 |
|---|---|
| status and design sources | `1af4bad56405fb24128285fa586e2d1e2b80c82f1bdffdafa7cbdb6053cd6812` |
| Harrison rooted repository | `6052d3114a89af378cf412cc3126b60bab9dc9fe249a673188d3369a681db386` |
| Kuber and Selub | `5053217d6432365b903b787cb53e923996e96feef404904caad89dd7ebd686bc` |

The component reports retain input freezes, commands, environment records,
machine-readable results, corrections, missing-artifact ledgers, and scoped
limitations. Third-party source payloads and local temporary paths are not
published.

## Current status and design sources

Brouwer's maintained parameter table marks `(99,14,1,2)` with `?`; the
audited table key says that this denotes no known example in that source.
This is maintained-source status, not a proof of openness.

McKay's slides give an approximate scale of about `1.5 x 10^21`
`2-(15,3,2)` designs. The surrounding deck supplies the nonisomorphic-design
context, but the numerical line itself says only `designs`, and the deck
supplies no exact enumeration certificate.

The live University of Rijeka indexes contained 146 Folder 1 parent matrices
and 590 Folder 2 derived matrices. The stated order-six automorphism
restriction applies to the Folder 1 parents. The sources do not establish
that every derived design inherits that automorphism or that Folder 2 is an
unrestricted complete catalogue.

## Kuber conditional Lean formalization

At commit `be7b0ae3394721a4c3a1375008a1dbfca44981fc`, the project passed a
clean detached Lean 4.27.0 `lake --wfail build` after all 7,869 requested
cache files were unpacked. The build completed 3,068 jobs. All seven printed
axiom sets in the audited `Conway99C3Orbits/Basic.lean` file were exactly
`[propext, Classical.choice, Quot.sound]`.

The checked endpoint is conditional matrix/arithmetic. It accepts supplied
matrix, orbit-set, diagonal, spectral, and congruence information; it does
not construct those objects from a graph. No graph-to-matrix bridge,
SimpleGraph model, or graph-level `6`-or-`27` theorem is formalized. The
build is imported only at that exact boundary.

## Harrison rooted repository

At commit `26b36c540611fa02c95a5a4bd78cd4a582257195`, the arbitrary-root
bridge to the honest rooted counting model is valid, and the tracked honest
builder does not import the earlier retracted forced-edge routine. The
verifier reconstructed the S7 orbit coverage, leaf-stripping layer, exact
Gram base identities, and all 1,302 recorded CNF recipe hashes.

Those formula identities are not UNSAT certificates. The pinned tree lacks
the 830 theorem-ladder CNF/proof bodies for `k>=14`, the 14 claimed rational
Gram certificates and checker, and the six non-Gram proof bodies. The R230
bodies are unpulled LFS pointers, and `k=13` includes a disclosed
cloud-verdict-only gap. Therefore the R230, `k>=14`, `k=13`, and resulting
graph exclusions all remain `UNKNOWN`.

The verifier's first machine result serialized wall-clock time. That
reproducibility-only failure is retained; the repaired result omits timing
and local paths and was reproduced byte-identically.

## Selub SAT framework

Selub's seven-page 2023 University of Chicago REU paper is verified as an
earlier direct SAT-framework proposal. It reports no completed solver run,
SAT/UNSAT result, instance hash, model, proof trace, or machine certificate.

The printed quadrilateral conversion visibly omits a target-pair restriction
in its existence disjunction. The audit therefore labels equisatisfiability
`NOT VERIFIED AS PRINTED`; it does not claim a complete counterassignment to
all other printed clauses. The rooted section also switches inconsistently
from `v1` to `N(v0)`.

## Publication wall

No external graph-level theorem is imported. No missing proof body, solver
verdict, log line, LFS pointer, conditional formal theorem, bounded source
search, approximate design count, or restricted design corpus changes an
unrestricted Wave 34 branch.

Conway-99 existence and nonexistence, `n3=708`, novelty, and priority remain
`UNKNOWN`.
