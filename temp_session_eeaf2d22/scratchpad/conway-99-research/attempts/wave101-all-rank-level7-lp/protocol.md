# Wave 101 discovery protocol

Role: `proof_a`.

1. Freeze the independently verified Wave 66/71 lattice transfer and the
   independently verified-with-literature-correction Wave 86 full
   `M_22(Gamma0(7))` implementation.
2. Use every surviving `q=2,4,...,14`; do not select rows after seeing an
   answer.
3. Use the exact Poisson factor `-7^(11-q/2)` and verify the complete
   15-dimensional basis and Fricke involution.
4. Form the full first-Sturm-bound scalar positivity cone after eliminating
   `x14` with `y0=1`.
5. Accept an LP bound only with both an exact nonnegative dual identity and a
   matching exact feasible primal point.
6. Check parity, level-one mod-7 objective residues, and rigorous lattice
   upper bounds.
7. Preserve zero-prefix controls and all non-colliding upper-bound
   comparisons.
8. Do not interpret coefficients beyond `x9` as signed-unit eigenvectors.
9. Label all new findings `DERIVED` or `UNKNOWN`; discovery does not promote
   itself to `VERIFIED`.
10. Do not stage or commit from this worker.
