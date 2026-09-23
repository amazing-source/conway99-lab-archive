# Statement and literature agent report — 2026-07-22

- Role: statement/literature agent
- Evidence scope: primary-source audit and independently reproduced elementary
  derivations
- Resolution verdict: `UNKNOWN`; no construction or nonexistence certificate
  found

## Status

The exact `srg(99,14,1,2)` existence problem remains open in the primary
literature checked through 2026-07-22. Cesarz--Woldar (2025) explicitly call
existence open. Petro--Phillips (2026) still discuss it among unknown strongly
regular-graph existence cases. The 2026 arXiv upload by Keramatipour is an MPhil
report dated 2023; its generic SAT/PB runs stalled and do not constitute a new
2026 resolution.

A literature search cannot prove that no result exists. Accordingly this is a
dated status audit, not a permanent mathematical claim.

## Reproduced equivalences

The agent supplied complete derivations, now integrated into
[CONJECTURE.md](../CONJECTURE.md), for:

- Conway's triangle/quadrilateral wording versus common-neighbor counts;
- the fact that those conditions force 14-regularity;
- the adjacency and Seidel matrix identities;
- the spectrum and global counts; and
- the root-normalized 84-vertex block formulation.

## Prior computations: exact scope

- Wilbrink's orbit analysis excludes order-11 automorphisms and hence vertex
  transitivity; it is not an unrestricted graph search.
- Behbahani--Lam restrict prime-order automorphisms; no universal proof
  certificate was located.
- Crnkovic--Maksimovic rule out specified composite group actions; asymmetric,
  `C2`, and `C3` cases remain outside those exclusions.
- Graeme Taylor's public notebooks explore local configurations. No compatible
  source license, full construction, or universal impossibility certificate
  was found.
- Keramatipour's direct encodings timed out/stalled. A timeout is not evidence
  of nonexistence.

No checked source supplied a universal CNF/ILP enumeration with an LRAT/DRAT
or equivalent independently replayable nonexistence certificate.

## Licensing notes

- Cesarz--Woldar is CC BY 4.0 and must be attributed.
- Link to Wilbrink's institutional scan; do not mirror it.
- Do not presume reuse rights for older journal PDFs or project reports.
- The Graeme Taylor repository showed no explicit license during this audit; its
  code must not be copied. Mathematical ideas may be independently specified
  and clean-room reimplemented.

## Main operational conclusion

The unrestricted 84-vertex residual CSP is the cleanest universal search
target. Conditional automorphism branches can be useful calibration projects,
but must remain visibly conditional. A negative universal claim requires the
exact generator, a complete proof-producing run, the proof artifact, a checker,
hashes, and reproduction logs.
