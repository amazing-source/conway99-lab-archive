# Wave 97 protocol freeze

## Target

Starting from the verified characteristic-seven evaluation code, seek an
unrestricted obstruction to a hypothetical
\(\operatorname{srg}(99,14,1,2)\) through exterior powers, generalized
Hamming weights, represented matroids, Schur evaluation algebras, or finite
orthogonal orbit counts.

No graph automorphism or vertex-transitivity assumption is permitted.

## Frozen imports

1. Wave 51:
   \[
   S=2A-J+I,\quad S^2=49(I+J),
   \]
   and, if \(r=\operatorname{rank}_{\mathbf F_7}S\),
   \[
   \operatorname{SNF}(S)=
   \operatorname{diag}(1^r,7^{99-2r},49^{r-1},490).
   \]
2. Wave 80:
   \[
   R=\operatorname{row}_{\mathbf F_7}(S),\qquad
   d(R^\perp)\ge6,
   \]
   and at \(r=28\),
   \[
   C/R\cong O^-(16,7),\quad
   R^\perp\cap\mathbf1^\perp/R\cong O^-(42,7),
   \]
   with orthogonal complement \(O^+(26,7)\).
3. Wave 80's forced short codeword has balanced weight 14, 16, or 18 and
   self-dot \(0,4,1\), respectively.
4. Wave 46 is a scope control: ordinary code enumerators and a full Schur
   cube for the different 231-coordinate triangle-projector code did not
   exclude the endpoint.

Exact imported manifest hashes are frozen in `input-freeze.sha256`.

## Questions

1. Does the Schur algebra of the 99-coordinate Seidel hull close sharply?
2. What exact code, spectrum, and Smith constraints are carried by
   \(C_2(S)\)?
3. Do generalized Hamming weights improve the support-six boundary?
4. Do finite orthogonal orbit counts exclude any forced short-vector type?
5. Which parts are genuine obstructions, and which are loss-of-information
   reformulations?

## Status rules

- Exact consequences proved from verified imports may be labelled
  `DERIVED`.
- Discovery does not label itself `VERIFIED`.
- A Smith profile, orbit count, formal code, or Hilbert function is not a
  graph construction.
- A lower bound on generalized weights is not a nonexistence certificate.
- `UNKNOWN` is retained for rank 28, a strict endpoint exclusion,
  Conway-99, and novelty unless an independent certificate changes it.
