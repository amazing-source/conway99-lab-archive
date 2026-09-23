# Waves 46--49 integration audit

```yaml
role: orchestrator
date_utc: 2026-07-27T18:37:47Z
git_commit: e4394aa9172fa97a6dafa9158148c2183603a01b
claim_label: VERIFIED
scope: ordinary F7 code, three-root moments, local degree-two polynomial calculus, combined conic facial scout, and five-root moments
inputs:
  - path: attempts/wave46-f7-code/package-manifest.sha256
    sha256: 756622d5f40457d188c818a0233ee002b64039548bd51a725ec606b821c60272
  - path: verification/wave46-f7-code/package-manifest.sha256
    sha256: 3624ea9eca399889c048b3f333ae8df12fbac60176fd7bca0924fc06a18fdff0
  - path: attempts/wave47-three-root-moment/package-manifest.sha256
    sha256: 3fee6bf5ec42c5b70138f508ba3fbff6b44b56870601ea25111cd7da93473737
  - path: verification/wave47-three-root-moment/package-manifest.sha256
    sha256: cec96a7cbc967bbbdc95215bc2086d3056d94966c95d7ca1d60fa731f17f58eb
  - path: attempts/wave47-branch15-polynomial/package-manifest.sha256
    sha256: f7441d43fa3d1fee7b3dd5b1768a4dc7637fa1cd1ca58d8af811899d5edce9ee
  - path: verification/wave47-branch15-polynomial/package-manifest.sha256
    sha256: a31884041a5335b96c58d8664adca9c8744a0783d2447bc98f751735ea09391a
  - path: attempts/wave48-conic-moment/package-manifest.sha256
    sha256: 6d54b416cd0cf65ef361bc0eb9947ede79200bc23bb543c969f8fd7182d56460
  - path: verification/wave48-conic-moment/package-manifest.sha256
    sha256: c060526df8c04edab94155b6424fce19ea856c014062a924fba9335be6e6acd6
  - path: attempts/wave49-five-root-moment/package-manifest.sha256
    sha256: 5b7243a0c506263cbd080d1a6b3e3b33dd1e7805e37c15c90481147290b1edf5
  - path: verification/wave49-five-root-moment/package-manifest.sha256
    sha256: 6c00c49b9ce2816866ae62d26a8f04b0dc3dddd26cec7eb8d4308386d406ac97
method: discovery/verifier separation, exact replay, manifest checks, hostile controls, and scope audit
outputs:
  - verification/2026-07-27-wave49-integration-audit.md
limitations:
  - no complete endpoint feasible point or infeasibility certificate exists
  - floating solver statuses are non-evidentiary
  - no strict upper-bound improvement or Conway-99 resolution is claimed
```

## Verdict

**PASS_SCOPED** for the exact finite Wave 46 through Wave 49 claims listed
below. Wave 48's facial identities are independently verified; its numerical
scout remains `UNKNOWN` and is not promoted to endpoint feasibility or
infeasibility evidence.

## Separation

- Wave 46 discovery and verification use separate finite-field
  implementations. The verifier rebuilds all 17 generic rank controls.
- The Wave 47 three-root verifier independently regenerates the labelled
  class streams, coefficient tensors, controls, matrices, directions, and
  primitive cuts.
- The Wave 47 polynomial verifier froze its complete degree-two calculation
  before comparison and independently reconstructs every relation and hash.
- The Wave 48 verifier independently reconstructs the affine space and all
  eleven common kernels before opening the discovery face claims. It opens no
  numerical solver artifact.
- The Wave 49 verifier froze a full pre-comparison result before opening
  discovery artifacts. It independently reconstructs all labelled tensors,
  relabellings, controls, lower decks, witness matrices, and negative
  directions.
- No verifier uses numerical SDP output as mathematical evidence.

## Exact accepted finite results

### Wave 46 ordinary characteristic-seven code

Conditional on the prism-free endpoint projector identities, the row code is
self-orthogonal, lies in the all-one hyperplane, has dual distance at least
three, contains at least 1,386 weight-69 words, and has full third Schur
power. The resulting rank floor is only 11. Generic controls satisfying the
ordinary constraints exist in every dimension 28 through 44. This verifies a
null obstruction, not an endpoint code.

### Wave 47 three-root moments

The verifier reconstructs all eight root families, all 57,006 nonzero
upper-triangle coefficient entries, 48 root-order maps, six known-graph
controls, and all 136 stored-witness matrices. It verifies 2,664 strict exact
negative directions and 2,657 distinct primitive cuts. These reject 17
specific aggregate vectors only.

### Wave 47 degree-two polynomial calculus

Seven local windows reproduce new linear-rank increments
`[2,1,2,2,2,2,2]`, hence 13 exact XOR relations. There are zero
contradictions and zero newly forced unary assignments. The 34,340 active
Wave 43 cuts partition exactly as
`[4141,0,5959,6060,6060,6060,6060]` and remain degree four.

The discovery README describes the 48 local blocks imprecisely as 24
exact-one and 24 exact-two targets. Independent parsing finds unsimplified
right-hand side one for all 48. The computation reads the correct OPB rows,
so no result or hash changes; the verifier report preserves the correction.

### Wave 49 five-root moments

The clean-room verifier reconstructs 683 labelled roots, 21 canonical
families, all 2,520 `S5` coordinate relabellings, 680,400 class-tensor checks,
42 Petersen/Clebsch controls, and all 357 matrices on the 17 stored
witnesses. Every matrix has an independently found strict exact negative
integer direction, and every discovery direction replays exactly.

Root permutations are coordinate relabellings, not automorphisms of a
hypothetical target graph.

## Wave 48 and numerical boundary

Clean-room exact reduction verifies rank 93 and nullity 116 for the Wave 44
affine system, all 170 particular identities, all 19,720 homogeneous
nullspace identities, and complete universal kernels for all eleven Wave
45/47 moment families. The retained Clarabel and SCS candidates have small
negative probabilities or eigenvalues at inconsistent scales. No exact
feasible vector and no exact rational infeasibility witness was obtained. The
bounded margin-zero/log-det continuation timed out without an artifact.

Wave 49's combined SDP scout is likewise near the boundary and
`optimal_inaccurate`; its floating residuals, eigenvalues, and duals are
diagnostics only.

## Artifact checks

```text
Wave 46 verifier tests / manifest:         16 PASS / 15 entries
Wave 47 three-root tests / manifest:        6 PASS / 9 entries
Wave 47 polynomial tests / manifest:        7 PASS / 11 entries
Wave 48 discovery tests / manifest:         5 PASS / 13 entries
Wave 48 verifier tests / manifest:          5 PASS / 11 entries
Wave 49 discovery tests / manifest:         5 PASS / 14 entries
Wave 49 verifier tests / manifest:          8 PASS / 12 entries
minimum required free physical memory:     20 percent
user-requested free physical memory:       15 percent
```

## Promotion boundary

```text
ordinary F7 obstruction:                    NONE, VERIFIED SCOPED
three-root finite witness refutations:      VERIFIED SCOPED
degree-two branch-15 relations:             VERIFIED SCOPED
exact affine facial reduction:              VERIFIED SCOPED
five-root finite witness refutations:       VERIFIED SCOPED
complete PSD-constrained count region:      UNKNOWN
endpoint proof coverage:                    0/33
strict upper bound below 4158:              NOT PROVED
rigorous interval:                          708 <= n3 <= 4158
endpoint / graph / Conway-99:                UNKNOWN
novelty and priority:                       UNKNOWN
```
