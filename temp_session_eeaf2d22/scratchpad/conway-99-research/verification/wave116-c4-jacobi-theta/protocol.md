# Wave 116 independent verification protocol

Role: `verifier`.

## Frozen input

The discovery package is identified by the SHA-256
`9c474c8fc6c04e382b7fd506997c7ec81cb5ea5fa38453e6f284271eda933d98`
of `attempts/wave116-c4-jacobi-theta/package-manifest.sha256`.  Every entry
listed by that manifest must match before verification and after replay.

## Accepted conditional inputs

Only the already verified Waves 66, 71, and 112 facts are imported:

1. `E_-4=(-A+3I+J/9)/7` and the centered vectors `u_i`;
2. `L` is even of rank 44, `3u_i in L`, and
   `K=sqrt(7)L*` is even of level seven;
3. through norm 18, vectors of `K` correspond to integral coordinate
   vectors `t_i=<y,u_i>`;
4. there are 2,079 induced four-cycles and the rank-28 row has at least
   105,624 oriented short-vector/cycle incidences.

No graph automorphism or equivalence of four-cycle orbits is assumed.

## Independent gates

1. Reconstruct the restricted projector and its complete rational spectrum.
2. Derive each `K`/`L` marking from lattice membership, not merely from a
   rational Gram matrix.
3. Check the four discriminant classes by row reduction over `F_7`.
4. Re-derive the Poisson factor from rank and determinant, including the
   `i^(-22)=-1` phase and normalized Fricke power.
5. Recompute the Fourier-pattern projected norm, antipodal factor, and
   52,812 versus 51,975 threshold.
6. Construct the exact degree-eight cardinal polynomials on
   `{-4,...,4}` and check the total degree-32 product interpretation.
7. Preserve the distinction between a strategy and a proved upper bound.
8. Keep rank 28, Conway-99, and literature novelty `UNKNOWN`.

The verifier code does not import or execute discovery code.
