# Independent packing derivation

Claim label: `VERIFIED`, conditional on the Wave 71 signed-unit support
reduction and the Wave 74 verified support-incidence equations.

## 1. Frozen conditional setup

Let \(G\) be an \(\operatorname{srg}(99,14,1,2)\). Conditionally assume the
Wave 71 signed support \(P\sqcup N\) and the Wave 74 equations. An outside
vertex \(x\) has
\[
d=|N(x)\cap P|=|N(x)\cap N|.
\]
For a support vertex \(p\), write
\[
R_p=N(p)\cap N
\]
when \(p\in P\), and use the symmetric definition when \(p\in N\).

If two distinct vertices \(p,q\) on one sign side are both adjacent to
\(x\), then \(x\) is already a common neighbor. If \(p,q\) are nonadjacent,
they have exactly \(\mu=2\) common neighbors, so
\[
|R_p\cap R_q|\leq1.
\]
If they are adjacent, they have exactly \(\lambda=1\) common neighbor, so
the sharper bound \(|R_p\cap R_q|=0\) holds. Thus every selected family of
opposite-support neighborhoods is linear: every two blocks intersect in at
most one point.

## 2. A multiplicity proof of the packing bound

Consider \(k\) blocks and, for each point \(y\) in their union, let \(m_y\)
be the number of blocks containing \(y\). Then
\[
\sum_y \binom{m_y}{2}
=\sum_{i<j}|R_i\cap R_j|
\leq \binom{k}{2}.
\]
For every integer \(m\geq1\),
\[
m-1\leq\binom m2.
\]
Therefore, if every block has size four,
\[
4k-\left|\bigcup_iR_i\right|
=\sum_y(m_y-1)
\leq\sum_y\binom{m_y}{2}
\leq\binom k2. \tag{1}
\]

For norm 16, three selected vertices would give \(k=3\), so (1) forces a
union of at least \(12-3=9\) points. The opposite sign side has only eight
points. Hence
\[
\boxed{d\leq2\quad\text{in norm 16}.}
\]

For norm 18, four selected vertices would give \(k=4\), so (1) forces a
union of at least \(16-6=10\) points. The opposite sign side has only nine
points. Hence
\[
\boxed{d\leq3\quad\text{in norm 18}.}
\]

This multiplicity argument also closes a possible gap in a bare
inclusion-exclusion slogan: it handles triple and quadruple intersections
without assuming that alternating higher-order terms have a favorable sign.

## 3. Equality rigidity on nine points

Suppose three four-subsets fit on exactly nine points. Equality must hold in
both inequalities used in (1). Consequently:

1. the sum of the three pair intersections is exactly three, so every pair
   intersects in exactly one point;
2. \(m_y-1=\binom{m_y}{2}\) for every used point, which excludes \(m_y\geq3\).

Thus the three pair-intersection points are distinct, the triple
intersection is empty, and the union is the whole nine-point side. The
independent enumerator finds exactly 7,560 unordered linear triples of
four-subsets on a labelled nine-point set, and every one has precisely this
rigid profile. It also confirms that no such triple fits on eight points and
no four-block family fits on nine points.

## 4. The norm-18 \(h=1\) endpoint obstruction

On either sign side, the two endpoints of the unique same-sign edge have
opposite-support degree five; each of the other seven support vertices has
opposite-support degree four.

Let a \(d=3\) outside block select three vertices on one sign side. If it
selected even one endpoint, its three opposite-support neighborhoods would
have total incidence at least
\[
5+4+4=13.
\]
The three pair intersections have total size at most three. The same
multiplicity inequality used above therefore gives union size at least
\(13-3=10\), impossible on nine points. If both endpoints were selected,
their pair intersection would actually be zero because \(x\) has already
used the unique common-neighbor allowance for that adjacent pair.

Therefore every \(d=3\) outside block avoids both endpoints of the unique
same-sign edge, on each sign side.

## 5. Independent histogram enumeration

Write \(n_j=|\{x:d_x=j\}|\). The Wave 74 verified moments are:

| lane | \(\sum n_j\) | \(\sum jn_j\) | \(\sum\binom j2n_j\) | packing |
|---|---:|---:|---:|---:|
| norm 16, \(h=0\) | 83 | 80 | 8 | \(j\leq2\) |
| norm 18, \(h=0\) | 81 | 90 | 18 | \(j\leq3\) |
| norm 18, \(h=1\) | 81 | 86 | 9 | \(j\leq3\) |

The verifier exhausts the bounded nonnegative integer values of
\(n_2,\ldots,n_{\max}\), then uniquely solves for \(n_1,n_0\). It obtains
exactly:

- norm 16: one row, \((11,64,8)\);
- norm 18, \(h=0\): seven rows,
  \((3,72,0,6)\) through \((9,54,18,0)\);
- norm 18, \(h=1\): four rows,
  \((1,77,0,3)\) through \((4,68,9,0)\).

All 1, 7, and 4 rows exactly equal the frozen discovery JSON.

## 6. Boundary

These are necessary packing and scalar-moment conditions. The rows are not
labelled incidence systems and do not prove that a compatible strongly
regular graph exists. The \(h=1\), \(d=3\) endpoint-avoidance rule is extra
structure not represented by the scalar histograms. Norm 14 and the
remaining norm-16/norm-18 alternatives survive. No automorphism is assumed.
Conway-99 and novelty remain `UNKNOWN`.
