# Wave 108 independent verification protocol

Role: `verifier`.

Frozen input:

- Wave 107 sealed package-manifest SHA-256:
  `7e899602825d3cdf989affade8a1e5a6256f17ba911f6351ea8bfe4a3b05d2b0`.
- Wave 105 sealed package-manifest SHA-256:
  `b0fd40eda5a3677d4a835788cea20dfcb9bb3c5764719fc04536893f1b5da4a1`.

Scope: conditional consequences of an induced
`H=C4 Cartesian K3` principal subgraph inside a hypothetical
`srg(99,14,1,2)`. No existence of the full SRG or occurrence of the motif is
assumed beyond this conditional scope.

The verifier must:

1. validate every Wave 107 manifest entry before running discovery code;
2. reconstruct `H` independently and verify its regularity and spectrum;
3. derive the restricted resolvent from
   `A^2=12I-A+2J`, then use Jacobi's complementary-minor identity and a
   rank-one determinant calculation to obtain `chi_D`;
4. refute `x^2-9x-38` using the independently forced value
   `trace(D^2)=1098`;
5. replay the first four spectral moments, edge/triangle/four-cycle counts,
   nullity, shifted ranks, interlacing, and the Perron/connectedness argument;
6. preserve the status wall:
   no spectral obstruction, motif extension `UNKNOWN`, Conway-99 `UNKNOWN`,
   and literature novelty `UNKNOWN`.

All verifier arithmetic must use only Python's standard library and exact
integers or rational numbers. The discovery checker may be rerun only after
the frozen manifest has validated.
