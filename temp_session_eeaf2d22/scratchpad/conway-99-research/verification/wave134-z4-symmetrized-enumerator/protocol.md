# Verification protocol

## Independence boundary

The derivation used only the frozen Wave2 statement and the sealed Wave131 and
Wave132 statements. Before the Wave134 discovery seal arrived, the verifier
derived the Smith-to-`Z4` types, residue/torsion identities, structural zero
ranges, small-support composition tables, collision arguments, and
symmetrized MacWilliams transform. It did not read or import discovery
implementations.

After sealing, the verifier:

1. checks the pinned SHA-256 of the discovery package manifest;
2. checks all 13 manifest entries and rejects paths outside the discovery
   package;
3. reads only `exact-results.json` and `search-status.json` as claim data;
4. compares the sealed Smith data, code types, forced tables, totals, and
   transform-state counts with the clean-room derivation; and
5. enforces that stale searches have inference `NONE` and the corrected
   rational/integral problems remain unrun and `UNKNOWN`.

The discovery test suite is run only as a secondary package-integrity check;
the independent result does not depend on it.

## Hostile checks

- Keep `q_u+q_v` distinct from `q_u-q_v`.
- Permit primal torsion weight seven; forbid dual torsion weights one through
  seven.
- Use `Res(Cperp)=D intersect even`. Since `1` lies in `D` and `d(D)>=8`,
  every nonzero even dual residue has weight from 8 through 90. Thus all four
  weight-92 zero/two-symmetry orbits are forced zero.
- Compare formula-derived composition tables with a separate exact Venn-atom
  enumeration.
- Check the MacWilliams coefficients both by full polynomial expansion and a
  factored integer formula.
- Reject any feasibility, realizability, novelty, or Conway-99 promotion in
  the absence of a corrected exact witness or certificate.
