# The characteristic-seven evaluation code

Claim label: `DERIVED` (discovery; independent verification required).

Everything is conditional on the frozen Wave 66 and Wave 71 imports and a
hypothetical \(\operatorname{srg}(99,14,1,2)\).

## 1. The marked vectors span modulo seven

Put
\[
N=\langle v_0,\ldots,v_{98}\rangle_{\mathbf Z}\subseteq L.
\]
Because \(v_i-v_j=3(u_i-u_j)\), one has \(3M\subseteq N\), while
\(v_0\in N\) and \(L=M+\mathbf Zv_0\).  Every class in \(L/N\) is therefore
killed by three.  Since seven is invertible on this finite 3-primary
quotient,
\[
\boxed{N+7L=L.}
\tag{1}
\]
In particular the \(v_i\) span \(L/7L\) over \(\mathbf F_7\).  This step is
what makes the evaluation map faithful; the frame identity alone would not.

Define
\[
\Phi:L^*/7L^*\longrightarrow\mathbf F_7^{99},\qquad
\Phi(y)=(\langle y,v_i\rangle\bmod7)_i.
\tag{2}
\]
If \(\Phi(y)=0\), then (1) gives
\(\langle y,L\rangle\subseteq7\mathbf Z\).  Hence \(y/7\in L^*\), so
\(y\in7L^*\).  Thus \(\Phi\) is injective and
\[
\boxed{C=\operatorname{im}\Phi\text{ is a }[99,44]_7\text{ code}.}
\tag{3}
\]
The exact relation \(\sum_i v_i=0\) also gives
\[
C\subseteq\mathbf1^\perp.
\tag{4}
\]

## 2. The code form, radical, and Seidel row space

On \(L^*/7L^*\), define
\[
\beta(\bar y,\bar z)=7\langle y,z\rangle\pmod7.
\tag{5}
\]
This is well defined because \(7L^*\subseteq L\).  Its radical consists
exactly of the classes of \(L\):
\[
\operatorname{rad}\beta=L/7L^*.
\tag{6}
\]
Indeed, \(\beta(y,L^*)=0\) says
\(\langle y,L^*\rangle\subseteq\mathbf Z\), which is equivalent to
\(y\in(L^*)^*=L\).  Since
\[
[L^*:7L^*]=7^{44},\qquad [L^*:L]=7^q,
\]
the radical has dimension \(44-q=r\).

The tight-frame identity now computes the ordinary code dot product:
\[
\begin{aligned}
\Phi(y)\cdot\Phi(z)
&=\sum_i\langle y,v_i\rangle\langle z,v_i\rangle\\
&=63\langle y,z\rangle\\
&=9\bigl(7\langle y,z\rangle\bigr)
\equiv2\beta(\bar y,\bar z)\pmod7.
\end{aligned}
\tag{7}
\]
Thus the radical of the restricted code dot product is the image of
\(L/7L^*\).

The integral Gram matrix of the marked vectors is
\[
G=27I+J-9A.
\tag{8}
\]
Modulo seven,
\[
G\equiv6I+J-2A=-S.
\tag{9}
\]
By (1), the images of the \(v_i\) span \(L/7L^*\); their evaluation words
are the rows of \(G\).  Consequently
\[
\boxed{
  C\cap C^\perp
  =\operatorname{rad}(C)
  =\operatorname{row}_{\mathbf F_7}(S),
  \qquad\dim(C\cap C^\perp)=r.
}
\tag{10}
\]
This identifies the hull, rather than merely placing the Seidel row space
inside it.

## 3. The orthogonal quotient

Let
\[
R=\operatorname{row}_{\mathbf F_7}(S).
\]
The exact Seidel spectrum gives \(S^2=49(I+J)\), so \(S^2=0\) over
\(\mathbf F_7\).  Hence \(R\) is totally isotropic and
\[
C\subseteq R^\perp=\ker S.
\]
The quotient
\[
W=R^\perp/R
\tag{11}
\]
is nondegenerate and has dimension
\[
\dim W=99-2r=11+2q.
\]
The all-one vector belongs to \(\ker S\), has norm
\(\mathbf1\cdot\mathbf1=99=1\pmod7\), does not belong to \(R\), and is
orthogonal to \(C\).  Its complement
\[
W_0=\mathbf1^\perp\cap W
\tag{12}
\]
has dimension \(10+2q\).

The quotient \(C/R\) is canonically \(L^*/L\) with bilinear form \(2\beta\),
so it is nondegenerate of dimension \(q\).  Wave 66's Milgram sign is
\[
\left({\det(C/R)\over7}\right)=(-1)^{q/2+1}.
\tag{13}
\]
The factor two in (7) does not change this square class because \(q\) is
even.  For a \(2m\)-dimensional quadratic space over \(\mathbf F_7\), the
split determinant class is \((-1)^m\).  Equation (13) is the opposite
class, and therefore
\[
\boxed{C/R\cong O^-(q,7),\qquad\text{Witt index }q/2-1.}
\tag{14}
\]

Removing \(r\) hyperbolic planes from the standard
\(\mathbf F_7^{99}\) form shows that \(W\) has square determinant
(\(r\) is even).  Removing the norm-one vector preserves that square class.
It follows that
\[
\boxed{
W_0\cong O^-(10+2q,7),\qquad
(C/R)^\perp_{W_0}\cong O^+(10+q,7).
}
\tag{15}
\]

At the difficult \(r=28,q=16\) row, the exact code geometry is
\[
\boxed{
\begin{array}{c}
C:[99,44]_7,\quad\dim\operatorname{Hull}(C)=28,\\
C/R\cong O^-(16,7)\ \text{(Witt index 7)},\\
W_0\cong O^-(42,7),\quad
(C/R)^\perp_{W_0}\cong O^+(26,7).
\end{array}}
\tag{16}
\]

