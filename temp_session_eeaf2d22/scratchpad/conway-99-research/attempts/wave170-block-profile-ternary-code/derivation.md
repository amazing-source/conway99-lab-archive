# Derivation

Let `K` be the 18-regular intersection graph on the 231 unique triangle
blocks. Fix a block `L={x1,x2,x3}`. For a disjoint block `M`, let

```text
j(L,M)=|N_K(L) intersect N_K(M)|.
```

This is the number of cross edges between the two point triples and lies in
`{0,1,2,3}`. Let `n_j(L)` count disjoint `M` with value `j`, and set
`p_L=n_3(L)`.

## 1. Three pointwise equations

There are 18 blocks meeting `L`, so

```text
sum_j n_j(L)=231-1-18=212.                          (1)
```

Each point of `L` has 12 neighbors outside `L`, for 36 boundary edges. The
outside endpoint of such an edge lies on six further triangle blocks, all
disjoint from `L`. Counting a boundary cross edge together with one of those
blocks gives

```text
sum_j j*n_j(L)=36*6=216.                            (2)
```

For each unordered point pair `xi,xk` in `L`, their two 12-vertex external
neighbor sectors are joined by a perfect matching. Indeed, for a vertex `y`
in the first sector, `y` and the other root point are nonadjacent and already
have one common neighbor in `L`; `mu=2` forces a unique second common
neighbor in the other sector. There are 12 matching edges for each of three
root pairs.

A pair of cross edges landing in one disjoint block is counted exactly once
by such a sector-matching edge. Therefore

```text
sum_j binomial(j,2)*n_j(L)=3*12=36.                 (3)
```

Solving (1)--(3) gives

```text
n3=p_L,
n2=36-3*p_L,
n1=144+3*p_L,
n0=32-p_L.                                         (4)
```

Nonnegativity gives `0<=p_L<=12`.

## 2. Global distribution

Every prism has a unique unordered pair of triangular bases, so

```text
sum_L p_L=2P.
```

Summing (4) over `L` and dividing by two gives

```text
N3=P,
N2=4158-3P,
N1=16632+3P,
N0=3696-P.                                         (5)
```

A disjoint block pair with two cross edges is precisely the six-vertex
`N3` configuration. Hence (5) recovers

```text
n3+3P=4158.
```

At `P=0`, every `p_L` is zero and every block has profile
`(32,144,36,0)`.

## 3. Maximum point-star cliques

The seven triangle blocks through one original point form a `K7`. These 99
point stars cover every edge of `K` exactly once, and every block vertex lies
in the three stars corresponding to its three points.

The size seven is maximum by linearity. For any pairwise-intersecting family
of triangle blocks, fix one block. If all other members meet it at the same
point, the point degree bounds the family by seven. If members use at least
two of its points, a block in one part has only two outside points and can
meet at most two blocks in another part without creating a double
intersection; each nonempty part then has size at most two. Again the total
is at most seven.

This clique geometry is compatible with the least eigenvalue `-3` and the
rank-99 Gram factor

```text
K+3I=B^T*B.
```

A star-complement representation for the 132-dimensional `-3` eigenspace
would retain 99 block vertices and express the other 132 through exact
binary neighborhood data. No such classification is supplied here.

## 4. Ternary Gram rank

Work over `F_3` and put

```text
M=B*B^T=A+I.
```

The SRG equation reduces to

```text
M^2=M-J,
M*J=J*M=0,
J^2=0.
```

Therefore `M^2` is idempotent. The characteristic polynomial of `M` modulo
three is

```text
x^45*(x-1)^54.
```

The same eigenvalue multiplicities apply to the idempotent `M^2`, so

```text
rank_F3(M^2)=54.
```

Because `M=M^2+J`, the image of `J` is the line spanned by the all-one
vector, this line lies in the kernel of `M^2`, and an idempotent's image and
kernel intersect trivially. Hence

```text
rank_F3(B*B^T)=rank_F3(M)=54+1=55.                  (6)
```

It follows that

```text
rank_F3(B)>=55.
```

The sum of all 99 point rows of `B` is zero over `F_3`, because every block
contains three points, so

```text
rank_F3(B)<=98.                                     (7)
```

Equations (6)--(7) are exact code constraints. They are parameter-forced and
currently imply no sharper bound on `p_L`, `P`, or `n3`.

## Boundary

The block profile recovers the known prism identity rather than improving
it. A useful continuation must combine the clique factor, ternary row code,
or star complement with the prism-free `n3=4158` support restrictions. No
complete classification or contradiction is present.
