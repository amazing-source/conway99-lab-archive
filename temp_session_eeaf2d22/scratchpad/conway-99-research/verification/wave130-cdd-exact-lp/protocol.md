# Independent verification protocol

Scope is restricted to exact rational feasibility of the finite cutoff-28
level-7 index-10/index-70 Jacobi relaxation.

The verifier:

1. freezes and replays all 34 entries in the Wave130 discovery manifest;
2. imports no discovery module or discovery verifier;
3. reads no serialized Fourier-column cache;
4. does not call or reuse the cddlib candidate generator;
5. reconstructs `phi_{-2,1}` and `phi_{0,1}` from product/theta formulas;
6. reconstructs every level-7 Eisenstein product and exact Fricke-eigen
   Fourier-echelon block;
7. rebuilds all 239 L/K Fourier columns through cutoff 28;
8. independently regenerates every original equality and inequality; and
9. substitutes the frozen 239-coordinate rational primal exactly.

Promotion requires all 454 equalities and all 1,686 inequalities to pass,
with the exact 506 tight labels agreeing with the sealed candidate.  This
does not promote any graph, lattice, rank-realizability, or global
all-cutoff claim.
