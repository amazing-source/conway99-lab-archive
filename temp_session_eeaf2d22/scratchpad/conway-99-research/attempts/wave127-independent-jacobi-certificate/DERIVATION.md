# Independent level-7 Jacobi derivation

Status: **DERIVED finite model; Conway-99 remains UNKNOWN.**

This derivation was completed without reading the Wave126 implementation.

## 1. The weak-Jacobi module

Put

\[
A=\phi_{-2,1},\qquad B=\phi_{0,1}.
\]

Our normalizations have

\[
A(\tau,z)=(y^{-1}-2+y)+O(q),\qquad
B(\tau,z)=(y^{-1}+10+y)+O(q),
\]

and \(A(\tau,0)=0,\ B(\tau,0)=12\).  For even weight and the
full integral translation group,

\[
J^{\mathrm{weak}}_{22,10}(\Gamma_0(7))
=
\bigoplus_{c=0}^{10}
M_{22+2c}(\Gamma_0(7)) A^cB^{10-c}.
\]

Here is a direct proof.  If \(\phi\) has weight \(k\) and index \(m\), then
\(\phi(\tau,0)\) is a modular form of weight \(k\).  Subtract

\[
12^{-m}\phi(\tau,0)B^m.
\]

The difference vanishes at \(z=0\).  It is even in \(z\), because
\(-I\in\Gamma_0(7)\) and \(k\) is even, so the zero has order at least two.
The form \(A\) has exactly such a double zero modulo the elliptic lattice.
Division by \(A\) therefore leaves a weak Jacobi form of weight \(k+2\) and
index \(m-1\).  Induction gives the displayed decomposition.  Evaluating at
\(z=0\) at every induction step also proves uniqueness.

The curve \(X_0(7)\) has genus zero, two cusps, and two elliptic points of
order three.  Hence, for the even weights used here,

\[
\dim M_w(\Gamma_0(7))=1+2\left\lfloor w/3\right\rfloor.
\]

For \(w=22,24,\ldots,42\), this gives

```text
15, 17, 17, 19, 21, 21, 23, 25, 25, 27, 29
```

and total dimension \(239\).

## 2. Exact modular bases

Let \(\chi=(\frac{-7}{\cdot})\), the primitive odd quadratic character
modulo seven.  For every odd \(a\geq3\), the implementation constructs

\[
\begin{aligned}
E_a^C&=-\frac{B_{a,\chi}}{2a}
 +\sum_{n\geq1}\sum_{d\mid n}\chi(d)d^{a-1}q^n,\\
E_a^T&=\sum_{n\geq1}\sum_{d\mid n}\chi(n/d)d^{a-1}q^n.
\end{aligned}
\]

Products \(E_a^\star E_{w-a}^{\star'}\) have weight \(w\), level seven,
and trivial character.  The code selects a subset whose exact rational
coefficient matrix has rank \(\dim M_w(\Gamma_0(7))\) through the Sturm
bound

\[
\left\lfloor\frac{[\mathrm{SL}_2(\mathbb Z):\Gamma_0(7)]w}{12}\right\rfloor
=\left\lfloor\frac{2w}{3}\right\rfloor.
\]

Membership plus this exact rank calculation proves that the selected
products form a basis; this is not a floating rank heuristic.

## 3. Fricke scaling

Use the normalized weight-\(w\) Fricke operator

\[
(f|W_7)(\tau)=7^{-w/2}\tau^{-w}f(-1/(7\tau)).
\]

The odd Eisenstein factors are exchanged by Fricke.  On their even-weight
products the factors are rational; for example,

\[
(E_a^CE_b^C)|W_7=-7^{(a-1)/2+(b-1)/2}E_a^TE_b^T.
\]

The other three orientations are obtained by replacing the exponent
\((a-1)/2\) by \((1-a)/2\) whenever \(C\) is replaced by \(T\).
Applying this map twice is the identity.

Write the L-side form as

\[
\Phi_L=\sum_{c=0}^{10} f_c A^cB^{10-c},
\qquad f_c\in M_{22+2c}(\Gamma_0(7)).
\]

For discriminant exponent \(q_{\rm disc}=16\), the L/K transformation is

\[
\Phi_K\left(-\frac1{7\tau},\frac z{7\tau}\right)
=-7^8\tau^{22}e^{20\pi iz^2/\tau}\Phi_L(\tau,z).
\]

Using

\[
A(-1/\tau,z/\tau)=\tau^{-2}e^{2\pi iz^2/\tau}A(\tau,z)
\]

block by block gives

\[
\Phi_K
=\sum_{c=0}^{10}h_c(\tau)
 A(7\tau,7z)^cB(7\tau,7z)^{10-c},
\qquad
h_c=-7^{-3-c}(f_c|W_7).
\]

Thus the exponent is exactly

\[
q_{\rm disc}/2-11-c=-3-c.
\]

## 4. Finite LP constraints

At cutoff \(N\), all rows are rational.  They impose:

1. \(c_L(0,0)=c_K(0,0)=2079\);
2. holomorphy, \(r^2\leq4mn\), on the L side (\(m=10\)) and K side
   (\(m=70\));
3. coefficient nonnegativity on both sides;
4. the K minimum gap \(c_K(n,r)=0\) for \(1\leq n\leq6\);
5. graph support \(c_K(n,r)=0\) for \(7\leq n\leq10,\ |r|>28\);
6. the tight-frame second moments

\[
11\sum_r r^2c_L(n,r)=10n\sum_r c_L(n,r),
\qquad
11\sum_r r^2c_K(n,r)=70n\sum_r c_K(n,r).
\]

A floating solver outcome is diagnostic only.  Exact finite feasibility is
promoted only if a rational coefficient vector is checked against every
exact equality and inequality.  Even such a vector would establish only
that this finite relaxation is feasible, not that a graph exists.

## 5. Exact face reduction

The raw modular basis is badly conditioned.  The implementation therefore
uses only invertible exact coordinate changes:

1. Fourier-echelonize each \(M_w(\Gamma_0(7))\) basis;
2. compute the rational Fricke matrix and verify \(W_7^2=I\);
3. split into the \(+1\) and \(-1\) Fricke eigenspaces;
4. Fourier-echelonize again inside each eigenspace.

Before solving, affine equality rows are reduced to an exact rational
basis, and positive-proportional inequality rows are deduplicated.  The
affine equalities are then put in rational reduced row echelon form.  This
expresses all 239 original variables in terms of fewer free parameters.

A balanced floating LP is used only to suggest active inequalities.  Those
active rows are imposed over \(\mathbb Q\), the resulting face is
parameterized exactly, and the process recurses.  The final rational point
is substituted into every unreduced row.

This produced verified rational feasible points at cutoffs 10, 12, 14, and
16.  In particular, the prior floating-infeasible statuses at these cutoffs
cannot serve as Farkas certificates.
