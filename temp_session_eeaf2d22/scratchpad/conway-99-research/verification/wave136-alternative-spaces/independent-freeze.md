# Wave 136 independent verifier freeze

This file was written before reading the Wave 136 discovery code or results.
It fixes the verifier's conventions and the consequences to be reconstructed
independently.

## Conway adjacency identity

Let \(A\) be the adjacency matrix of a hypothetical
\(\operatorname{srg}(99,14,1,2)\).  Over the integers,

\[
A^2=12I-A+2J.
\]

Hence over \(\mathbf F_2\),

\[
A^2=A.
\]

Because \(A\) is symmetric with zero diagonal, its binary row space
\(D=\operatorname{im}(A)\) has an alternating, nondegenerate restriction of
the standard dot product:

* every vector in \(D\) has even Hamming weight;
* \(D\cap D^\perp=0\);
* the previously established binary rank is \(54\), so \(D\) is a
  \(54\)-dimensional symplectic space.

## Quadratic form and Gauss constraint

For \(u\in D\), define

\[
q(u)=\operatorname{wt}(u)/2\pmod 2.
\]

This is a quadratic refinement of the dot product because

\[
q(u+v)+q(u)+q(v)=u\mathbin{\cdot}v.
\]

If \(r_i\) is an adjacency row, then \(q(r_i)=14/2=1\).  For
\(x\in\mathbf F_2^{99}\),

\[
q(Ax)=\sum_i x_i+\sum_{\{i,j\}\in E}x_ix_j.
\]

The Gauss sum of any nondegenerate quadratic form on a \(54=2\cdot27\)
dimensional symplectic space is

\[
\sum_{u\in D}(-1)^{q(u)}=(-1)^{\operatorname{Arf}(q)}2^{27}.
\]

Thus, if \(N_0\) and \(N_2\) count words in \(D\) whose weights are
respectively \(0\) and \(2\) modulo \(4\), then exactly one of the two
possibilities holds:

\[
(N_0,N_2)=(2^{53}+2^{26},2^{53}-2^{26})
\]

or

\[
(N_0,N_2)=(2^{53}-2^{26},2^{53}+2^{26}).
\]

The adjacency identity and rank alone fix the magnitude, not the Arf sign.
Any discovery witness whose residue enumerator has another difference is
refuted.  A claim that this derivation fixes the sign requires an additional,
separately proved premise.

## Additive GF(4) graph-state convention

Represent \(\mathbf F_4=\{0,1,\omega,\omega^2\}\) as
\(\mathbf F_2^2\) by

\[
(a,b)\longmapsto a+\omega b.
\]

For binary \(x\), define

\[
c(x)=x+\omega Ax,\qquad S_A=\{c(x):x\in\mathbf F_2^{99}\}.
\]

The trace-Hermitian form becomes

\[
\langle (x,Ax),(y,Ay)\rangle
=x\mathbin{\cdot}Ay+Ax\mathbin{\cdot}y=0
\]

because \(A=A^T\).  The map is injective through its first component, so
\(|S_A|=2^{99}\).  Therefore \(S_A\) is an additive self-dual code.  No
\(\mathbf F_4\)-linearity is implied.

For a coordinate with state \((x_i,(Ax)_i)\), use the state order
\(00,10,01,11\), corresponding to \(0,1,\omega,\omega^2\).  The complete
additive MacWilliams character matrix in this order is

\[
H=
\begin{pmatrix}
1&1&1&1\\
1&1&-1&-1\\
1&-1&1&-1\\
1&-1&-1&1
\end{pmatrix}.
\]

Self-duality gives
\[
W(z)=2^{-99}W(Hz).
\]

Any lower-dimensional "symmetrized" transform must be derived from an
explicitly stated variable identification that is invariant under this
substitution.  Coefficients indexed by the four state counts
\((n_{00},n_{10},n_{01},n_{11})\) cannot be called graph-forced merely from
the SRG parameters unless an exact counting derivation is supplied.

## Promotion boundary

The verifier will accept exact identities and independently replayed finite
coefficient calculations only.  An enumerator satisfying these necessary
identities is not a code, a graph-state realization, or a Conway graph.
Conway-99 remains `UNKNOWN`.
