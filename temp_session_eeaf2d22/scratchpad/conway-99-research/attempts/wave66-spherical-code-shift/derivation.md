# Spherical embedding, equiangular lift, and the difference lattice

Claim label: `CANDIDATE`.

Everything below is conditional on a hypothetical
\(\operatorname{srg}(99,14,1,2)\).  It does not construct or exclude the
graph.

## 1. Two primitive-idempotent spherical embeddings

The restricted eigenvalues of \(A\) are \(3\) with multiplicity \(54\) and
\(-4\) with multiplicity \(44\).  The two primitive idempotents are

\[
E_3={A+4I-\frac2{11}J\over7},\qquad
E_{-4}={-A+3I+\frac19J\over7}.
\]

After normalizing their diagonals to one, they give:

| embedding | dimension | adjacent inner product | nonadjacent inner product |
|---|---:|---:|---:|
| \(E_3\) | 54 | \(3/14\) | \(-1/21\) |
| \(E_{-4}\) | 44 | \(-2/7\) | \(1/28\) |

The second embedding can be lifted by one constant coordinate.  If its unit
vectors are \(x_i\), put

\[
y_i=\left(\sqrt{8/9}\,x_i,\;1/3\right)\in\mathbf R^{45}.
\]

Then the \(99\) unit vectors \(y_i\) are equiangular:

\[
\langle y_i,y_j\rangle=
\begin{cases}
-1/7,&i\sim j,\\
+1/7,&i\not\sim j.
\end{cases}
\]

After scaling \(w_i=\sqrt7\,y_i\), their integral Gram matrix is

\[
B=(\langle w_i,w_j\rangle)
  =6I+J-2A=7I-S.
\]

The Seidel convention here is \(S=2A-J+I\): its adjacent entries are \(+1\),
its nonadjacent entries are \(-1\), and \(S\mathbf1=-70\mathbf1\).

It has diagonal \(7\), off-diagonal entries \(\pm1\), row sum \(77\), and
spectrum

\[
77^1,\quad 14^{44},\quad0^{54}.
\]

This is a real Gram representation, not an assertion that the \(w_i\) have
integer Euclidean coordinates.

## 2. The even rank-44 difference lattice

Let \(g=\sum_iw_i\), \(c=g/99\), and

\[
u_i={w_i-c\over\sqrt2}.
\]

The \(u_i\) lie in a 44-dimensional space, sum to zero, and have centered
Gram matrix

\[
C=3I-A+\frac19J.
\]

Its nonzero eigenvalue is \(7\), with multiplicity \(44\).  Therefore

\[
\sum_i u_i u_i^{\mathsf T}=7I.
\tag{1}
\]

This centering explicitly removes the all-ones direction: \(C\mathbf1=0\),
\(C\) vanishes on the 54-dimensional eigenvalue-three space, and \(C=7I\)
on the 44-dimensional eigenvalue-minus-four space.  The claimed rank 44
therefore does not count the constant coordinate introduced by the lift.

Define

\[
M=\operatorname{span}_{\mathbf Z}\{u_i-u_j:0\le i,j<99\}.
\]

For coefficient vectors \(x,y\in\mathbf Z^{99}\) with coordinate sum zero,

\[
\left\langle\sum_i x_i u_i,\sum_i y_i u_i\right\rangle
=x^{\mathsf T}(3I-A)y.
\tag{2}
\]

Consequently \(M\) is an even integral lattice: modulo two,
\(x^{\mathsf T}(3I-A)x\equiv\sum_i x_i\equiv0\), and its real rank is \(44\).

## 3. Exact denominator bound for the dual

Take \(y\in M^*\) and set \(t_i=\langle y,u_i\rangle\).  All differences
\(t_i-t_j\) are integers.  Since \(\sum_i t_i=0\), write

\[
t_i=n_i+\frac a{99},\qquad n_i\in\mathbf Z,\qquad\sum_i n_i=-a.
\tag{3}
\]

The vector \(t\) lies in the \(-4\) eigenspace of \(A\), so

\[
(A+4I)n=-{2a\over11}\mathbf1.
\tag{4}
\]

The left side is integral; hence \(11\mid a\).  Write \(a=11b\).  The tight
frame identity (1) gives

\[
7y=\sum_i t_i u_i=\sum_i n_i u_i.
\]

Multiplying by nine and adding \(b\) to all coefficients does not change the
vector, because \(\sum_i u_i=0\), while it makes their sum zero:

\[
\sum_i(9n_i+b)=9(-11b)+99b=0.
\]

Thus

\[
\boxed{63M^*\subseteq M.}
\tag{5}
\]

