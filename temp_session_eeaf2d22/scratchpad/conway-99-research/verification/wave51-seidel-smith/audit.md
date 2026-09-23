# Wave 51 independent Seidel-Smith audit

Date UTC: 2026-07-27T19:09:30Z

## Verdict

- `VERIFIED`: after correcting one signed-spectrum transcription error, the
  conditional Smith form is
  \[
  \operatorname{diag}(1^r,7^{99-2r},49^{r-1},490),
  \qquad r=\operatorname{rank}_{\mathbf F_7}(S).
  \]
- `VERIFIED`: modulo 7 the Jordan type is
  \(J_2(0)^r\oplus J_1(0)^{99-2r}\).
- `VERIFIED`: the symmetric-square argument gives only \(r\ge14\).
- `REFUTED`: the discovery text's spectrum
  \(-70^1,+7^{44},-7^{54}\) has its two nonprincipal multiplicities
  reversed. The correct spectrum is
  \(-70^1,+7^{54},-7^{44}\).
- `UNKNOWN`: existence or nonexistence of the graph, and every endpoint rank
  \(r=28,\ldots,44\).

The spectrum correction does not affect the absolute determinant or any
Smith, Jordan, or symmetric-square conclusion.

## Independent reconstruction

For a hypothetical `srg(99,14,1,2)`,
\[
A^2=12I-A+2J,\quad AJ=JA=14J,\quad J^2=99J.
\]
Expanding \(S=2A-J+I\) gives
\[
S^2=49I+49J.
\]

On the all-ones vector, \(A\) has eigenvalue 14 and \(S\) has eigenvalue
\(-70\). On its orthogonal complement, \(A\) obeys
\[
x^2+x-12=(x-3)(x+4)=0.
\]
Dimension and trace give multiplicities 54 for \(3\) and 44 for \(-4\).
Consequently the Seidel spectrum is
\[
-70^1,\quad 7^{54},\quad(-7)^{44},
\]
which has trace zero and absolute determinant \(10\cdot7^{99}\). The
discovery spectrum instead has trace \(-140\), so that exact assertion is
false even though its absolute determinant is unchanged.

## Why the full Smith form really is forced

Let \(U=I+J\). Its determinant is 100, a unit in the 7-adic integers. Thus
\(U\in\mathrm{GL}_{99}(\mathbf Z_7)\), and
\[
49S^{-1}=U^{-1}S.
\]
If \(a_1\le\cdots\le a_{99}\) are the 7-adic Smith exponents of \(S\), the
ordered Smith exponents on the left are
\[
2-a_{99}\le\cdots\le2-a_1.
\]
The right side is 7-adically equivalent to \(S\). Componentwise equality of
the two ordered lists gives
\[
a_i+a_{100-i}=2.
\]
It also forces every exponent into \(\{0,1,2\}\). Rank \(r\) modulo 7 says
that exactly \(r\) exponents are zero. Pairing then forces exactly \(r\)
exponents to be two, leaving \(99-2r\) exponents equal to one.

The step above is essential. Rank modulo 7 and the determinant alone do not
determine the 7-primary factors. For example, at \(r=28\), both exponent
profiles
\[
0^{28},1^{43},2^{28}
\quad\text{and}\quad
0^{28},1^{44},2^{26},3^1
\]
have 99 entries, rank 28 modulo 7, and total 7-adic determinant valuation 99.
Only the reciprocal identity excludes the second profile.

Modulo 2, \(S=I+J\) has rank 98. Modulo 5, \(S\mathbf1=0\), while
\(S^2=49(I+J)\) has rank 98, so \(S\) also has rank 98. Rank alone locates
one divisible invariant factor for each prime but does not determine its
exponent. The determinant supplies \(v_2(\det S)=v_5(\det S)=1\). Since
invariant factors form a divisibility chain, both unique local factors occur
in the last invariant factor. Aligning the nondecreasing 2-, 5-, and
7-primary exponent lists therefore gives, with no remaining local-to-global
choice,
\[
\operatorname{SNF}(S)
=\operatorname{diag}(1^r,7^{99-2r},49^{r-1},490).
\]

The proof uses \(U\) as a unit only over \(\mathbf Z_7\). It is not a unit
over \(\mathbf Z_2\) or \(\mathbf Z_5\); the verifier has a hostile test that
would catch an invalid reuse at those primes.

## Jordan and symmetric-square checks

Modulo 7, \(G=S\bmod7\) satisfies \(G^2=0\). Every nilpotent Jordan block
therefore has size one or two. Each size-two block contributes rank one, so
rank \(r\) forces exactly
\[
J_2(0)^r\oplus J_1(0)^{99-2r}.
\]

Because \(G\) is symmetric over the odd-characteristic field
\(\mathbf F_7\), it factors as \(G=VHV^\mathsf T\), where \(V\) has \(r\)
columns and \(H\) is nonsingular symmetric. The induced nondegenerate form on
\(\operatorname{Sym}^2(\mathbf F_7^r)\) makes the Gram matrix of the 99 pure
squares equal to \(G\circ G=J-I\). This matrix has rank 98 over
\(\mathbf F_7\). Hence
\[
98\le\frac{r(r+1)}2,
\]
so \(r\ge14\).

For completeness, \(G^2=0\) and the full column rank of \(V\) imply
\(V^\mathsf TV=0\), producing the relation that the 99 pure squares sum to
zero. Their Gram rank is already 98, so this is the unique relation and this
dimension argument cannot improve itself.

## Hostile tests and boundary

Thirteen independent tests:

- reject the discovery spectrum by its nonzero trace;
- distinguish 7-adic invertibility of \(I+J\) from its failure at 2 and 5;
- exhaust every reciprocal 7-profile for \(r=1,\ldots,49\);
- exhibit a different profile with the same modular rank and determinant;
- show rank modulo 2 does not by itself distinguish exponent one from three;
- assemble all primary factors and check count, divisibility, determinant,
  and ranks modulo 2, 5, and 7;
- reconstruct all square-zero Jordan dimensions;
- recompute the symmetric-square boundary;
- confirm that all 17 imported ranks \(28,\ldots,44\) survive;
- compare frozen discovery and independent artifact bytes.

No automorphism, graph instance, or unrecorded existence assumption was used.
The Smith profiles are necessary conditions only. They neither construct a
matrix nor exclude a graph.

