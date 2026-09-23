# Derivation

## 1. Root partition

Fix a triangle `T={t0,t1,t2}`. For `i=0,1,2`, let `A_i` be the vertices
outside `T` adjacent to `t_i`. Adjacent vertices have exactly one common
neighbor, already supplied by the third vertex of `T`, so no outside vertex
is adjacent to two vertices of `T`. Hence

```text
|A_0|=|A_1|=|A_2|=12,   |B|=60,
```

where `B` contains the vertices adjacent to none of `T`.

For `x in A_i`, the unique common neighbor of `x,t_i` lies in `A_i`.
Therefore the adjacency matrix `M_i` induced on `A_i` is a perfect matching.

For `x in A_i` and `j != i`, the nonedge `x,t_j` has two common neighbors.
One is `t_i`; the other is a unique vertex of `A_j`. Thus every cross-block
`F_ij` is a permutation matrix and `F_ji=F_ij^T`.

Each `x in A_i` has ten remaining neighbors in `B`. Each `b in B` has exactly
two neighbors in every `A_i`. Writing the three incidence matrices as
`C_i`, they have row sum 10 and column sum 2. The graph induced on `B` is
8-regular; write its adjacency matrix as `D`.

## 2. Prisms as fixed points

A triangle with one vertex in each `A_i` forms the second face of a triangular
prism rooted at `T`. After relabeling the three `A_i`, its count is

```text
q_T = trace(F_01 F_12 F_20).
```

Every prism has two triangle faces, so `sum_T q_T=2N1`. At `n3=4158`, the
frozen formula `N1=1386-n3/3` gives `N1=0`; equivalently every root
composition must be a derangement.

## 3. The forced Gram matrix

For `srg(99,14,1,2)`,

```text
A^2 = 12 I - A + 2 J.
```

Taking its `(A_i,A_i)` block gives

```text
C_i C_i^T = 9I - M_i + J.                         (1)
```

Taking the `(A_i,A_j)` block, where `{i,j,k}={0,1,2}`, gives

```text
C_i C_j^T
 = 2J - F_ij - M_i F_ij - F_ij M_j - F_ik F_kj.  (2)
```

Equations (1)-(2) determine `G=C C^T` for the stacked matrix
`C=(C_0;C_1;C_2)`.

## 4. Exact prism-free witness

Use 12 coordinates and set

```text
M_0=M_1=M_2=(0 1)(2 3)(4 5)(6 7)(8 9)(10 11),
F_01=F_02=I,
F_12=P,  P(x)=x+6 mod 12.
```

`P` is a fixed-point-free involution and commutes with `M`. Therefore the
rooted prism count is zero.

The Gram blocks become

```text
G_ii = 9I-M+J,
G_01=G_02 = 2J-I-2M-P,
G_12 = 2J-I-P-2MP.
```

Every entry is nonnegative.

## 5. Exact PSD certificate

The commuting involutions `M,P` have joint eigenvalues `m,p in {+1,-1}`.
On the all-ones direction `J` has eigenvalue 12; otherwise it has eigenvalue
zero. For a joint character `(m,p,j)`, the three group coordinates see

```text
[ d  a  a ]
[ a  d  b ]
[ a  b  d ],

d=9-m+j,
a=2j-1-2m-p,
b=2j-1-p-2mp.
```

This splits into the antisymmetric eigenvalue `d-b` and the symmetric
two-by-two block

```text
[ d       sqrt(2)a ]
[ sqrt(2)a  d+b    ].
```

The five character cases and their integer determinant certificates are in
`exact-results.json`. Every `d-b` and every two-by-two determinant is
nonnegative. Their multiplicities give rank 32 exactly.

## 6. Missing compatibility

PSD is necessary but does not produce the binary matrix `C`. If such a factor
exists, the mixed `(A_i,B)` block further requires

```text
C_i D = 2J-C_i-M_iC_i-F_ijC_j-F_ikC_k.            (3)
```

Finally, the `(B,B)` block requires

```text
D^2 = 12I-D+2J-sum_i C_i^T C_i.                   (4)
```

Binary factorization, equations (3)-(4), and agreement between different
root triangles are precisely outside the verified projection.
