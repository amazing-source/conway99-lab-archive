# Wave 31 T20 verifier objection ledger

This ledger records hostile checks and why they did or did not veto the
submission.  Failed objections are retained to prevent later repetition.

## V31-T20-O01: shell enumeration could be incomplete

**Attack.**  A single reverse-LDL implementation might contain an interval
rounding error or prune a valid norm-four vector.

**Check.**  The verifier implemented its own exact rational LDL recursion,
proved the interval bound from

```text
(q*x+p)^2 * denominator <= numerator*q^2,
```

and repeated the full enumeration after a nontrivial coordinate permutation.
The changed-basis shell mapped back exactly to the original shell.

**Outcome.**  Objection failed.  Both trees contain the zero vector and 5,076
norm-four vectors, with no vectors of norms one, two, or three.

## V31-T20-O02: cardinality could hide a wrong canonical line list

**Attack.**  The correct count could coexist with a missing line and an extra
line.

**Check.**  The verifier compared the complete sorted tuple list with all
2,538 submitted lines and recomputed the canonical JSON hash.

**Outcome.**  Objection failed.  The complete lists agree and hash to
`25af9df21492a5b9022c1888424f4892e0e1cb56d82adee73b49197a536f569e`.

## V31-T20-O03: canonical orientation might be an automorphism restriction

**Attack.**  Selecting only the first-nonzero-positive vectors could remove
possible row signs or quotient by an assumed graph symmetry.

**Check.**  Every nonzero norm-four vector occurs with its negative.  The
canonical rule retains exactly one representative of each antipodal pair.
The later sign variable restores either orientation.  No orbit or target
automorphism is used.

**Outcome.**  Objection failed.

## V31-T20-O04: pair geometry could omit high inner products

**Attack.**  A partial graph build or residue shortcut could miss
absolute-three or absolute-four pairs.

**Check.**  The verifier computed all 3,219,453 unordered products directly
from `v^T T20 w`, accumulated all signed values, and recomputed every
absolute-two degree.

**Outcome.**  Objection failed.  Only `0,+/-1,+/-2` occur and the handshake
identity holds.

## V31-T20-O05: GF(2) rank could confuse coefficient and augmented pivots

**Attack.**  Treating the augmented bit as an ordinary variable can report a
rank without separately proving consistency.

**Check.**  The verifier row-reduced the 211 coefficient rows and the 211
augmented rows separately.

**Outcome.**  Objection failed.  Both ranks are 210, so the system is
consistent with one row dependency.  This remains only a relaxation.

## V31-T20-O06: rational weights might depend on solver floats

**Attack.**  A rounded LP solution could appear feasible while missing exact
moments or leaving the box.

**Check.**  The verifier ignored solver output, parsed all 210 fractional
strings as exact `Fraction` values, instantiated all 2,538 weights, checked
every bound and the sum, and reconstructed all 210 moments.

**Outcome.**  Objection failed.  The exact certificate passes.  It is not a
Boolean frame.

## V31-T20-O07: a modulo-2^64 collision could hide a repair

**Attack.**  Hash collisions, signed integer normalization, or overflow
semantics could cause a false negative.

**Check.**  Reduction modulo `2^64` is linear for signed integers.  Exact
feature equality necessarily yields the same residue.  The submitted scan
stores every required removal key, queries every addition choice, and checks
the complete feature vectors for all matching keys.  The verifier reproduced
the SplitMix64 coefficient hash and the zero-candidate counts.

The verifier also ran a separate exhaustive lookup using
`sum_e a_e*257^e`.  On this domain every comparison difference coordinate has
absolute value at most 102, so equality of base-257 codes is injective by
successive reduction modulo 257.

**Outcome.**  Objection failed.  Neither scan finds a radius-one or radius-two
repair.

## V31-T20-O08: the exchange scan might not cover the stated domain

**Attack.**  A loop could omit some selected removal or unselected addition.

