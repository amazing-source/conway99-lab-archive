# Wave 57 clean-room verification protocol

Frozen at `2026-07-27T20:54:00Z`, before inspection of
`attempts/wave57-star-complement/`.

## Scope

Assume a hypothetical prism-free `srg(99,14,1,2)` and fix an arbitrary graph
triangle `T`.  No automorphism of the graph, of `T`, or of any derived
partition is assumed.  Independently check the Wave 57 star-complement claims:

1. derive the equitable `T/X/Y` quotient from the SRG axioms;
2. construct the two supported `3`-eigenvectors and two supported
   `-4`-eigenvectors on `T union X`;
3. derive, rather than import, the spectral-projector block formulas and all
   rank/nullity consequences for `A_Y`;
4. check `|Y|`, the degree and triangle count of `G[Y]`, its first four
   spectral moments, and the `C4(X)`/`C4(Y)` ledger;
5. enumerate every claimed integer multiplicity pair and every claimed
   `C4(X)` interval using exact rational arithmetic;
6. reproduce all compact-interval moment-localizer bounds and attack every
   equality versus lower-bound statement;
7. check the algebraic-integer scalar controls by exact polynomial arithmetic;
8. check exact star-set/star-complement intersection and order statements,
   including whether the proposed target is actually contained inside `Y`;
9. calibrate hostile mutations for formulas, counts, ranges, and status
   inflation.

## Independence rules

- The verifier implementation must not import discovery code.
- Discovery artifacts are read only after this protocol and the upstream
  hashes are frozen.
- Floating-point eigenvalues may be diagnostic only.  Promoted claims require
  integer, rational, or symbolic certificates reproduced independently.
- Interlacing gives inequalities unless equality is separately proved.
- A lower bound on an eigenvalue multiplicity is not silently upgraded to an
  equality.
- A feasible moment spectrum is not a graph, a star complement, or an endpoint
  construction.
- A failed bounded search is not a nonexistence certificate.
- The prism-free endpoint and Conway-99 remain `UNKNOWN` unless a complete
  independently checked proof or construction is supplied.

## Resource guard

The checker refuses to start below 20 percent free physical memory on Windows,
which is stricter than the user's 15 percent floor.  All enumerations in scope
are small exact loops; no large solver or dense numerical allocation is
authorized.

## Promotion rule

The package status is:

- `VERIFIED` only if every material scoped claim is exactly reproduced;
- `REFUTED_IN_PART` if the core lane survives but at least one material claim
  is false or overstates the derivation;
- `UNKNOWN` if the evidence cannot settle the scoped claims.

Discovery remains unable to verify itself.
