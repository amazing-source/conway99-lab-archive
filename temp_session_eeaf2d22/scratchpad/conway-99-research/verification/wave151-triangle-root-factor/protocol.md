# Wave151 clean-room verification protocol

## Frozen discovery seal

The discovery package manifest was hashed before any artifact was inspected:

`attempts/wave151-triangle-root-factor/package-manifest.sha256`
SHA-256 `0e9ea04bad3fb41fda4224684663d828d3d19baea02387303775dd599d34d490`.

Every package artifact was then hashed without opening it. The complete
pre-inspection hash list is recorded in `input-freeze.sha256`.

## Separation boundary

No discovery Python file will be imported or executed. The verifier will use
a separate standard-library implementation to reconstruct the stored
24-by-60 binary factor, check row and column semantics, and reproduce the
relevant Gram blocks exactly.

## Solver evidence boundary

A solver `UNSAT` status is only a diagnostic unless accompanied by a
checkable proof artifact that is independently replayed. Stored residuals are
validated only for their explicitly frozen fixed-\(Q_1,Q_2\) scope.

## Claim boundary

Even a verified 24-by-60 factor covers only two of the three 12-row fibres.
The full 36-by-60 incidence matrix \(C\), a compatible residual adjacency
matrix \(D\), graph realization, Conway-99, and every strict bound remain
`UNKNOWN` unless separately certified.

## Resource boundary

Only small exact binary matrices are used. Initial host free memory was
31.85%, above the required 15% reserve.