## 4. A new small-support consequence: \(d(C^\perp)\ge6\)

Every column of \(S\) is nonzero, so \(R^\perp\) has no word of weight one.
If a word of \(R^\perp\) has support \(I\), its nonzero coefficients give
a full-support vector in the kernel of the principal matrix \(S[I,I]\).

For \(|I|=2,3,4\), every zero-diagonal sign matrix with off-diagonal entries
\(\pm1\) is nonsingular modulo seven.  The exact determinant residue sets
are respectively
\[
\{6\},\qquad\{2,5\},\qquad\{4,5\}.
\tag{17}
\]

At \(|I|=5\), `exact_check.py` exhausts all \(2^{10}=1024\) labelled
graphs.  An induced subgraph of the target must have at most one common
neighbor inside the set for an adjacent pair, and at most two for a
nonadjacent pair.  Exactly 683 labelled graphs pass these necessary
\((\lambda,\mu)\) controls.  Among them, 132 have a full-support Seidel
kernel; they form three isomorphism types:

| type | degree sequence | coefficient pattern up to scalar | labelled copies |
|---|---|---|---:|
| \(P_4\sqcup K_1\) | \(0,1,1,2,2\) | three \(+1\), two \(-1\) | 60 |
| triangle with two separate leaves | \(1,1,2,3,3\) | four \(+1\), one \(-1\) | 60 |
| \(C_5\) | \(2,2,2,2,2\) | five \(+1\) | 12 |

For a putative kernel vector \(x\) on \(I\), every outside vertex with
incidence pattern \(p\in\{0,1\}^5\) must satisfy
\[
2\sum_{i\in I}p_ix_i=\sum_{i\in I}x_i\pmod7.
\tag{18}
\]
No \(0/1\) pattern satisfies (18) in any of the three cases.  This is also
checked for all 132 labelled projective relations.  Since a five-set has 94
outside vertices, no such support can occur.  Therefore
\[
d(R^\perp)\ge6.
\]
Because \(R\subseteq C\), one has \(C^\perp\subseteq R^\perp\), and hence
\[
\boxed{d(C^\perp)\ge6.}
\tag{19}
\]
Equivalently, \(C\) is an orthogonal array of strength five.  This conclusion
uses no graph automorphism and no unbounded search.

## 5. The Wave 71 short vectors inside the code

For a Wave 71 short vector \(z=\sqrt7\,y\in K\), the integral eigenvector
coordinates satisfy
\[
t_i=\langle y,u_i\rangle\in\{0,+1,-1\}
\]
at squared norms \(14,16,18\), with equally many plus and minus signs.
Evaluation gives
\[
\Phi(y)=3t\pmod7.
\tag{20}
\]
The three exact symbol compositions and self-dots are

| \(\|z\|^2\) | code weight | symbols \(3,4\) | code self-dot |
|---:|---:|---:|---:|
| 14 | 14 | \(7,7\) | \(0\) |
| 16 | 16 | \(8,8\) | \(4\) |
| 18 | 18 | \(9,9\) | \(1\) |

The self-dot formula is simply
\[
\Phi(y)\cdot\Phi(y)=9\sum_i t_i^2=2\|z\|^2\pmod7.
\tag{21}
\]
Thus norm 14 gives an isotropic or zero class in \(C/R\), while norms 16
and 18 give anisotropic classes.  A minus-type 16-space has seven
hyperbolic planes, so it represents zero and every nonzero field value.
The orthogonal type therefore excludes none of the three alternatives.

The low-norm dictionary is injective after reduction modulo seven: two
\(\{0,\pm1\}\)-vectors congruent modulo seven are equal.  Only the scalars
\(\pm1\) preserve the alphabet \(\{0,\pm3\}\), so every pair \(\{\pm t\}\)
determines one projective code line and its six nonzero scalar multiples.
Wave 71's congruence consequently supplies a scalar-closed subset of
short-weight codewords of cardinality
\[
3(N_{14}+N_{16}+N_{18})\equiv6\pmod{42},
\tag{22}
\]
and in particular at least six codewords of weights \(14,16,18\).

## 6. MacWilliams boundary

The 99 Seidel rows are pairwise projectively distinct and have weight 98.
Their scalar multiples give 594 mandatory weight-98 codewords in \(C\).
Together with one minimally forced short projective line, these data do not
overfill any of the orthogonal-array moments through strength five:
\[
\sum_{c\in C}\binom{\operatorname{wt}(c)}j
=\binom{99}j6^j7^{44-j},
\qquad0\le j\le5.
\tag{23}
\]
`exact-results.json` records strict positive slack in all six equations,
even when every one of the six minimally forced short words is assigned
weight 18 to maximize its contribution.

This is a hostile null control only.  Positive slack does not construct the
remaining weight distribution, an integral MacWilliams enumerator, or a
code.  The hull and orthogonal-type information is not captured by the
ordinary univariate enumerator.

## 7. Exact boundary

The finite-field shift is exact and retains more of the lattice than an
ordinary Seidel row code:

- its dimension is fixed at 44;
- its hull is exactly the rank-\(r\) Seidel row space;
- the discriminant form becomes the non-split quotient \(O^-(q,7)\);
- at rank 28 the forced short lattice vector becomes a sparse balanced code
  line in one of three weights;
- the dual distance is at least six.

The rank-28 row nevertheless survives all these conditions.  No formal
complete enumerator, code, graph, or contradiction is constructed.
Conway-99 and novelty remain `UNKNOWN`.
