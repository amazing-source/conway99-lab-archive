# Wave 19 n=3, v=60 structural audit: preinspection freeze

```yaml
role: verifier
date_utc: 2026-07-23T13:14:19Z
git_commit: "13b2a90 (supplied target prefix; no Git command will be run)"
claim_label: UNKNOWN
scope: "Independent adversarial audit of the Wave 19 n=3, v=60 structural candidate and its two stated finite residual regimes"
inputs: "None opened from Wave 19 before this freeze"
method: "Freeze independent derivations, pass/fail conditions, hostile mutations, and publication boundary before inspecting the candidate"
command: "Not applicable"
outputs: "verification/n3-60-structural/preinspection-freeze.md (hash recorded immediately after creation)"
limitations: "The task forbids Git commands; commit identity is the supplied prefix rather than an independently resolved full hash."
```

## Contamination boundary

This file is written before opening any file under
`attempts/wave19-n3-60-structural/` or the candidate
`agents/2026-07-23-wave19-n3-60-structural.md`.  The verifier may subsequently
authenticate premises from the already-audited Wave 15 and Wave 16 framework,
but will not read, execute, cite, or import Wave 17 or Wave 18 material.

## Independently frozen derivations

1. Re-derive the complete nonnegative-integer profile system for total
   `sum(q)=40` directly from the incidence/moment identities authenticated from
   Wave 15/16.  Enumerate it with a newly written checker whose control flow and
   data representation do not copy the candidate.
2. Reconstruct endpoint crossing semantics from definitions: identify what is
   counted at each endpoint, prove the local-to-global equality, and test it on
   hand-built tiny objects, loops/multiple-edge impostors, and deliberately
   inconsistent endpoint labels.
3. Reproduce every exclusion through `r=19`; then separately reproduce the
   `r=20, m=28` and `r=20, m=29` exclusions.  Each exclusion passes only if all
   integer cases are covered without an unstated symmetry, connectivity,
   simplicity, or realizability assumption.
4. Residual A (`m=27`): independently enumerate point profiles, derive the
   associated cubic-graph conditions, classify all relevant cubic graph
   possibilities (or verify a complete external classification), re-derive the
   outside first/second moments, and explicitly enumerate/check every
   compatibility condition joining local profiles, graph incidences, and
   outside data.
5. Residual B (`m=30`): define `F`, `R`, and `Z` from primitives rather than
   names; derive the asserted `e(Z) <= 3` consequence from the moment equations;
   exhaust all topologies allowed by that bound, including disconnected,
   isolated-vertex, triangle, path, matching, and repeated-neighborhood edge
   cases; and independently enumerate the claimed outside histograms.
6. For every finite enumeration, compare two formulations when feasible:
   direct nested integer enumeration versus equation filtering or a small
   independent constraint/backtracking implementation.  Counts alone do not
   pass; canonical machine-readable witnesses or no-case certificates and
   per-equation checks are required.

## Pass/fail conditions

- **PASS for an identity:** it follows line by line from authenticated
  definitions/premises, uses no Wave 17/18 premise, and is confirmed on
  independently generated admissible toy data where such data exist.
- **PASS for a finite list:** the domain bounds are proved, the enumeration is
  complete over those bounds, every output is checked against the original
  equations, and an independently structured enumeration yields the same
  canonical set.
- **PASS for an exclusion:** every case in the stated scope is rejected by a
  necessary condition whose hypotheses are checked in that case.  A solver
  status, empty restricted search, or failure to construct is not enough.
- **PASS for a residual description:** all variables have primitive semantics;
  mappings in both directions are checked; topology coverage includes all
  degenerate/disconnected cases; and no local object is combined with an
  incompatible global histogram.
- **FAIL / blocking objection:** any missing domain case, arithmetic mismatch,
  hidden automorphism or simplicity assumption, use of Wave 17/18, mismatch
  between endpoint and global counts, incomplete cubic/topology coverage,
  moment list mismatch, or compatibility condition asserted but not enforced.
- **INCONCLUSIVE:** evidence may support a necessary reduction while lacking a
  complete checked bridge or certificate.  Such evidence cannot be promoted.

## Hostile mutations fixed in advance

The checker/test harness will inject, where type-correct:

1. one-unit changes to each profile count while preserving the easiest linear
   total, to ensure the remaining moment equations reject near misses;
2. endpoint swaps, an endpoint counted twice, an omitted endpoint, and a
   crossing/noncrossing label flip;
3. loop and parallel-edge impostors in graph encodings, plus disconnected
   cubic-looking degree sequences;
4. a degree-preserving 2-switch on cubic candidates to detect classification
   by degree sequence alone;
5. outside histograms with the correct population but wrong first moment, the
   correct first moment but wrong second moment, and moment-colliding
   histograms where available;
6. `Z` topologies at and just beyond the claimed edge bound: empty, one edge,
   adjacent/disjoint two edges, three-edge matching/path/star/triangle, and
   four-edge counterpressure examples;
7. relabelings/canonicalization collisions and a deliberately imposed
   automorphism restriction, which must change or be proved not to change the
   search space;
8. locally valid but globally incompatible pairings of point profiles, cubic
   graph data, and outside histograms.

Each mutation passes the harness only if it is either rejected for the precise
violated invariant or retained when it is genuinely within scope.  A mutation
test that merely crashes is a failure.

## Exact status boundary

The target statement is not declared solved by this audit unless both residual
regimes are eliminated or completely resolved by independently checkable
certificates.  Reproducing all advertised reductions while either `m=27`
Residual A or `m=30` Residual B remains does **not** improve the public status
beyond:

`UNKNOWN_FINITE_RESIDUAL`.

The verifier does not promote its own discovery to `VERIFIED`.  At most this
audit can independently support that boundary, mark particular reductions
`DERIVED`, or issue a `REFUTED`/blocking finding against an advertised step.
