# Wave 39 cross-base ternary projection

Status: `DERIVED_INCONCLUSIVE`.

This package attacks the conditional prism-free endpoint `n3=4158` at the
only surviving ternary boundary

```text
rank_F3(M)=12, with square factor-form determinant.
```

It obtains a new necessary cross-base restriction but no contradiction:
for every original graph vertex, the 84 graph triangles adjacent to that
vertex force at least twelve pairs of equal five-dimensional projections.
Each such pair gives an explicit factor-row dependency supported on four or
six triangles.  The endpoint remains `UNKNOWN`, and the general bound remains
`n3<=4158`.

## 1. The determinant tower

Use the independently verified factorization over `F_3`

```text
C=V H V^T,   C=2M-21I,
```

and the common vector-star sum `w`.  At rank twelve, the form `H` has square
determinant and `(w,w)=2`.  With `z_T=v_T-w`, the centered vectors span the
nondegenerate space

```text
W=w^perp,   dim W=11,   det(W)=2 (nonsquare).
```

For a fixed original vertex `x`, its seven incident triangles have centered
Gram `J-I`, sum to zero, and span a nondegenerate six-space `E_x`.  A basis
of six has Gram `J_6-I_6`, determinant one.  Therefore

```text
K_x=E_x^perp in W
```

is a nondegenerate nonsquare five-space.

## 2. Projection of an adjacent triangle

Let `z_0,...,z_6` be the centered rows in the star of `x`.  For any centered
row `z_U`, put

```text
d_i=(z_i,z_U),
p_U=-sum_i d_i z_i,
q_U=z_U-p_U in K_x.
```

The formula for `p_U` follows from `sum_i d_i=0` and the simplex Gram.
Since `z_U` is isotropic,

```text
(q_U,q_U)=sum_i d_i^2.                         (1)
```

Suppose `U` does not contain `x` but has one vertex adjacent to `x`.
There are exactly

```text
14*6=84
```

such triangles.  The star triangle containing the edge to `x` contributes
`M=0`.  Each of the other six star triangles is disjoint from `U`, already
has one cross edge, and has one or two cross edges because the endpoint is
prism-free.  Their entries are therefore `M=0` or `M=-1`.  The verified
identity `(M N^T)[U,x]=-2` forces exactly two minus entries.  Consequently

```text
d_U has five 1s and two 2s,
(q_U,q_U)=7=1 mod 3.                              (2)
```

## 3. Forced short dependencies

Exact enumeration of the nonsquare form

```text
diag(1,1,1,1,2)
```

gives

```text
norm 0 vectors: 81
norm 1 vectors: 72
norm 2 vectors: 90.
```

Thus the 84 adjacent triangles map to only 72 possible oriented norm-one
vectors in `K_x`.  If the occupancies are `m_a`, then

```text
sum_a binom(m_a,2) >= sum_(m_a>0)(m_a-1) >= 84-72=12.   (3)
```

So every vertex forces at least twelve equal-projection pairs `q_U=q_V`.
For such a pair,

```text
z_U-z_V+sum_i(d_Ui-d_Vi)z_i=0.                    (4)
```

The two positions occupied by `2` in `d_U` and `d_V` cannot be equal:
equal `d` and equal `q` would determine equal `z`, contradicting distinct
factor rows.  If those position pairs overlap in one position, (4) has
support four; if they are disjoint, it has support six.  Every coefficient
in (4) sums to zero, so the same relation holds with `v_T=z_T+w`.

The pair's centered inner product is also forced:

```text
overlap one: D_UV=1,
disjoint:    D_UV=2.
```

These dependencies are a new exact closing target.  This package does not
prove they are incompatible across all 99 vertex stars.

## 4. Local rank shortcut is false

The checker freezes two simple tripartite four-regular quotients on
`6+6+6` vertices, with every bipartite block two-regular:

```text
rank_F3(P-I)=10,
rank_F3(P-I)=11 with nonsquare discriminant.
```

The second has the determinant class required if a rank-eleven local Gram
spans the global centered space.  Hence neither local quotient axioms nor
the global determinant class forces `rank_F3(P-I)>=12`.

These quotient matrices are not 36-vertex cores, simultaneous `B/H`
completions, endpoint matrices, or graphs.

## 5. Hostile positive control

The checker constructs an exact nonsquare eleven-space as the orthogonal
sum of the six-dimensional star and the five-dimensional complement.  It
places 84 distinct isotropic adjacent vectors with the required five-one,
two-two star profiles.  Their projections use all 72 norm-one vectors,
with twelve values repeated once, and it checks all twelve resulting
support-four/six relations exactly.

This is a control for the projection relaxation only.  It omits the other
140 triangles, the full `V^T V=0` frame, the global `D` relation alphabet,
simultaneous compatibility at other vertices, and a graph.

## Reproduction

```powershell
.\.venv\Scripts\python.exe -B attempts\wave39-cross-base-rank\exact_check.py --output attempts\wave39-cross-base-rank\exact-results.json
.\.venv\Scripts\python.exe -B attempts\wave39-cross-base-rank\exact_check.py --verify attempts\wave39-cross-base-rank\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave39-cross-base-rank\test_exact_check.py
```

The exact result is:

```text
forced equal-projection pairs per vertex: at least 12
dependency support:                         4 or 6
endpoint excluded:                          no
upper bound improved:                       no
n3=4158 / Conway-99:                        UNKNOWN
```
