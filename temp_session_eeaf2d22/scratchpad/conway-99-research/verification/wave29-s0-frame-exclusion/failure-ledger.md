# Wave 29 independent-verifier failure and correction ledger

## Preserved corrections

1. **Preinspection commit metadata was stale.** The initial
   `protocol-freeze.md` carried `d76d030f...`, the previously supplied public
   Wave 27 head. After inspection, the Wave 29 discovery and all six frozen
   inputs identified `74b6f3adcee19ca2b0480258bb7bf51198bd085a` as the
   applicable local frozen base. The protocol file retains the original value
   and appends the correction; the audit and run report use the Wave 29 base.
   This metadata issue does not affect any byte hash or derivation.

2. **`C_K` PSD shortcut rejected.** An early proof-reading temptation was to
   treat `C_K` as positive semidefinite. That does not follow. The final proof
   uses only that `C_K` is integral and `G_K`-self-adjoint and that
   `B_K=I+2C_K` has positive spectrum. Therefore `mu(C_K)>-1/2`, and the
   negative interval is checked separately.

3. **Determinant quotient rounded only after integrality.** The real inequality
   is `det(Q)<=6525/729`, which is slightly less than nine. The integer bound
   is then `det(Q)<=8`; it is not a direct real-number simplification.

## Failed or non-evidentiary routes

- Re-running the Wave 28 15-million-node norm enumeration was rejected as
  unnecessary duplication. Its independently audited output and hash are
  frozen inputs to this implication audit.
- A numerical plot of the logarithmic inequality was rejected as a
  certificate. The final verifier uses exact rational bounds on `log(3)`,
  a formal derivative factorization, and a separate calculus proof on
  `(-1/2,0)`.
- Aggregate row-count parity was checked for a hidden contradiction. Every
  immediate double-count and cross-zero condition is consistent. This absence
  is not promoted to an existence claim for a row-pattern matrix.
- A small exact block-matrix calculation is retained only as a hostile
  implementation control. The general block splitting is proved symbolically;
  the small example is not extrapolated as finite-search evidence.

## Active premise deletions

- Without minimum four in both orthogonal blocks, a mixed `2+2` row can occur.
- Without the even-unimodular rank-12 veto, `det(B_K)=729` merely saturates the
  logarithmic cap.
- Without the multiple-of-six trace residue, `(tr(B_K),tr(B_L))=(28,32)` is
  AM-GM compatible and gives no contradiction.
- Without integrality of `C_K`, the characteristic pseudodeterminant may be
  below one; `(1/2)I_12` is an explicit control.

No mathematical defect was found in the scoped Wave 29 discovery.
