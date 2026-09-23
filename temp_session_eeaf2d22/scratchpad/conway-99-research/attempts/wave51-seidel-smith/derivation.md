# Conditional Seidel Smith form

Claim label: `CANDIDATE`.

Let \(A\) be the adjacency matrix of a hypothetical
\(\operatorname{srg}(99,14,1,2)\), let \(J\) be the all-ones matrix, and set
\[
S=2A-J+I.
\]
The standard strongly regular graph identity is
\[
A^2=12I-A+2J,
\]
while \(AJ=JA=14J\) and \(J^2=99J\). Direct expansion gives
\[
S^2=49(I+J).
\]
The spectrum of \(S\) is
\[
-70^1,\quad 7^{44},\quad (-7)^{54},
\]
so
\[
|\det S|=70\cdot 7^{98}=10\cdot7^{99}.
\]

## 1. The representation modulo 7

Write \(G=S\bmod 7\) and
\[
r=\operatorname{rank}_{\mathbf F_7}(G).
\]
Because \(G^2=0\), every Jordan block has size at most two. A size-two
nilpotent block has rank one, so the complete Jordan type is
\[
G\sim J_2(0)^r\oplus J_1(0)^{99-2r}.
\]
In particular, \(r\le49\).

## 2. The 7-primary Smith factors

Work over the 7-adic integers. The matrix \(U=I+J\) is invertible there because
\[
\det(U)=100
\]
is a 7-adic unit. From \(S^2=49U\),
\[
49S^{-1}=U^{-1}S.
\]
Left multiplication by the integral unimodular matrix \(U^{-1}\) does not
change Smith exponents.

Let
\[
0\le a_1\le\cdots\le a_{99}
\]
be the 7-adic valuations of the Smith factors of \(S\). The Smith exponents of
\(49S^{-1}\) are
\[
2-a_{99}\le\cdots\le2-a_1.
\]
They must equal the exponents of \(S\). Consequently
\[
a_i+a_{100-i}=2.
\]
Exactly \(r\) Smith factors are units modulo 7, so exactly \(r\) of the
exponents are zero. Pairing forces exactly \(r\) exponents to be two, with the
remaining \(99-2r\) equal to one:
\[
0^r,\quad1^{99-2r},\quad2^r.
\]

## 3. The 2- and 5-primary factors

Modulo 2,
\[
S=I+J.
\]
Since \(99\) is odd, this matrix has kernel spanned by the all-ones vector and
rank 98. Since the determinant has 2-adic valuation one, precisely one Smith
factor is even.

Modulo 5, \(S\mathbf1=-70\mathbf1=0\). Also
\[
S^2=49(I+J),
\]
and \(I+J\) has rank 98 modulo 5 because its eigenvalue on \(\mathbf1\) is
\(100=0\) while it is the identity on the coordinate-sum-zero subspace.
Therefore \(98=\operatorname{rank}(S^2)\le\operatorname{rank}(S)\le98\).
Again, precisely one Smith factor is divisible by 5.

Invariant factors form a divisibility chain. Hence the unique factor divisible
by 2 and the unique factor divisible by 5 must both be the final invariant
factor. The final factor is also one of the \(r\) factors with 7-adic exponent
two. No other primes divide the determinant. For \(1\le r\le49\), the complete
conditional Smith normal form is therefore
\[
\boxed{\operatorname{SNF}(S)=
\operatorname{diag}\left(
1^r,\,
7^{99-2r},\,
49^{r-1},\,
490
\right).}
\]
Equivalently,
\[
\operatorname{coker}(S)\cong
(\mathbf Z/7)^{99-2r}\oplus
(\mathbf Z/49)^{r-1}\oplus
\mathbf Z/490.
\]

## 4. A symmetric-square obstruction

Any symmetric rank-\(r\) matrix over a field of odd characteristic can be
written
\[
G=VHV^\mathsf T,
\]
where \(V\) has \(r\) columns and \(H\) is nonsingular and symmetric. Denote
the rows of \(V\) by \(v_i\). In the induced bilinear form on
\(\operatorname{Sym}^2(\mathbf F_7^r)\), the Gram matrix of the 99 pure
squares \(v_i\odot v_i\) is
\[
G\circ G.
\]
The Seidel matrix has zero diagonal and every off-diagonal entry is \(1\) or
\(-1\). Thus
\[
G\circ G=J-I.
\]
Over \(\mathbf F_7\), \(99\equiv1\), so \(J-I\) has rank 98. It follows that
\[
98\le\dim\operatorname{Sym}^2(\mathbf F_7^r)
=\frac{r(r+1)}2,
\]
and hence
\[
r\ge14.
\]

There is no hidden extra dimension in this particular argument. From
\(G^2=0\) and the full column rank of \(V\), one gets \(V^\mathsf TV=0\), so
\[
\sum_i v_i\odot v_i=0.
\]
The Gram rank 98 shows that this is the unique linear relation among the 99
pure squares. The symmetric-square route therefore stops at \(r\ge14\).

## 5. Endpoint comparison

The independently verified current interval is
\[
28\le r\le44.
\]
Every one of its 17 integer values satisfies the Jordan, determinant, local
rank, and Smith-divisibility tests recorded in `exact-results.json`. The new
symmetric-square floor \(r\ge14\) is strictly weaker than the existing floor
\(r\ge28\).

The exact structural output of this lane is the conditional Smith/cokernel
classification. It does **not** exclude an endpoint rank, construct a matrix,
or prove nonexistence of the graph.

