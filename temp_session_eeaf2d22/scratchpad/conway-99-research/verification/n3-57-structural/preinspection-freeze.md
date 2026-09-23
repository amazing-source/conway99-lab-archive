# Wave 18 `n3=57` structural audit: preinspection freeze

```yaml
role: verifier
date_utc: 2026-07-23T12:38:00Z
git_commit: NO_GIT
claim_label: UNKNOWN
scope: >
  Adversarial clean-room verification of the frozen Wave 18 conditional
  n3=57 structural discovery. This freeze precedes any inspection of
  agents/2026-07-23-wave18-n3-57-structural.md or
  attempts/wave18-n3-57-structural/*.
inputs:
  forbidden_until_freeze_complete:
    - agents/2026-07-23-wave18-n3-57-structural.md
    - attempts/wave18-n3-57-structural/*
method: >
  Independently reconstruct every stated premise from the earlier frozen
  framework or direct combinatorics; implement a materially independent exact
  checker; exhaust all enumerated branches; run hostile mutations designed to
  make each key premise fail; compare against the submitted report only after
  independent expected results and acceptance tests are fixed.
command: commands will be recorded verbatim after execution
outputs:
  - verification/n3-57-structural/preinspection-freeze.md
  - verification/n3-57-structural/independent_checker.py
  - verification/n3-57-structural/checker-results.json
  - verification/n3-57-structural/mutation-results.json
  - verification/2026-07-23-wave18-n3-57-structural-audit.md
limitations: >
  The assignment supplies the names of the branches and quantities to audit,
  but not their submitted derivations. Target existence and novelty remain
  UNKNOWN regardless of this conditional-lane result.
```

## Frozen clean-room reconstruction matrix

| Item | Independent reconstruction required before comparison | Pass condition |
|---|---|---|
| Conditional scope | Identify the exact assumptions implied by `n3=57` and distinguish them from any result at `n3=54` or other waves | Every used premise is derived locally or cited to an authenticated frozen input; no stronger statement is silently imported |
| `sum q=38` profiles | Derive the integer variables, lower/upper bounds, parity/congruence conditions, and total equation from first principles | Independent enumeration is complete, deterministic, and agrees with a separately coded brute-force/cartesian check |
| `d_K>=4` | Reconstruct the object `K`, its degree meaning, and why the lower bound follows | Bound follows from stated local axioms alone; mutation `d_K=3` must produce a rejected or explicitly exceptional branch |
| `|X|` incidence bound | Double-count incidences with all multiplicities and distinctness assumptions exposed | Both sides of the count are independently recomputed; equality conditions are recorded |
| Dense-subset threshold | Derive the extremal/averaging threshold and strict versus weak inequality | Exhaust small integer boundary values and verify off-by-one behavior |
| `r=18` equality cases | Enumerate every equality profile and independently test each stated contradiction | No case omitted; each contradiction has a local certificate and survives label permutations |
| `r=19`, `m=27/28` point sizes | Enumerate all allowed point-size multisets and all downstream branches | Exhaustive enumeration has independent count/checksum and no reliance on submitted case ordering |
| Endpoint-local crossing bounds | For point sizes 2, 3, 4, and 5, derive the exact maximum/minimum number of crossing incidences at each endpoint | Use explicit finite enumeration of endpoint neighborhoods plus a hand-checkable formula; mutations violating one endpoint constraint are detected |
| Actual-neighbor distinctness | Separate formal incidence slots from distinct graph neighbors | Checker stores neighbor identities, rejects collisions exactly when graph simplicity/local axioms require, and accepts legal coincidences only if proved legal |
| Degree-sum arithmetic | Recompute all sums and equality implications with exact integers | Symbolic identities and exhaustive branch values agree |
| Spectral arithmetic | Recompute characteristic/eigenvalue or Rayleigh/interlacing calculations exactly | Rational/integer arithmetic only; no floating-point threshold decides a branch |
| Import audit | Search the submitted report after clean-room work for Wave17 exclusion, global `H`-degree assumptions, Wave14 caps, or automorphisms | Every premise has local provenance; any unproved imported premise vetoes verification |

## Frozen checker architecture

The independent checker will be a standalone Python program written only
after the mathematical variables have been reconstructed. It will:

1. use `fractions.Fraction` and integer arithmetic only;
2. enumerate profiles by a direct recursive generator;
3. enumerate the same profiles a second way using a cartesian-product
   reference implementation;
4. canonicalize multisets before hashing so submitted labels/order cannot
   affect counts;
5. emit every surviving and rejected branch with a reason code;
6. separately model endpoint incidences and actual neighbor identities;
7. produce JSON suitable for independent replay;
8. contain no import from, parser for, or copied code from the submitted
   attempt directory.

## Frozen hostile-mutation suite

At least the following mutations will be run:

```text
M01  change sum(q)=38 to 37
M02  change sum(q)=38 to 39
M03  permit d_K=3
M04  relax the |X| incidence bound by one
M05  strengthen the |X| incidence bound by one
M06  replace a strict dense-subset threshold by a weak one
M07  replace a weak threshold by a strict one
M08  delete one r=18 equality profile
M09  duplicate one r=18 equality profile
M10  omit m=27
M11  omit m=28
M12  allow a point-size-2 endpoint one extra crossing
M13  allow a point-size-3 endpoint one extra crossing
M14  allow a point-size-4 endpoint one extra crossing
M15  allow a point-size-5 endpoint one extra crossing
M16  merge two actual neighbors that occupy distinct incidence slots
M17  split one actual neighbor into two identities
M18  perturb a degree sum by +1
M19  perturb a spectral numerator by +1
M20  evaluate the spectral inequality in floating point near its boundary
M21  inject a Wave17 n3=54 exclusion as an axiom
M22  inject a global H-degree assumption
M23  inject a Wave14 cap
M24  inject a nontrivial automorphism
```

Each mutation must either change an expected enumeration/checksum, create a
counterexample, or be rejected by a named invariant. A mutation with no
observable effect is a coverage gap until explained.

## Frozen decision rules

1. The submitted discovery cannot verify itself.
2. A solver exit code is not a certificate; all finite branches must be
   emitted or summarized by reproducible canonical hashes.
3. Restricted enumeration must list every restriction.
4. Equality arguments must record all equality conditions, not just the final
   numerical equality.
5. Formal incidence counts do not imply distinct actual neighbors.
6. Floating-point output cannot decide an exact spectral branch.
7. Any imported Wave17 exclusion, global `H`-degree, Wave14 cap, or
   automorphism assumption not rederived locally is fatal to `VERIFIED`.
8. Failed branches and hostile mutations are retained.
9. `n3=57` remains `DERIVED` or `UNKNOWN` unless every branch, arithmetic
   identity, and provenance check passes.
10. The global Conway-99 target and novelty remain `UNKNOWN` under every
    outcome of this audit.

## Inspection boundary

This file is the inspection boundary. The submitted report and attempt
directory may be opened only after this file has been written and hashed.
