# Wave 120 independent verification protocol

The discovery package is frozen at manifest SHA-256
`e2e35519158556a1810affdee4bc148a333ee95a63557ea1a1e687dfcd883017`.
The checker imports no discovery Python and authenticates every frozen
manifest entry before reading the machine-readable witness.

The verification reconstructs:

1. the C4 principal projector block and the exact real affine minima;
2. the integer anchor-mass proof, including its general `r` form;
3. all six norm-pair inner-product intervals;
4. the forty signed records as abstract coordinates, including rooted type
   counts and all four anchor equations;
5. every pair norm/profile condition and binary distance;
6. the all-subsets inequality from a symbolic fixed-sign argument;
7. positive definiteness and rank via all forty exact integer leading
   principal determinants of the scaled residual Gram.

The verified Wave96 verifier package, not its discovery package, supplies
the imported norm-20 status. The verified Wave112 package supplies the
rooted outside partition.

The verifier does not encode the 95 outside eigen-equations, one common
adjacency matrix, or kernel-code membership. It therefore cannot promote
the formal witness to an eigenvector family or graph.
