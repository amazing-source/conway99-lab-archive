# Retained boundary and non-closures

Claim label: `UNKNOWN` unless otherwise stated.

1. **Deficiency coupling alone does not close norm 16.** All five support
   orbits retain couplings; there are 4,985 coupling multisets across the
   canonical representatives.
2. **Per-`X2` singleton marginal flow does not prune.** Every coupling has
   a feasible local contingency table when `X2` is independent. These
   tables are checked one vertex at a time and are not a simultaneous
   outside graph.
3. **Outside type moments do not close.** They force `e(X2)` from the range
   `0..12` down to `{0,1}`, but retain 43 and 7 degree-histogram triples.
4. **Principal-minor spectra do not delete a support orbit.** They determine
   exact outside spectra and four-cycle counts, but all five pass trace and
   interlacing-compatible checks.
5. **Missing object.** The next boundary is a simultaneous 83-vertex simple
   graph satisfying all support-vs-outside marginals and all outside-pair
   `lambda/mu` equations. No nonhit for such a graph is recorded here.
6. **Corrected spectral exponent swap.** A transient derivation reversed the
   multiplicities of the two restricted eigenvalues. The correct full-graph
   multiplicities are `mult_A(3)=54` and `mult_A(-4)=44`, so the outside
   factor is `(x-3)^38(x+4)^28`. The reversed exponents give
   `trace(D)=-70` and are rejected by the exact checker.
