# Wave 34 external-source audit: Kuber Lean and Selub SAT lanes

Date: 2026-07-24

Verdict: **PASS WITH SCOPED CORRECTIONS**

```text
Kuber repository pin and dependency pins:       VERIFIED
Kuber clean external build:                     VERIFIED
Kuber principal theorem axiom set:               VERIFIED standard Lean axioms
Kuber graph-to-matrix bridge:                    NOT FORMALIZED
Selub metadata and framework scope:              VERIFIED
Selub completed solver result or certificate:    NONE
Selub printed quadrilateral CNF equivalence:      NOT VERIFIED AS PRINTED
Conway-99 / n3=708 / novelty:                    UNKNOWN
```

## Frozen inputs

The eight repository inputs in `input-freeze.sha256` matched the bytes frozen
by the Wave 34 external-source protocol. The Kuber repository was checked at
commit `be7b0ae3394721a4c3a1375008a1dbfca44981fc`, tree
`f37a1b03a96dc4be0dfab7156ed4408e37bffdb6`. The GitHub commit record and
codeload archive independently matched that pin and the file hashes recorded
in `source-ledger.json`.

External source bytes were treated as untrusted inspection inputs. No source
archive, PDF, rendered page, dependency checkout, or build cache is retained
in this publication package.

## Kuber Lean project

The pinned project declares `leanprover/lean4:v4.27.0`. The audit used the
official Windows release archive:

```text
Lean:        4.27.0, commit db93fe1608548721853390a10cd40580fe7d22ae
Lake:        5.0.0-src+db93fe1
archive:     505,567,614 bytes
SHA-256:     c34b9c2820857185978fc7310c8badeda68c9c16e83edecf176a8003c5fda1b2
```

Every direct and transitive Lake dependency revision is recorded in
`dependency-ledger.json`. The final build used a fresh detached external Git
clone, not the earlier archive-populated experiment:

```powershell
git clone https://github.com/Kuberwastaken/conway99-c3-orbit-restriction.git <external-clone>
git -C <external-clone> checkout --detach be7b0ae3394721a4c3a1375008a1dbfca44981fc
<pinned-lake> exe cache get
<pinned-lake> --wfail build
```

The cache command downloaded and unpacked all 7,869 requested mathlib cache
files. The build completed successfully with 3,068 jobs and no warning
promoted by `--wfail`. Curated compact summaries of the observed command
outcomes are retained in `cache-get-summary.txt` and `lean-build.log`; they
are not complete raw stdout transcripts.

The seven `#print axioms` commands in
`Conway99C3Orbits/Basic.lean` all reported exactly:

```text
[propext, Classical.choice, Quot.sound]
```

These are standard Lean axioms. A scan of that audited Lean file found no
`sorry`, `admit`, custom axiom declaration, `unsafe`, `native_decide`,
`native_eval`, `implemented_by`, or `run_tac`.

### Exact theorem boundary

The principal theorem
`Conway99C3Orbits.triangularOrbitCount_eq_six_or_twentySeven` is a conditional
matrix/arithmetic theorem. It consumes:

1. an arbitrary rational `33 x 33` matrix;
2. a supplied finite set of orbit indices;
3. a diagonal-classification hypothesis;
4. a supplied spectral trace certificate; and
5. a supplied triangle-action congruence.

It proves that the supplied set has cardinality `6` or `27`. The repository
does not define a `SimpleGraph`, construct the quotient matrix from a graph,
formalize the order-three action, derive the spectral certificate, or prove
the triangle congruence from a Conway graph.

The packaged `C3QuotientCertificate` has seven fields. None is mechanically
derived from a graph in the repository. Its `quotientIdentity` and
`regularity` fields are not even consumed by the packaged endpoint; the
endpoint uses only `diagonal`, `spectrum`, and `triangle_congruence` together
with the supplied data. `lean-interface-map.json` records every field and its
exact use.

Therefore kernel acceptance verifies the encoded conditional theorem only.
It does not establish a graph-level `6`-or-`27` theorem, construct a graph,
or exclude one.

### Retained failed build route

The first archive-populated dependency experiment reproduced the pinned
source bytes but lacked the Git metadata Lake expected while reconciling
package URLs. That route failed closed. The final evidence comes from the
fresh detached Git clone above, whose cache and build commands both passed.

## Selub 2023 paper

The institutional PDF has:

```text
title:    Conway's 99-Graph Problem: A Boolean Satisfiability Approach
author:   Nathaniel Selub
context:  University of Chicago Mathematics REU 2023 participant paper
pages:    7
bytes:    289,879
SHA-256:  e533b92599e0f562e8ee63d5ca7e5ee5e2caaaa28de70fa6a73250cf333470f6
```

The paper proposes a direct Boolean edge encoding with 4,851 edge variables,
triangle/common-neighbor clauses, quadrilateral clauses, vertex-permutation
symmetry breaking, and rooted preprocessing. Its final section is explicitly
“Next Steps.” It reports no completed solver command, solver version,
SAT/UNSAT conclusion, model, proof trace, DIMACS hash, runtime, or machine
certificate.

Two printed-formula qualifications are material:

1. On pages 4–5, the displayed quadrilateral-existence disjunction ranges
   over every quadrilateral auxiliary variable without visibly tying the
   opposite pair `(a,b)` to the target nonedge `(i,j)`. As printed, a
   quadrilateral elsewhere can satisfy the clause. The claimed
   equisatisfiability of that displayed conversion is therefore
   **NOT VERIFIED AS PRINTED**. This audit records the visible indexing gap;
   it does not supply a complete Boolean counterassignment for every other
   printed clause.
2. On pages 6–7, the root is introduced as `v1` but the neighborhood switches
   to `N(v0)`. The intended root-plus-14-neighbors construction is inferable,
   but the notation is inconsistent and no preprocessing artifact is supplied.

`selub-scope.json` records the exact checked metadata, semantics, proposed
BibTeX record, and limitations.

## Strongest justified conclusion

Kuber's pinned Lean project cleanly builds and kernel-checks a useful
conditional arithmetic/matrix restriction with only standard Lean axioms.
The graph bridge remains explicit external hypothesis data. Selub supplies
historical SAT-framework prior art, not a solver result, and its displayed
quadrilateral conversion has an indexing gap.

Nothing in either source resolves an unrestricted Wave 34 branch, excludes
`n3=708`, constructs or excludes `srg(99,14,1,2)`, or establishes novelty.
