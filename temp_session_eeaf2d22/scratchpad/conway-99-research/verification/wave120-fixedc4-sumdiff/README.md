# Wave 120 independent verification

Verdict: `VERIFIED_WITH_CLARIFICATION`, conditional on a hypothetical
`srg(99,14,1,2)` and the frozen verified inputs.

The exact real minimum for doubled alternating C4 coordinates is `112/5`.
The four anchor equations and `mu=2` sharpen every integer eigenvector in
that slice to norm at least `32`, and the same argument gives

```text
||x_1+...+x_r||^2 >= 4r^2+8r.
```

All six submitted pairwise inner-product intervals are correct. The
forty-record file also passes independent checks for fixed-C4 type counts,
all four anchor equations, pairwise norm and low-norm magnitude profiles,
every positive-subset anchor inequality, binary weight/distance, and an
exact positive-definite rank-40 residual Gram.

The object is only a formal relaxation witness. Its signed supports do not
satisfy the 95 outside eigen-equations, and no common graph adjacency or
target kernel-code membership is encoded. Its abstract spherical
realization need not preserve the displayed unit coordinates. Thus it
shows that the scoped pairwise Gram and binary distance relaxations cannot
prove a cap below 40; it is not a family of eigenvectors and not a graph.

Chronology clarification: Wave120 described the Wave96 norm-20
classification as awaiting verification. The frozen Wave96 verifier
package now marks that theorem verified conditional on its own frozen
inputs.

Caps 25 and 24, ranks 28 and 30, Conway-99, and novelty remain `UNKNOWN`.
