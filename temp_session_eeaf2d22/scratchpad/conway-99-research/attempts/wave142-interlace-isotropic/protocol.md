# Wave142 protocol

## Frozen target

Condition on a hypothetical adjacency matrix of an
`srg(99,14,1,2)`. Over `F2` the accepted premises are

```text
A=A^T, diag(A)=0, A^2=A, A*1=0,
rank(A)=54, nullity(A)=45, d(im(A))>=14.
```

Investigate only:

1. the size-refined vertex-nullity interlace data
   `nullity_F2(A[S])`;
2. the isotropic matroid represented by `IAS(G)=[I|A|I+A]`;
3. exact local consequences through six vertices and the complement band
   forced by `d(im(A))>=14`; and
4. whether these consequences are rows in, or require a lift of, the
   Wave141 bivariate table
   `B[i,j]=#{x:wt(x)=i,wt(Ax)=j}`.

## Certificate boundary

- Import only hash-pinned repository inputs.
- Use exact integer or rational arithmetic.
- Enumerate at most the 62 accepted six-vertex classes and their 64
  diagonal toggles.
- Do not enumerate subsets of a 99-vertex graph.
- Treat local coefficient nonnegativity as no stronger than its exact
  displayed inequality.
- A new general upper bound requires an exact inequality below `4158`.
- Absence of such an inequality is `UNKNOWN`, not a proof that the space
  cannot work.
- Discovery does not verify itself.

## Primary definitions

The state-sum definition of the two-variable/vertex-nullity interlace
polynomial is from Arratia, Bollobas, and Sorkin:
<https://arxiv.org/abs/math/0209054>.

The `IAS(G)=[I|A|I+A]` isotropic-matroid bridge and its parametrized Tutte
specializations are described by Traldi:
<https://arxiv.org/abs/1301.0293> and
<https://arxiv.org/abs/1301.4946>.

These references establish terminology and general identities only. They do
not establish any Conway-99 consequence or novelty claim.
