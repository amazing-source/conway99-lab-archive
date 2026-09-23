# Wave 27 trace-verifier failures and cautions

## `B=SQ` is not Euclidean-symmetric

Treating `B` as symmetric merely because `S` and `Q` are symmetric would
be invalid.  The audit instead uses similarity to
`S^(1/2) Q S^(1/2)` for its positive real spectrum and the exact identity
`B^TQ=QB` for self-adjointness.  No commuting assumption is introduced.

## The discovery checker is not a proof of the lower bound by itself

The submitted `local_trace_floor_certificate()` checks the final scalar
inequalities but does not mechanically derive the pseudodeterminant,
integral splitting, or KKT reductions.  The verifier therefore audited
those arguments separately and encoded their exact scalar consequences in
an independent checker.

## Missing parity bridge in discovery prose

After excluding `tr(C^2)=2`, the discovery report jumps to
`tr(C^2)>=4`.  The necessary reason is the integral identity
`tr(C^2)=tr(C) (mod 2)`.  It is present in the frozen Wave 25 audit and is
spelled out in the verifier audit.  Discovery files were not silently
edited.

## No finite entry-box search was accepted as completeness evidence

An enumeration of small entries of `Q` would be only a restricted search.
The verifier does not use such an enumeration to establish the
unrestricted trace floor.

## First byte-replay wrapper used standard output

The first independent byte comparison captured standard output on Windows,
which translated line endings to CRLF and therefore did not match the
LF-only stored JSON.  That wrapper result was not accepted.  Replaying with
the checker's `--output` path, which explicitly writes LF, produced the
same SHA-256 hash as `independent-results.json`.

## Scope separation

The rank-44 block identities and matrix digests were cross-checked, but the
full root/no-orthogonal-`A2` certificate belongs to the separate
construction verifier.  Neither verifier supplies a 231-row projector,
Schur-square origin, graph, or endpoint exclusion.
