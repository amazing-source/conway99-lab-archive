# Wave 101 independent verification protocol

Discovery package:

```text
attempts/wave101-all-rank-level7-lp/package-manifest.sha256
sha256 54d620a8644d7efe5d2e418869b035331127862c2125ef3da325272417307619
```

The verifier first recorded a byte inventory of all discovery files and then
reconstructed the calculation without importing or executing discovery code.
A broad repository grep returned a few Wave 101 prose-line matches during the
same batched read as the manifest hash; this process note is retained rather
than overstating clean-room isolation. The exact independent result and its
hash were frozen before the discovery files were opened for comparison.

`precomparison.sha256` records the initial arithmetic freeze. After
comparison, the independent result was augmented with explicit direction
residues for every prefix objective, without changing any LP certificate.
`postcomparison-final.sha256` records the final verifier and result bytes.

## Assigned checks

1. Reconstruct the complete 15-dimensional space
   `M_22(Gamma0(7))` and its exact Fricke involution.
2. Derive the rank-dependent Poisson factor, including its sign and power of
   seven, for every `q=2,4,...,14`.
3. Verify every submitted scalar LP optimum with an exact feasible primal
   point and a nonnegative exact dual identity.
4. Verify antipodal parity rounding and independently replay the level-one
   mod-seven affine scope.
5. Attack the integral zero-prefix controls, especially the claim that
   `x7=x8=x9=0` remains feasible in all seven rows.
6. Verify the mod-two lattice upper comparisons and check for an actual
   lower/upper collision.
7. Enforce the Wave 71 dictionary boundary: only `x7,x8,x9` may be identified
   with the norm-14, norm-16, and norm-18 signed-unit graph vectors.

## Verdict policy

- Exact agreement plus fail-closed scope permits `VERIFIED`.
- A valid but nonsharp submitted comparison may be retained with an explicit
  sharpening.
- A formal scalar point is never promoted to a lattice, marked frame, graph,
  or nonexistence certificate.
