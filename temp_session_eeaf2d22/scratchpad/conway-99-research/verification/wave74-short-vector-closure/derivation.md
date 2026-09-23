# Independent derivation

Claim label: `VERIFIED`, conditional on Wave 71's stated signed-unit support
reduction.

## 1. Frozen hypothesis

Let \(G\) be an \(\operatorname{srg}(99,14,1,2)\) with adjacency matrix
\(A\). Conditionally import only the following Wave 71 statement: there is
an integer vector \(t\) with
\[
\mathbf1^{\mathsf T}t=0,\qquad At=-4t,
\]
whose nonzero coordinates are \(+1\) on \(P\), \(-1\) on \(N\), and zero
outside, where \(|P|=|N|=s\). For norm 16, \(s=8\) and there are no
same-sign edges. For norm 18, \(s=9\) and each sign side has
\(h\in\{0,1,2\}\) edges.

No other part of Wave 71 is verified here.

## 2. Degree and incidence equations

For \(v\in P\), let \(r_v\) be its degree within \(P\). The coordinate
equation \((At)_v=-4\) gives
\[
|N(v)\cap N|=4+r_v.
\]
Summing over \(P\), and applying the symmetric equation on \(N\), gives
equal same-sign edge counts and
\[
e(P,N)=4s+2h.
\]

Thus incidences from one sign side to the outside set
\(X=V(G)\setminus(P\cup N)\) total
\[
14s-2h-e(P,N)=10s-4h. \tag{1}
\]
For \(x\in X\), its zero-coordinate equation says
\[
|N(x)\cap P|=|N(x)\cap N|=:d_x. \tag{2}
\]
In particular its total support degree is \(2d_x\), so \(0\le d_x\le7\).

Among unordered pairs on one sign side, the strongly regular graph
parameters allow total common-neighbor capacity
\[
h\lambda+\left(\binom{s}{2}-h\right)\mu
=s(s-1)-h. \tag{3}
\]
If the opposite sign side has same-side degrees \(r_v\), its contribution to
this capacity is
\[
\sum_v\binom{4+r_v}{2}. \tag{4}
\]
The same sign side itself contributes
\(\sum_v\binom{r_v}{2}\). Therefore the outside contribution is the
remainder after subtracting both terms.

## 3. Exhausting both norm-18 \(h=2\) shapes

The verifier enumerates all
\(\binom{\binom92}{2}=630\) unordered pairs of distinct edges on nine
vertices. Exactly two degree shapes occur:

- 252 adjacent-edge pairs with degrees \((2,1,1,0^6)\);
- 378 disjoint-edge pairs with degrees \((1,1,1,1,0^5)\).

There is no hidden third shape.

If either sign side has the adjacent shape, apply (4) to pairs on the
opposite side:
\[
\binom62+2\binom52+6\binom42=71.
\]
But (3) is
\[
2\lambda+34\mu=70.
\]
The opposite-support contribution alone exceeds the full capacity, so an
adjacent shape is impossible regardless of the other side's two-edge shape.
For bookkeeping, the adjacent side also supplies one same-support
common-neighbor incidence, so the formal full remainder is \(70-71-1=-2\).
The discovery JSON's `outside_pair_incidences=-1` for this already-impossible
lane subtracts only the fatal opposite-support contribution. No histogram or
live conclusion depends on that sentinel value.

Consequently both sides would have to be disjoint. Equation (4) is then
\[
4\binom52+5\binom42=70,
\]
exactly saturating (3). A two-edge matching has no vertex adjacent to two
vertices of its own side, so the same-support contribution is zero as well.
Hence
\[
\sum_{x\in X}\binom{d_x}{2}=0. \tag{5}
\]
Thus every \(d_x\le1\).

For \(s=9,h=2\), (1) requires
\[
\sum_{x\in X}d_x=90-8=82,
\]
but \(|X|=99-18=81\). Equation (5) would force
\(\sum_xd_x\le81\), a contradiction. This independently verifies that
norm 18 can only retain \(h=0\) or \(h=1\).

## 4. Exhaustive remaining histogram check

Write
\[
n_j=|\{x\in X:d_x=j\}|,\qquad 0\le j\le7.
\]
For each remaining lane the verifier imposes
\[
\sum_jn_j=|X|,\qquad
\sum_j jn_j=I,\qquad
\sum_j\binom j2n_j=C. \tag{6}
\]
It exhausts \(n_2,\ldots,n_7\) over the finite ranges
\[
0\le n_j\le\left\lfloor C/\binom j2\right\rfloor.
\]
After a tuple meets the third equation in (6), the second and first
equations uniquely determine
\[
n_1=I-\sum_{j=2}^7jn_j,\qquad
n_0=|X|-n_1-\sum_{j=2}^7n_j.
\]
Keeping exactly the nonnegative solutions is therefore complete, not a
heuristic or a bounded-prefix search.

The exact results are:

| lane | \(|X|\) | \(I\) | \(C\) | \(e(X)\) | histograms |
|---|---:|---:|---:|---:|---:|
| norm 16, \(h=0\) | 83 | 80 | 8 | 501 | 4 |
| norm 18, \(h=0\) | 81 | 90 | 18 | 477 | 20 |
| norm 18, \(h=1\) | 81 | 86 | 9 | 481 | 6 |

All 30 full histogram vectors exactly equal the frozen discovery artifact.

## 5. Boundary

The enumeration certifies only scalar moment solutions. It neither builds
the bipartite outside-incidence matrices nor checks all pairwise
compatibilities needed for a strongly regular graph. Hence the surviving
histograms cannot be called realizations, candidates, or evidence for
existence. Norm 14 and the 30 aggregate norm-16/norm-18 lanes remain open.
Conway-99 and novelty remain `UNKNOWN`.
