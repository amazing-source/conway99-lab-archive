# Derivation: Schur closure, exterior Smith form, and orthogonal orbits

Claim label: `DERIVED` discovery, conditional on the frozen verified
imports.

## 1. Schur closure of the Seidel hull

Reduce \(S\) modulo seven and put
\[
R=\operatorname{row}_{\mathbf F_7}(S).
\]
Since \(S^2=0\) modulo seven and \(S\) is symmetric, \(R\) is
self-orthogonal. Therefore every coordinatewise product of two words in
\(R\) has coordinate sum zero:
\[
R*R\subseteq\mathbf1^\perp.
\tag{1}
\]

Let \(s_i\) be row \(i\) of \(S\). Its diagonal coordinate is zero and all
other coordinates are \(+1\) or \(-1\). Hence
\[
s_i*s_i=\mathbf1-e_i.
\tag{2}
\]
The 99 vectors in (2) are the rows of \(J-I\). Since
\[
99\equiv1\pmod7,
\]
\(J-I\) has kernel \(\langle\mathbf1\rangle\) and rank 98. Equations
(1)--(2) prove
\[
\boxed{R*R=\mathbf1^\perp.}
\tag{3}
\]

The full third product follows constructively. Fix a coordinate \(i\) and
choose \(j\ne i\). By (3), \(e_i-e_j\in R*R\), while
\[
s_j*(e_i-e_j)=S_{ji}e_i-S_{jj}e_j=S_{ji}e_i.
\]
The coefficient \(S_{ji}\) is nonzero, so \(e_i\in R*R*R\). This holds for
every \(i\), giving
\[
\boxed{R*R*R=\mathbf F_7^{99}.}
\tag{4}
\]

At rank 28 the evaluation algebra therefore has Hilbert function
\[
H(0),H(1),H(2),H(3)=(1,28,98,99)
\]
and first-difference vector
\[
(1,27,70,1).
\]

Wave 51 already proved that the 99 pure quadratic images span a
98-dimensional space and have the displayed all-one relation. Equation
(3) packages this as an equality of Schur codes. Its dual is
\(\langle\mathbf1\rangle\), so the 99 quadratic Veronese images have one
linear relation, with every coefficient nonzero. Any 98 of them are
independent. Equivalently, the point set has the degree-two
Cayley--Bacharach property.

The 44-dimensional evaluation code \(C\) contains \(R\). Since \(C/R\) is
nondegenerate, some \(c,d\in C\) have \(c\cdot d\ne0\). The coordinate sum
of \(c*d\) is \(c\cdot d\), so \(c*d\notin\mathbf1^\perp\). Together with
(3), this proves
\[
\boxed{C*C=\mathbf F_7^{99}.}
\tag{5}
\]
These equalities are saturation statements, not contradictions.

## 2. The exterior-square matrix

Index rows and columns by two-subsets of the 99 vertices and define the
second compound
\[
E=C_2(S),\qquad
E_{I,J}=\det S[I,J].
\tag{6}
\]
It has order
\[
\binom{99}{2}=4851.
\]
Because \(S\) is symmetric, so is \(E\). Cauchy--Binet gives
\[
E^2=C_2(S^2)=2401\,C_2(I+J),
\tag{7}
\]
and hence \(E^2=0\) modulo seven.

For a linear map of rank \(r\), its second exterior power has rank
\(\binom r2\). Therefore
\[
\operatorname{rank}_{\mathbf F_7}E=\binom r2.
\tag{8}
\]
At \(r=28\), the row code of \(E\) is a self-orthogonal
\[
[4851,378]_7
\]
code.

The compound columns are wedges of pairs of columns of \(S\). Wave 80's
\(d(R^\perp)\ge6\) says every set of at most five columns of \(S\) is
independent. In particular every two-column wedge is nonzero. If two
distinct wedges were proportional, their underlying two-planes would
coincide, making the union of at most four columns dependent. Thus the
4,851 compound columns are projectively distinct and
\[
d(\operatorname{row}(E)^\perp)\ge3.
\tag{9}
\]

## 3. Exact distinguished row weight

Fix a pair \(\{a,b\}\). The diagonal entry of its compound row is
\[
\det\begin{pmatrix}0&S_{ab}\\S_{ab}&0\end{pmatrix}=-1.
\]
There are \(2(99-2)=194\) other pairs sharing one vertex, and every
corresponding minor is \(+1\) or \(-1\).

For a disjoint pair \(\{c,d\}\), the minor vanishes precisely when
\[
\frac{S_{ac}}{S_{bc}}=\frac{S_{ad}}{S_{bd}}.
\tag{10}
\]
If \(a,b\) are adjacent, the remaining 97 vertices split into
\[
1,\ 12,\ 12,\ 72
\]
according to adjacency to both, only \(a\), only \(b\), or neither. The two
ratio classes in (10) consequently have sizes 73 and 24. If \(a,b\) are
nonadjacent, the four counts are
\[
2,\ 12,\ 12,\ 71,
\]
giving the same ratio-class sizes. Thus exactly
\[
73\cdot24=1752
\]
disjoint-pair entries are nonzero and
\[
\binom{97}{2}-1752=2904
\]
are zero. Every distinguished compound row has weight
\[
\boxed{1+194+1752=1947.}
\tag{11}
\]
Its integral square norm is
\[
1+194+4(1752)=7203=3\cdot2401,
\]
consistent with (7). Projectivity supplies 4,851 distinguished lines and
29,106 scalar-closed weight-1,947 codewords.