In particular the discriminant group has exponent dividing \(63\).

## 4. Determinant and discriminant group

Let \(L=\operatorname{span}_{\mathbf Z}\{w_i\}\).  The difference lattice
\(D=\operatorname{span}_{\mathbf Z}\{w_i-w_j\}\) is saturated in \(L\):
every rational relation among the \(w_i\) lies in the \(3\)-eigenspace and
has coefficient sum zero.  Hence a basis of \(D\), together with \(w_0\), is
a basis of \(L\).

The projection of \(w_0\) onto \(D^\perp=\mathbf Rg\) has squared length

\[
{\langle w_0,g\rangle^2\over\langle g,g\rangle}
={77^2\over99\cdot77}={7\over9}.
\]

Since the form on \(D\) is twice the form on \(M\),

\[
\det L={7\over9}\det D
       ={7\over9}\,2^{44}\det M.
\tag{6}
\]

The product of the nonzero eigenvalues of \(B\) is
\[
77\cdot14^{44}=2^{44}7^{45}11.
\]
The top determinantal divisor \(\det L\) divides that product.  Modulo two,
\(B=J\) has rank one, so exactly 44 of its 45 nonzero Smith factors are even.
The displayed product has 2-adic valuation exactly 44, forcing
\[
v_2(\det L)=44.
\]
Equation (6) initially gives
\[
\det M=9\cdot7^a11^b
\]
for some nonnegative integers \(a\) and \(b\in\{0,1\}\).  Containment (5)
removes the prime 11 and makes every 7-primary invariant factor elementary.

It remains to count the factors at 3 and 7.

- Modulo 7, the coordinate-sum-zero space is a nondegenerate complement to
  \(\langle\mathbf1\rangle\).  On it, the form (2) is one half of
  \(B=-S\).  Hence its rank is \(r\), and \(M\) has \(44-r\) elementary
  7-factors.
- Modulo 3, (2) is the restriction of \(-A\) to the 98-dimensional
  coordinate-sum-zero space.  Its radical is
  \(\ker(A)\oplus\langle\mathbf1\rangle\), of dimension \(54+1=55\).
  Thus the form has rank \(43\).  Exactly one 3-primary factor occurs; its
  total 3-adic valuation from (6) is two, so it is \(\mathbf Z/9\).

Therefore

\[
\boxed{\det M=9\cdot7^{44-r},\qquad
M^*/M\cong\mathbf Z/9\oplus(\mathbf Z/7)^{44-r}.}
\tag{7}
\]

Here \(M^*/M\) denotes the discriminant group with the conventional
identification of \(M\) inside \(M^*\).

## 5. Milgram forces an even characteristic-seven rank

The lattice \(M\) is positive definite of rank and signature 44.  Apply
Milgram's formula to its finite quadratic form:

\[
|M^*/M|^{-1/2}\sum_{x\in M^*/M}e^{2\pi iQ(x)}
=e^{2\pi i\,44/8}=-1.
\tag{8}
\]

For every nondegenerate quadratic form on the cyclic group \(\mathbf Z/9\),
the normalized quadratic Gauss sum is \(+1\).  The elementary 7-primary part
has dimension
\[
q=44-r.
\]
After diagonalization over \(\mathbf F_7\), its normalized Gauss sum is
\[
\delta\,i^q,\qquad \delta\in\{+1,-1\},
\]
because \(7\equiv3\pmod4\).  It can equal the required real phase \(-1\)
only if \(q\) is even.  Hence

\[
\boxed{r\equiv0\pmod2.}
\tag{9}
\]

There is one zero-dimensional exception.  If \(q=0\), the 7-primary group is
absent and its Gauss phase is fixed at \(+1\), not an adjustable
\(\delta\).  The remaining \(\mathbf Z/9\) phase \(+1\) contradicts the
required phase \(-1\).  Thus \(q>0\), and

\[
\boxed{r\le42.}
\tag{10}
\]

For positive even \(q\), either determinant sign is available.  The required
7-primary sign is
\[
\delta=-i^{-q}=(-1)^{q/2+1}.
\]
Thus this group-level calculation gives no further rank exclusion.  Within
the imported interval, the surviving ranks are
\[
28,30,32,34,36,38,40,42.
\]
All surviving cases have exact discriminant-form level
\(\operatorname{lcm}(9,7)=63\).

## 6. The dual has minimum at least two

By (1),

\[
7\|y\|^2=\sum_i t_i^2.
\tag{11}
\]

Choose \(0\le a<99\) in (3).  Since \(11\mid a\), there are two cases.

### Nonintegral cosets

For fixed \(a\), the least possible squared norm under (3), without the
eigenvector equation, is