**Check.**  The selected set has 105 distinct indices and its complement has
2,433 indices.  The verifier builds all 105 single-removal requirements and
all `105 choose 2 = 5,460` pair-removal requirements, then visits all 2,433
single additions and all `2,433 choose 2 = 2,958,528` addition pairs.

**Outcome.**  Objection failed for the named radius-two domain.  Supports at
distance three or greater and other starting supports remain unsearched.

## V31-T20-O09: the cap-one argument could exclude the full domain

**Attack.**  The diagonal bound might be phrased as a global obstruction.

**Check.**  It applies only when all 105 selected lines have maximum absolute
coordinate at most one.  The verifier counts 1,196 such lines and records
1,342 remaining lines outside the restriction.

**Outcome.**  Objection failed.  The candidate consistently labels only the
restricted domain excluded.

## V31-T20-O10: A4_U=M_U could be an invalid matrix cancellation

**Attack.**  Replacing `Q_U` by `U^-1` or regrouping the matrices could ignore
the definitions of `M_U`, `W_U`, and `Q_U`.

**Check.**  From the frozen definitions:

```text
M_U W_U M_U
=X_U U X_U^T W_U X_U U X_U^T
=X_U U Q_U U X_U^T.
```

Because `B_U=UQ_U=I`, `Q_U=U^-1`, yielding `M_U`.  No commutativity is used.

**Outcome.**  Objection failed under the explicitly frozen decomposable
endpoint premises.

## V31-T20-O11: the 84-unit transfer could lose trace

**Attack.**  Even if `A4_U=M_U`, the row split or global excess count might
not imply the stated T20 trace.

**Check.**  The frozen split is 105+126=231.  The U trace is `126*4=504`.
The frozen global trace is 1,260, leaving 756.  Also
`4*(105+84)=756`.

**Outcome.**  Objection failed.  This is necessary data, not an `A4_A`
construction.

## V31-T20-O12: `sum c=1044` might be copied rather than derived

**Attack.**  The aggregate row counts could be self-consistent but detached
from the frozen trace premise.

**Check.**  For a T20 row, the diagonal cube contributes 64 and the
off-diagonal cube sum is `-4-6c`, so its total is `60-6c`.  The frozen
`trace(B_A)=36` gives

```text
36 = 105*60 - 6*sum c,
sum c = 1044.
```

All aggregate counts then recompute algebraically.

**Outcome.**  Objection failed.

## V31-T20-O13: timeouts might be treated as nonexistence

**Attack.**  HiGHS, CP-SAT, SCIP, or oriented-model no-incumbent results could
be globalized.

**Check.**  The JSON says `ALL_NONCERTIFYING`, `NOT_PROVED`, and
`NOT_FOUND_OR_EXCLUDED`.  The report and failure ledger repeatedly state that
the unrestricted frame is unknown.  The independent checker uses no solver
telemetry as evidence and contains a hostile mutation that vetoes promotion
of the global frame status.

**Outcome.**  Objection failed.

## V31-T20-O14: embedded commit hash differs from submission commit

**Attack.**  The report and YAML embed
`31bc516a581decb6394bf5e780f07fb05d567274`, whereas the requested freeze is
`67a0e4585c9c378dcd658784a3876564557b70e3`.

**Check.**  The embedded hash is exactly the parent of the construction
commit.  The verifier freezes the final committed bytes, tree, parent, and all
blob hashes at the requested commit.

**Outcome.**  Provenance clarification, not a mathematical veto.  The final
submission commit is controlling.

## Retained limitations

```text
unrestricted Boolean second moment:            UNKNOWN
oriented zero-sum alphabet frame:              UNKNOWN
Q_A / B_A / A4_A:                              UNKNOWN
coupled T20 plus U24 endpoint:                  UNKNOWN
rooted or integrally indecomposable forms:      UNKNOWN
n3=708, Conway-99, and novelty:                 UNKNOWN
```
