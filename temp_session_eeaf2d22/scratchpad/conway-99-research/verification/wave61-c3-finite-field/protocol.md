# Wave 61 independent verification protocol

## Frozen scope

This verifier audits the conditional `kappa=3` lane at the prism-free
`n3=4158` endpoint.  It accepts as input the 18 frozen fibre-preserving
component types in the Wave 60 component census and reconstructs all
`C(20,3)=1140` unordered triples with repetition.

Before any Wave 61 discovery source, test, result, protocol, or report was
opened, `preinspection-freeze.sha256` recorded every visible byte in the Wave
61 package and the complete Wave 58 and Wave 60 input packages.

The verifier:

1. validates every component edge list directly, including cubicity,
   connectedness, triangle-freeness, fixed-fibre perfect matchings, cross-fibre
   perfect matchings, codegree caps, four-cycle counts, and pairwise
   inequivalence under `S4 x S4 x S4` with fibres fixed;
2. reconstructs every 36-by-36 integral Gram target from the edge lists;
3. uses an independent least-significant-pivot `F2` elimination to check the
   six partition indicators, Gram ranks, quadratic radicals, the 198-bit
   local-pair spans, the 630-bit full-pair spans, and the 21-pattern moment
   system;
4. uses a leading-corner symmetric congruence elimination over
   `F3,F5,F7,F11` to check rank, discriminant square class, and anisotropic
   dimension;
5. checks the cubic pair-margin identity and explicitly separates it from the
   untested existence of a nonnegative integral third-order tensor;
6. performs hostile one-bit RHS mutations and malformed-component tests;
7. compares discovery summaries only after completing the independent
   reconstruction.

## Independence and symmetry boundary

No Wave 60 or Wave 61 implementation is imported.  Coordinate permutations
inside the three fixed four-point fibres are used only to validate that the
18 supplied records represent distinct fibre-preserving types.  They are not
assumed to extend to automorphisms of a candidate endpoint graph.  Components,
fibres, rows, and columns are never identified by an assumed graph
automorphism.

## Status wall

The numerical relaxations may be promoted only after an exact replay.  Their
success cannot promote an incidence design or graph:

- a finite-field Gram factor is not a 60-column binary design;
- parity span membership forgets nonnegative integer multiplicity and
  distinct-column constraints;
- the cubic margin identity does not establish existence of its tensor;
- no compatible `A_Y`, endpoint graph, endpoint exclusion, or improved
  general `n3` upper bound is claimed.

The endpoint and Conway-99 status remain `UNKNOWN`.

## Resource guard

The verifier refuses to start below 20% free physical memory and repeats the
check every 32 triples, stricter than the requested 15% free-memory floor.
