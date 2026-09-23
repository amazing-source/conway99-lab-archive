# Wave 58 clean-room verification protocol

Frozen at `2026-07-27T21:13:32Z`, before inspection of
`attempts/wave58-cross-incidence-rank/`.

## Conditional scope

Assume a hypothetical prism-free `srg(99,14,1,2)` and fix an arbitrary graph
triangle.  Use its cells `T`, `X=X0 union X1 union X2`, and `Y`, of orders
3, 36, and 60.  No automorphism of the completed graph or fixed triangle is
assumed.

Independently verify the Wave 58 cross-incidence lane:

1. reconstruct the `T/X/Y` cross-incidence Gram and transfer identities;
2. replay the prior Wave 36 rank, component, and multiplicity theorem with an
   explicit chronology guard;
3. independently prove `C4(X)<=27`;
4. enumerate the normalized `m=4` and `m=6` component cores without importing
   discovery code;
5. distinguish a coordinate-normalized labelled enumeration from an
   isomorphism classification or a completed-graph symmetry quotient;
6. reproduce all component-core counts and distributions and the claimed
   component-specific four-cycle sets for `kappa=2,3`;
7. replay the named canonical Wave 40 restricted-lift calculation while
   preserving its exact conditional scope;
8. check all three surviving `(a,b,kappa)` rows and every local or scalar
   control;
9. calibrate hostile mutations of formulas, counts, normalization metadata,
   completeness wording, and final status.

## Independence and promotion

- The verifier imports no Wave 58 discovery module.
- Discovery artifacts are read only after this protocol and all upstream
  chronology hashes are frozen.
- Coordinate relabelling used to normalize one fibre matching is not a graph
  automorphism assumption and is not evidence that generated cores are
  pairwise nonisomorphic.
- Exhaustion is promoted only for the exact labelled, normalized search space
  constructed by the verifier.
- A set of observed four-cycle values is not an interval unless every
  intermediate value is actually present.
- A canonical restricted lift is one conditional example, not coverage of all
  endpoint cores, lifts, or graphs.
- The verifier may return `VERIFIED`, `REFUTED_IN_PART`, or `UNKNOWN`; the run
  report uses the AGENTS.md claim-label vocabulary.
- No graph construction, endpoint exclusion, strict general upper bound, or
  Conway-99 resolution is inferred from a local control.

## Resource guard

The verifier refuses to start below 20 percent free physical memory on
Windows, stricter than the user's 15 percent floor.  The normalized component
enumerations are bounded exact loops and may not launch a large solver.
