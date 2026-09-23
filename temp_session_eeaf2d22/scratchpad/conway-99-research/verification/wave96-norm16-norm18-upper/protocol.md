# Wave 96 independent verification protocol

Date frozen: 2026-07-28

Role: verifier

Discovery input:

```text
attempts/wave96-norm16-norm18-upper/package-manifest.sha256
sha256 1d1e7d01edfbfcd2871683390b56e16dc36a18cfc899f301f15a0fce3b246a73
```

## Scope

- Assume a hypothetical `srg(99,14,1,2)`.
- Import the lattice dictionary, shell facts, modular inequality, `N14`
  endpoint bound, and rank-30 scalar prefix only from the frozen verified
  manifests listed in `input-freeze.sha256`.
- Recompute the weighted cap arithmetic, fixed-C4 projector, norm-20
  profiles and exclusions, alternating-C4 bound, and rank-30 implication
  without importing discovery code.
- Audit the proposed Jacobi continuation only for honest status and the
  coefficient/index interpretation that follows from the checked finite
  identities.

## Fail-closed boundary

- A pointwise cap is not inferred from an average or a spherical relaxation.
- The cross-polytope is not treated as a lattice or graph.
- The Jacobi route is not promoted without a transformation law and signed
  coefficient control.
- No rank exclusion, shell upper bound, graph nonexistence, resolution, or
  novelty claim is permitted.
