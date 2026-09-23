# Wave 170 independent verification

Verdict: `VERIFIED_WITH_SCOPE`.

The verifier independently confirms:

- `(n0,n1,n2,n3)=(32-p,144+3p,36-3p,p)` at every triangle block;
- the global unordered-pair counts and `N2=n3`;
- maximum clique size seven in the block-intersection graph;
- `rank_F3(B*B^T)=55`; and
- `55<=rank_F3(B)<=98`.

These are exact structural constraints. They recover the known prism identity
and add clique/code data, but do not improve the numerical bound, exclude the
endpoint, or resolve Conway-99.