\[
\sum_i t_i^2\ge {a(99-a)\over99}.
\tag{12}
\]

For \(a=22,\ldots,77\) in steps of 11, this is at least \(154/9>14\).
The cases \(a=11\) and \(a=88\) are negatives of one another.  Take \(a=11\).
Then (4) is

\[
(A+4I)n=-2\mathbf1,\qquad \sum_i n_i=-11.
\tag{13}
\]

Let \(P\) be the sum of the positive entries of \(n\).  There must be a
positive entry: otherwise, at a negative coordinate \(n_v=-m\), equation
(13) requires the positive neighbor sum
\((An)_v=4m-2\).  The same coordinate argument gives \(P\ge2\).
The total negative mass is \(P+11\), so

\[
\sum_i n_i^2\ge P+(P+11)\ge15.
\]

Equality would force exactly two \(+1\)'s and thirteen \(-1\)'s.  Every
negative vertex would then have to see both positive vertices and no negative
one, making each positive vertex see all thirteen negatives; its required
neighbor sum is instead \(-6\).  Hence equality is impossible.  Parity gives
\(\sum n_i^2\equiv\sum n_i\pmod2\), so
\[
\sum_i n_i^2\ge17.
\]
Therefore
\[
\sum_i t_i^2=\sum_i n_i^2-\frac{11}{9}
\ge\frac{142}{9}>14.
\]

### Integral coset

Now \(a=0\), so \(t=n\in\mathbf Z^{99}\), \(\sum n_i=0\), and
\(An=-4n\).  Divide by a common power of two.  For the resulting primitive
integer vector, its odd support is a nonzero word of
\(\ker_{\mathbf F_2}(A)\), hence has size at least eight.  If
\(\sum n_i^2<14\), parity and the zero coordinate sum leave only:

1. eight entries \(\pm1\);
2. ten entries \(\pm1\);
3. twelve entries \(\pm1\); or
4. eight odd entries \(\pm1\) and one even entry \(\pm2\).

The imported weight-eight support theorem excludes cases 1 and 4: the eight
odd vertices are independent, so at such a vertex the neighbor sum is,
respectively, \(0\) or one of \(0,\pm2\), never the required \(\pm4\).

For ten \(\pm1\) entries, zero sum gives five of each sign.  The eigenvector
equation says that every support vertex has four more opposite-sign than
same-sign neighbors.  If \(h\) is the number of same-sign edges in either
sign class, the induced edge count is \(20+4h\).  The standard positive
restricted-eigenvalue bound gives at most 20 edges on ten vertices, so
\(h=0\).  The support would be a 4-regular bipartite graph on \(5+5\)
vertices, necessarily \(K_{5,5}\) minus a perfect matching.  Two vertices
on one side then have at least three common neighbors, contradicting
\(\mu=2\).

For twelve \(\pm1\) entries, the same argument gives six of each sign and
\(24+4h\) induced edges.  The spectral bound is at most 26, so \(h=0\).
The support would be 4-regular bipartite on \(6+6\).  Counting common
neighbors of pairs in one part gives
\[
6\binom42=36,
\]
but the 15 nonadjacent pairs can have at most \(15\mu=30\), a contradiction.

Thus every nonzero integral coset has \(\sum t_i^2\ge14\).  Together with
the nonintegral cases and (11),

\[
\boxed{\min(M^*)\ge2.}
\tag{14}
\]

Equality, if it occurs, must come from an integral \(-4\)-eigenvector of
Euclidean squared norm 14.  This turns the next step into a finite
short-vector/code problem rather than another pair-coordinate linear
relaxation.

## 7. Geometry-of-numbers cross-check

The standard Blichfeldt bound
\[
\gamma_{44}\le {2\over\pi}\Gamma(24)^{1/22}
\]
combined with \(\min(M^*)\ge2\) gives
\[
\det M\le\left({\gamma_{44}\over2}\right)^{44}
={23!^2\over\pi^{44}}.
\]
Using (7), this implies only \(r\ge18\).  The row \(r=18\) still passes the
same numerical inequality, and the imported verified bound \(r\ge28\) is
strictly stronger.  This calculation is retained as a hostile scale check,
not promoted as progress on the endpoint.

## 8. Exact boundary

For the currently verified \(28\le r\le44\), the Milgram condition leaves
eight determinant rows:

\[
9\cdot7^2,\;9\cdot7^4,\;\ldots,\;9\cdot7^{16}.
\]
They remain arithmetically possible.  No lattice in this package is constructed,
and no row is excluded by a complete genus or theta-series classification.
The Conway graph remains `UNKNOWN`; novelty remains `UNKNOWN`.
