# Wave 66 hostile controls

These controls are part of the discovery package.  They make likely
factor/sign/saturation failures explicit for an independent verifier.

## Seidel sign

The package fixes
\[
S=2A-J+I.
\]
Thus adjacent entries are \(+1\), nonadjacent entries are \(-1\), and the
spectrum is
\[
-70^1,\quad 7^{54},\quad(-7)^{44}.
\]
The earlier reversed multiplicities rejected in the Wave 51 audit are not
reused.  With this convention, \(B=7I-S=6I+J-2A\) has spectrum
\(77^1,0^{54},14^{44}\).

## Constant-coordinate contamination

Before centering, \(B\) has rank 45.  After subtracting its centroid and
halving,
\[
C=3I-A+J/9
\]
has eigenvalues \(0\) on both the all-ones direction and the
54-dimensional eigenvalue-three space, and eigenvalue seven only on the
44-dimensional eigenvalue-minus-four space.  Any rank-45 result for \(M\)
is rejected.

## Factor of two

The scaled equiangular vectors have norm seven and pairwise products
\(-1\) on graph edges and \(+1\) on nonedges.  Therefore
\[
{1\over2}\|w_i-w_j\|^2=7-\langle w_i,w_j\rangle
\in\{8,6\}.
\]
For arbitrary zero-sum integer coefficient vectors, the halved form is
exactly \(3I-A\), not \(6I-2A\).  Omitting this division would multiply the
rank-44 determinant by \(2^{44}\).

## Saturation of the difference lattice

If \(q w_0\) is an integer combination of differences, it supplies an
integer relation among all \(w_i\) with coefficient sum \(q\).  Every
rational relation belongs to \(\ker B\), the eigenvalue-three space of \(A\),
which is orthogonal to \(\mathbf1\).  Hence \(q=0\).  Thus \(L/D\) is
torsion-free, and the basis-plus-height determinant calculation has no hidden
square index.

An independent verifier should attack this step by reconstructing the top
determinantal-divisor formula rather than trusting the prose.

## Determinant exponents

The checks that separately pin the answer are:

1. \(B\bmod2=J\), so 44 of the 45 nonzero Smith factors are even.
2. The nonzero pseudodeterminant has 2-adic valuation exactly 44.
3. The projection height is \(7/9\).
4. \(63M^*\subseteq M\), removing prime 11 and limiting local exponents.
5. The form has rank 43 modulo 3 and rank \(r\) modulo 7.

Together these give one factor \(\mathbf Z/9\) and exactly \(44-r\)
elementary factors \(\mathbf Z/7\).  Mutations \(7^{45-r}\),
\(\mathbf Z/3\oplus\mathbf Z/3\), and a retained 11-factor are rejected.

## Milgram phase

The rank-44 positive signature requires phase \(-1\).  The cyclic
9-primary form contributes \(+1\); an elementary 7-primary form of positive
dimension \(q\) contributes \(\delta i^q\).  Odd \(q\) is rejected.  The case
\(q=0\) is also rejected because the absent 7-part has fixed phase \(+1\),
not an adjustable sign.  This control narrows the imported interval to even
\(r\le42\); for positive even \(q\) it fixes the 7-primary determinant sign
to \((-1)^{q/2+1}\).

## Dual-minimum prerequisites

The proof of \(\min(M^*)\ge2\) imports all three Wave 2 binary facts, not only
the rank:

- \(\ker_{\mathbf F_2}(A)\) has minimum weight at least eight;
- a weight-eight support is independent;
- every vertex meets that support in zero or two points.

It then separately excludes primitive integral squared norms:

- 8: independent weight-eight support;
- 10: forced \(K_{5,5}\) minus a matching, violating \(\mu=2\);
- 12: either the weight-eight-plus-\(\pm2\) case, or a forced 4-regular
  bipartite graph on \(6+6\) whose same-side common-neighbor count is
  \(36>30\).

For nonintegral dual cosets, the eigenvalue equation forces the common
fractional numerator to be a multiple of 11.  The only small cosets
\(a=11,88\) require an integer vector of squared norm at least 17, which is
enough.  Dropping any one of these prerequisites invalidates the stated
minimum proof.