## 4. Complete exterior Smith form

The verified conditional Smith form of \(S\) has 7-adic exponents
\[
0^r,\quad1^{99-2r},\quad2^r.
\tag{12}
\]
Applying the second exterior-power functor to a Smith equivalence gives all
pairwise sums of the prime-adic exponents. Put \(b=99-2r\). The 7-adic
multiplicities for \(E\) are
\[
\begin{array}{c|ccccc}
\text{exponent}&0&1&2&3&4\\ \hline
\text{multiplicity}&
\binom r2&rb&r^2+\binom b2&rb&\binom r2.
\end{array}
\tag{13}
\]

The unique factor 490 in the Smith form of \(S\) carries the only factors
2 and 5. Exactly 98 exterior pairs use that factor, so the sorted 2-adic
and 5-adic exponent lists each end with 98 ones. For every live
\(r\ge28\), \(\binom r2\ge98\), and these factors align with the last 98
7-adic exponent-four positions. Consequently
\[
\boxed{
\begin{aligned}
\operatorname{SNF}(E)=\operatorname{diag}(&
1^{\binom r2},
7^{rb},
49^{r^2+\binom b2},
343^{rb},\\
&2401^{\binom r2-98},
24010^{98}).
\end{aligned}}
\tag{14}
\]
At \(r=28,b=43\), this becomes
\[
\boxed{
\operatorname{diag}(
1^{378},7^{1204},49^{1687},343^{1204},
2401^{280},24010^{98}).
}
\tag{15}
\]

As determinant controls, the prime valuations are
\[
v_2(\det E)=98,\quad v_5(\det E)=98,\quad
v_7(\det E)=98\cdot99=9702.
\]

The rational eigenvalues of \(S\) are
\[
-70^1,\quad 7^{54},\quad(-7)^{44}.
\]
Taking pairwise products gives the exact spectrum
\[
490^{44},\quad(-490)^{54},\quad
49^{2377},\quad(-49)^{2376}.
\tag{16}
\]
Its trace is \(-4851\), agreeing with the constant diagonal \(-1\).

## 5. Generalized Hamming weights

At rank 28, \(R^\perp\) is a \([99,71]_7\) code. If a coordinate set has
matroid nullity \(j\ge1\), it contains a circuit. Since every five columns
are independent, that circuit has rank at least five. Hence its size is at
least
\[
\boxed{d_j(R^\perp)\ge j+5.}
\tag{17}
\]
The generalized Singleton bound supplies
\[
d_j(R^\perp)\le28+j.
\tag{18}
\]
The forced Wave 80 short word only narrows the first value to
\[
6\le d_1(R^\perp)\le18.
\]
These intervals are consistent for every \(j\); they do not exclude the
matroid.

## 6. Orthogonal orbit reduction

At rank 28, Wave 80 gives
\[
O^-(42,7)=O^-(16,7)\perp O^+(26,7).
\]
Witt extension implies that all nondegenerate minus-type 16-subspaces with
this complement form one orbit under \(O^-(42,7)\). Its exact size is
\[
\frac{|O^-(42,7)|}{|O^-(16,7)|\,|O^+(26,7)|},
\tag{19}
\]
the 352-digit integer recorded in `exact-results.json`.

Inside \(O^-(16,7)\), the projective point orbits have sizes
\[
\begin{array}{c|c}
\text{type}&\text{number of projective points}\\ \hline
\text{isotropic}&(7^7-1)(7^8+1)/6\\
\text{square anisotropic}&(7^{15}+7^7)/2\\
\text{nonsquare anisotropic}&(7^{15}+7^7)/2.
\end{array}
\tag{20}
\]
The norm-14 word has self-dot zero and may map to zero or the isotropic
orbit. Norms 16 and 18 have self-dots 4 and 1. Both are nonzero squares, so
they occupy the same square-anisotropic projective orbit.

Thus abstract orthogonal geometry loses the distinction between the
norm-16 and norm-18 branches. A successful continuation must retain the
coordinate alphabet, weight, or marked Seidel hull.

## 7. Exact boundary

Wave 97 supplies a new 4,851-coordinate exterior code and its complete
conditional Smith form, but all eight rank rows survive. The Schur algebra
is already saturated in degree three, generalized-weight bounds have slack,
and the orthogonal group is transitive on the relevant embeddings.

```text
rank r=28 excluded:                  NO
strict n3 upper bound below 4158:   NOT PROVED
Conway-99:                          UNKNOWN
novelty:                            UNKNOWN
```
