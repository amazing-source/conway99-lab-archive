# Exact construction and premise ledger

## 1. Local projector ingredients

Work in `V=F_3^11` with form matrix

```text
M=diag(1,1,1,1,1,1,1,1,1,1,2).
```

The checker reconstructs three six-spaces `E_P,E_Q1,E_Q2`, their orthogonal
projectors `P,Q1,Q2`, and seven singular columns for each. For every type
`R`:

```text
R^2=R
R^T M=M R
rank(R)=6
tr(R)=0
Gram(z_0,...,z_6)=J_7-I_7
sum_i z_i=0
R=-sum_i z_i z_i^T M.
```

The three six-spaces span all 11 ambient dimensions. The relevant local pair
data are

| Pair | `tr(RS)` | `tr(RSRS)` |
|---|---:|---:|
| `P,Q1` | 2 | 1 |
| `P,Q2` | 2 | 2 |
| `Q1,Q2` | 1 | 2 |

Thus replacing `Q1` by `Q2` preserves its pair trace with `P` and changes the
alternating fourth trace.

## 2. A seven-factorized linear triple system

Partition the 99 point labels into cyclic components of orders

```text
27, 36, 36.
```

For a component `Z_n`, use these blocks:

1. the `n/3` translates of the short block
   `{0,n/3,2n/3}`;
2. all `n` translates of `{0,1,5}`; and
3. all `n` translates of `{0,2,10}`.

The short orbit is color 0. Color a translate `t+{0,1,5}` by
`1+(t mod 3)`, and color `t+{0,2,10}` by `4+(t mod 3)`.

For `n=27` and `n=36`, the directed difference sets

```text
{+-1,+-4,+-5},
{+-2,+-8,+-10},
{+-n/3}
```

are internally repetition-free and pairwise disjoint. Therefore two point
rows share at most one block: the triple system is linear.

At a fixed point `x`, the three block translates from the first full orbit
have indices `x,x-1,x-5`, which are distinct modulo 3. The second full orbit
has indices `x,x-2,x-10`, also distinct modulo 3. Together with the short
orbit, every point sees each color `0,...,6` exactly once.

The total block count is

```text
7*27/3 + 7*36/3 + 7*36/3 = 63+84+84 = 231.
```

Let `B` be the `99 by 231` point-block incidence. It has row degree 7 and
column degree 3. Linearity gives a simple point graph `A` in which two
distinct points are adjacent exactly when they share a block. Hence

```text
BB^T=A+7I                 over Z
BB^T=A+I                  over F_3.
```

Every point has 7 blocks and gains two distinct neighbors per block, so `A`
is 14-regular with 693 edges.

## 3. Coupling the incidence to the projector simplices

In realization A, assign projector types to the three components by

```text
P, Q1, Q2.
```

In realization B, assign

```text
P, Q2, Q1.
```

For a block of color `i`, use column `z_i` from its component's assigned
simplex. Since every point sees each color once, its seven incident block
columns are exactly the corresponding simplex. This proves the star coupling
for all 99 points.

Each projective direction appears 9 times in the order-27 component or 12
times in an order-36 component. Those multiplicities vanish in `F_3`, so the
global frame operator is zero. Consequently, for the `11 by 231` column
matrix `Z`,

```text
Z Z^T M=0,
D=Z^T M Z,
D^2=0.
```

The three simplex spans together have dimension 11, hence

```text
rank(Z)=rank(D)=11.
```

## 4. Edge/nonedge fourth-trace separation

Both endpoints of every point-graph edge lie in the same component. Within a
component all 99-point projector labels are equal. Therefore, on every edge,

```text
g_xy=tr(R^2)=tr(R)=0,
h_xy=tr(R^4)=tr(R)=0
```

in both realizations.

Across components there are no graph edges. Swapping `Q1,Q2` preserves every
pair trace, including all `P-Q` pairs, but it interchanges the values 1 and 2
of `h` on ordered `P-Q` pairs. Their number is

```text
2 * 27 * (36+36) = 3888.
```

Thus:

```text
full g matrix:                    identical
ordered edge h differences:      0
ordered nonedge h differences:   3888
```

## 5. Exact graph failures

The point graph is deliberately audited rather than described as locally
linear. Its connected components have orders `27,36,36`. It has 1,329 graph
triangles, of which only 231 are designated blocks. The exact common-neighbor
distributions are:

```text
edge lambda:
4:144, 5:243, 6:27, 7:225, 8:27, 9:27

nonedge mu:
0:3240, 2:144, 4:180, 5:27, 6:315, 7:27, 8:225
```

So the construction does not satisfy either `lambda=1` or `mu=2`.

## 6. Correct tensor rank ledger

Self-adjoint endomorphisms of an 11-dimensional nondegenerate orthogonal
space correspond to symmetric bilinear forms and have dimension

```text
11*12/2=66.
```

Because `tr(I)=11=2` in `F_3`, trace is a nonzero functional on this space.
The trace-zero self-adjoint subspace therefore has dimension 65.

The word

```text
h(A,B)=tr(ABAB)
```

is bilinear after the quadratic lifts `A -> A tensor A` and
`B -> B tensor B`, with the second tensor factors contracted after an index
permutation. These quadratic lifts lie in `Sym^2(W)` for the 65-dimensional
trace-zero self-adjoint space `W`, whose dimension is

```text
65*66/2=2145.
```

The resulting unconditional bound

```text
rank(H) <= min(99,2145)=99
```

is valid but vacuous.

Similarly, `wedge^2(P_x)` acts on a 55-dimensional space, but it is an
operator on that space. Before further structural reduction it has up to
`55^2=3025` operator coordinates, not 55. No rank-55 conclusion is licensed.

## 7. Logical conclusion

This is a construction-level compatibility blueprint substantially stronger
than a pairwise control: it adds exact star/block coupling, a linear
degree-correct incidence, the modular `BB^T` identity, and complete agreement
of the fourth traces on a 14-regular edge relation.

It is still relaxed. The surviving named graph-specific invariants are at
least:

- projective distinctness of all 231 centered columns;
- the exact `lambda=1,mu=2` point-graph common-neighbor laws;
- the selected-orthogonality block relations;
- actual adjacent outer-cycle modules;
- prism-free `n3=4158` compatibility; and
- endpoint code/cover constraints.

No target status is promoted.
