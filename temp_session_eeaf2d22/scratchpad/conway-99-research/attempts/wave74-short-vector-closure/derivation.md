# Outside-incidence closure for the signed short-vector supports

Claim label: `DERIVED` (discovery; independent verification required).

## 1. Uniform equations

Let \(P,N\) be the positive and negative unit supports, each of size \(s\).
Let \(h\) be the number of same-sign edges in each side.  Wave 71 proves
\[
e(P,N)=4s+2h.
\tag{1}
\]
The support degree incidences from one sign side are therefore
\[
2h+e(P,N)=4s+4h.
\]
Since every graph vertex has degree 14, the number of incidences from one
side to the outside set \(X=V\setminus(P\cup N)\) is
\[
\boxed{\sum_{x\in X}d_x=14s-(4s+4h)=10s-4h,}
\tag{2}
\]
where the eigenvector equation at a zero coordinate gives
\[
d_x=|N(x)\cap P|=|N(x)\cap N|.
\tag{3}
\]
There are \(99-2s\) outside vertices.

For unordered pairs in one sign side, the total SRG common-neighbor capacity
is
\[
h\lambda+\left(\binom s2-h\right)\mu=s(s-1)-h.
\tag{4}
\]
A support vertex of same-sign degree \(r\) has opposite-sign degree \(4+r\).
Thus common-neighbor incidences through the opposite support side total
\[
\sum_{v\in N}\binom{4+r_v}{2}.
\tag{5}
\]
For \(h=0\), \(h=1\), and two disjoint same-sign edges, (5) is respectively
\[
6s,\qquad 6s+8,\qquad 6s+16.
\tag{6}
\]
There are no same-side support triangles in these three shapes.  Subtracting
(5) from (4) gives the exact outside-pair moment
\[
\boxed{\sum_{x\in X}\binom{d_x}{2}
=s(s-1)-h-\sum_{v\in N}\binom{4+r_v}{2}.}
\tag{7}
\]

Finally, \(x\) has \(2d_x\) support neighbors, hence outside degree
\(14-2d_x\).  Therefore the induced outside edge count is
\[
e(X)=\frac{14|X|-2\sum_xd_x}{2}=7|X|-\sum_xd_x.
\tag{8}
\]

## 2. Norm 18, \(h=2\), is impossible

If the two same-sign edges share an endpoint, Wave 71 already gives
\[
\sum_{v\in N}\binom{4+r_v}{2}=71
>70=s(s-1)-h.
\]
Thus the two edges must be disjoint on each side.

For \(s=9,h=2\), equations (2), (4), and (6) give
\[
|X|=81,\qquad
\sum_{x\in X}d_x=90-8=82,
\]
and
\[
\sum_{x\in X}\binom{d_x}{2}=70-70=0.
\]
The last equality forces every \(d_x\le1\).  But then
\[
\sum_{x\in X}d_x\le|X|=81,
\]
contradicting the required value 82.

Hence
\[
\boxed{\text{a norm-18 solution must have }h\in\{0,1\}.}
\tag{9}
\]

This argument uses all 81 outside vertices and no symmetry assumption.

## 3. Norm 16, \(h=0\)

Here \(s=8\), \(|X|=83\).  Equations (2), (7), and (8) give
\[
\sum d_x=80,\qquad
\sum\binom{d_x}{2}=8,\qquad
e(X)=501.
\tag{10}
\]
Since \(2d_x\le14\), it is enough to enumerate \(0\le d_x\le7\).
Writing \(n_j=|\{x:d_x=j\}|\), the exact checker finds precisely four
histograms \([n_0,\ldots,n_7]\):
\[
\begin{array}{c|rrrrrrrr}
 &n_0&n_1&n_2&n_3&n_4&n_5&n_6&n_7\\\hline
1&8&72&2&0&1&0&0&0\\
2&9&70&2&2&0&0&0&0\\
3&10&67&5&1&0&0&0&0\\
4&11&64&8&0&0&0&0&0
\end{array}
\tag{11}
\]
These are necessary moment solutions, not graph constructions.

## 4. Norm 18, \(h=0\)

Now \(s=9\), \(|X|=81\), and
\[
\sum d_x=90,\qquad
\sum\binom{d_x}{2}=18,\qquad
e(X)=477.
\tag{12}
\]
The exact bounded histogram enumeration has 20 solutions.  They are stored
in `exact-results.json`.  Their maximum occupied \(d\) ranges from two to
five.  Aggregate outside moments alone do not delete this lane.

## 5. Norm 18, \(h=1\)

For one same-sign edge per side,
\[
\sum d_x=86,\qquad
\sum\binom{d_x}{2}=9,\qquad
e(X)=481.
\tag{13}
\]
There are exactly six histograms:
\[
\begin{array}{c|rrrrrrrr}
 &n_0&n_1&n_2&n_3&n_4&n_5&n_6&n_7\\\hline
1&0&79&0&1&1&0&0&0\\
2&1&76&3&0&1&0&0&0\\
3&1&77&0&3&0&0&0&0\\
4&2&74&3&2&0&0&0&0\\
5&3&71&6&1&0&0&0&0\\
6&4&68&9&0&0&0&0&0
\end{array}
\tag{14}
\]
Again, these are necessary conditions only.

## 6. Boundary

Wave 74 removes the norm-18 \(h=2\) branch exactly.  It does not remove:

- the Wave 71 norm-14 complement-of-Fano/design branch;
- norm 16 with one of the four outside histograms (11);
- norm 18, \(h=0\), with one of 20 histograms;
- norm 18, \(h=1\), with one of the six histograms (14).

The Wave 71 congruence
\[
N_{14}+N_{16}+N_{18}\equiv2\pmod{14}
\]
therefore still does not contradict the graph hypothesis.  Conway-99 and
novelty remain `UNKNOWN`.
