# Wave 31 orchestrator correction and publication ledger

Date: 2026-07-24

## Scope

This ledger records the immutable Wave 31 chronology, verifier corrections,
discarded harness failures, finite-search boundaries, and publication wall.
It does not certify a discovery by orchestrator authority.

## Frozen revisions

| Revision | Commit | Role |
|---|---|---|
| sign-commutant discovery | `a8b0c34040f6857b3c5ebcc44f108e03a4159088` | conditional proof candidate |
| statement and literature audit | `31bc516a581decb6394bf5e780f07fb05d567274` | bounded source/status audit |
| T20 finite construction search | `67a0e4585c9c378dcd658784a3876564557b70e3` | exact finite evidence |
| sign-commutant verification | `2a3705dac7de871d23855a12e0d0ddb7aa36d862` | primary and skeptical audits |
| T20 finite-evidence verification | `682de9a0b3cba43266911736fb0bf275a15741d8` | independent exact audit |

Only the orchestrator performed Git writes. Discovery agents did not promote
their own claims.

## Sign-commutant theorem

The published scoped implication is:

```text
actual target vertex-triangle incidence/projector package
+ rootless even integral rank-44 endpoint S-form
+ nontrivial integral orthogonal decomposition of S

==> contradiction.
```

For a coordinate block of `b` triangles, its diagonal sign matrix commutes
with the zero-eigenspace projector. Transport through the vertex-triangle
incidence matrix gives a symmetric graph operator commuting with the exact
`-4` spectral projector. The full commutator expansion and adjacent-edge
cancellation force the signed triangle incidence vector to be constant.
Double counting gives `33 | b`.

The submitted route also uses the lattice-block tight-frame trace
`4b=21r` and checks every proper rank. The independent verifier found a
shorter strengthening: the coordinate block of the projector is itself a
projector, so its trace gives `21 | b`. Hence `231 | b`, impossible for a
nonempty proper block.

The primary verifier returned `PASS_SCOPED` after 21 independent tests and a
15-test submitted replay. A separate skeptical checker returned
`PASS_NO_FATAL_GAP`. The theorem excludes every nontrivial rootless integral
orthogonal decomposition under the actual target incidence semantics,
including the Wave 30 `20+24` survivor. It is not restricted to one
determinant-729 construction; the determinant exponent does not enter the
commutator argument.

## Primary-verifier wording correction

During orchestrator QA, one verifier sentence attributed one-block row
support to both evenness and the norm floor. The logically sufficient
premise is `min(S)>=4`: two nonzero orthogonal integral components would
already contribute norm at least eight. Evenness is inherited but is not
needed for that step.

The verifier package was corrected before its publication commit. Its
hostile control with `S=diag(2,2)` shows loss of the norm floor and, in that
example, loss of even-integral minimum four together; it is not presented as
an evenness-only countermodel. The theorem and verdict did not change.

During central integration review, a draft exposition incorrectly said the
entire adjacent entry of `KA-AK` vanished. The frozen proof and verifiers
instead—and correctly—show

```text
(ZA-AZ)_xy=0,
(KA-AK)_xy=d_x-d_y,
3(d_x-d_y)=d_x-d_y.
```

The README and structure note were corrected before commit. No frozen proof
artifact, test, or verdict changed.

## Retained harness failures

Two early primary-verifier `unittest` invocations were run from the wrong
directory and discovered zero substantive tests. They are retained in
`verification/wave31-sign-commutant/failed-objections.md`. The frozen command
was then run from the candidate directory and passed all 15 submitted tests.
No zero-test run is counted as evidence.

An attempted host-side wrapper for the skeptical checker was rejected rather
than treated as evidence. The committed standard-library checker was run
directly and its deterministic output was independently hashed.

## Literature chronology

The literature package froze the matrix/Schur survivor before the
sign-commutant proof existed. Its historical statement that the
sign-involution constancy lemma was `UNKNOWN` is therefore preserved. A
post-freeze addendum records the later proof signature without retroactively
rewriting the search chronology.

The audit logged 80 query strings in 20 batches, made four direct
metadata/abstract open attempts, retained 14 metadata records, and retained
no raw source payload. No exact prior result was found in the searched
sources as of 2026-07-24. That is a bounded non-discovery, not a novelty,
priority, nonexistence, or global-openness certificate.

After the immutable audit snapshot, the orchestrator added five cited
records to `SOURCES.bib`: Niemeier's rank-24 classification,
Conway--Sloane on integral coordinates and s-integrability,
Bertucci--Bonifacio's 2026 Euclidean-lattice preprint, Stanić on strongly
regular signed graphs, and Kharaghani--Pender--Suda on signed strongly
regular graphs and association schemes. The snapshot's corresponding
`absent_at_report_time` fields remain historically correct and were not
rewritten.

## T20 finite construction boundary

The construction package verifies the complete norm-four shell of the
displayed `T20`, all 2,538 antipodal lines, all 3,219,453 distinct-line
pairs, the exact 210-equation second-moment formulation, a rational
box-relaxation witness, the cap-one-coordinate exclusion, and a complete
radius-one/two nonhit around the named 105-line support.

The independent implementation:

- enumerates the full shell in two exact bases;
- recomputes every pair and both GF(2) ranks;
- checks all 2,538 rational weights and all 210 moments;
- uses a collision-free base-257 encoding for the complete named
  radius-two domain;
- separately replays the submitted modulo-`2^64` fingerprint; and
- verifies the conditional `A4_U=M_U` trace transfer.

The discovery suite passes 10 tests and the independent suite passes 11.
The verdict is `PASS_SCOPED_FINITE_EVIDENCE`. It neither finds nor excludes
an unrestricted Boolean frame. Solver timeouts and no-incumbent telemetry
remain noncertifying.

The construction run report embeds its parent
`31bc516a581decb6394bf5e780f07fb05d567274` because it was generated before
the construction commit. The independent verifier freezes the controlling
submitted object at `67a0e4585c9c378dcd658784a3876564557b70e3`; no candidate
byte was repaired or reinterpreted.

The proof, primary-verifier, T20-discovery, and T20-verifier stored JSON
files include dynamic OS and Python runtime fields. Literal byte identity is
therefore asserted for the pinned/current replay environment, not for every
operating system or Python build. Mathematical field agreement remains the
cross-platform requirement. The skeptical result has no runtime block.

Once the sign-commutant theorem is applied, no `T20 orthogonal_sum U24`
rootless decomposable actual endpoint can exist regardless of the finite
frame search. The shell, rational, parity, local-neighbourhood, and
conditional trace facts remain valid finite evidence; they are not promoted
to a global frame result.

## Publication wall

```text
rootless integrally decomposable actual-incidence endpoint: VERIFIED impossible
Wave 30 20+24 survivor under those premises:                VERIFIED impossible
displayed T20 finite shell and named radius-two domain:      VERIFIED
unrestricted T20 Boolean/oriented frame:                    UNKNOWN
rooted endpoint forms:                                      UNKNOWN
rootless integrally indecomposable endpoint forms:          UNKNOWN
n3=708:                                                     UNKNOWN
Conway-99 existence or nonexistence:                        UNKNOWN
novelty or priority:                                        UNKNOWN
```

The strongest conditional global bound remains `n3>=708`. Wave 31 changes a
structural endpoint boundary, not the Conway-99 resolution status.
