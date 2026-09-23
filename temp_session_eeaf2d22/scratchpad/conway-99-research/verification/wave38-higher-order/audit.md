# Wave 38 higher-order independent audit

Verdict: **PASS with one wording qualifier, at conditional/local scope**.

The signed four-cycle subtraction, ternary centering lemma, fixed-base
nineteen-triangle rank identity, and frozen rank-ten local control were
reconstructed independently.  The verifier did not import or execute
`attempts/wave38-higher-order/exact_check.py`; comparison with discovery used
only the frozen JSON data.

The one qualifier is:

```text
centered seven-row Gram (z_T, D=C+J):   rank 6 over F_3
uncentered seven-row Gram (v_T, C):     rank 7 over F_3
```

The submitted prose makes the centered meaning clear, but the JSON field
`seven_clique_gram_rank: 6` is ambiguous when read alone.  No numerical or
substantive mathematical discrepancy was found.

## Scope and evidence separation

The target is the hypothetical prism-free endpoint `n3=4158`.  General
claims below are conditional on the already audited endpoint identities.
The 36-vertex graph is an exactly checked local relaxation, not an endpoint
graph.

Before inspecting the submitted Wave 38 contents, the six files in
`attempts/wave38-higher-order/` were frozen by SHA-256.  The independent
checker contains its own arithmetic, graph reconstruction, rank elimination,
and enumeration code.  The submitted Python was never imported or run.

## 1. Signed trace subtraction

Put `S=M-4I`.  The audited endpoint data give

```text
spec(S)=17^44,(-4)^187,
231 support vertices,
68 nonzero off-diagonal signs in every row.
```

Therefore

```text
tr(S^3)=44*17^3+187*(-4)^3 = 204204,
tr(S^4)=44*17^4+187*(-4)^4 = 3722796.
```

For a loopless support graph, a closed four-walk that is not on four
distinct vertices satisfies `v0=v2` or `v1=v3`.  Each class has
`231*68^2` members.  The alternating walks
`v0-v1-v0-v1-v0`, of which there are `231*68`, lie in both classes.
Inclusion-exclusion gives

```text
2*231*68^2 - 231*68
 = 231*68*(2*68-1)
 = 2120580.
```

Every edge of such a backtracking walk occurs an even number of times, so
its signed contribution is `+1`.  Every remaining closed walk traverses a
simple support four-cycle, with eight starting-point/orientation
representations and common sign product.  With “balanced” defined as edge
product `+1`,

```text
balanced C4 - unbalanced C4
 = (3722796-2120580)/8
 = 200277.
```

The analogous triangle count is

```text
(balanced triangles)-(unbalanced triangles)
 = tr(S^3)/6
 = 34034.
```

Hostile controls checked a positive-product signed `C4` contributes `+8`
after subtraction and a negative-product `C4` contributes `-8`.  Omitting
the overlap term in the non-simple count makes the remainder nondivisible by
eight, so the common double-counting error is detected.

This counts support four-cycles, including cycles that may have chords.  It
does not determine either unsigned count separately and gives no endpoint
contradiction.

## 2. Common ternary vertex-star sum and centering

Let `N` be the `99 x 231` vertex-triangle incidence matrix, `A` the original
graph adjacency matrix, and `Gamma` the triangle-intersection adjacency
matrix.  From

```text
Gamma=N^T N-3I,
N N^T=7I+A,
A^2=12I-A+2J,
M=21I+4Gamma-Gamma^2+J,
```

one obtains, without using the submitted implementation,

```text
Gamma N^T=N^T(4I+A),
(4I+A)^2=28I+7A+2J,
M N^T=9N^T-3N^T A+J.                    (1)
```

For a fixed triangle `T`, a vertex in `T` has two neighbors in `T`; an
outside vertex adjacent to `T` has exactly one; and a remaining vertex has
zero.  Equation (1) consequently has entries

```text
4, -2, 1
```

in those three cases.

Reduce

```text
C=2M-21I=V H V^T
```

over `F_3`, where `V` has full column rank and `H` is nondegenerate.  If
`v_T` is a factor row and

```text
w_x = sum_(T contains x) v_T,
```

then twice each of `4,-2,1` is `2 mod 3`.  Thus

```text
(v_U,w_x)=2
```

for every `U,x`.  The rows `v_U` span the factor space, whose form is
nondegenerate, so all `w_x` are one vector `w`.

The seven triangles through one original vertex have mutually orthogonal
factor rows of norm two.  Hence

```text
(w,w)=7*2=2 mod 3.
```

For `z_T=v_T-w`,

```text
(z_T,w)=0,
(z_T,z_T)=0,
(z_T,z_U)=C_TU+1,
sum_(T contains x) z_T=w-7w=0.           (2)
```

Thus the centered Gram is exactly `D=C+J`.  All `z_T` lie in `w`-orthogonal.
Since the vectors `v_T=z_T+w` span the full factor space and the anisotropic
vector `w` cannot lie in `w`-orthogonal, the `z_T` span all of
`w`-orthogonal.  Its form is nondegenerate, so

```text
rank_F3(D)=r3-1.                          (3)
```

On one seven-triangle vertex star, the centered Gram is `J-I` over `F_3`,
with rank six and kernel spanned by the all-one vector.  By contrast, the
uncentered Gram is `2I_7` and has rank seven.  This is the audit's wording
qualifier.

## 3. Fixed-base nineteen-triangle contraction

Fix a graph triangle `T={t0,t1,t2}`.  There are six other triangles through
each `ti`, hence nineteen triangles including `T`.  Contract the matching
edge of each of those eighteen triangles.  Between each pair of six-label
parts, the extra cross-fibre matching edges give a two-regular bipartite
graph.  Prism-freeness forbids a doubled quotient edge, so their union `P`
is a simple four-regular tripartite graph on parts `6+6+6`.

In the order `T | 6 | 6 | 6`, equation (2) gives

```text
          [ 0       1^T   ]
D_T   =   [ 1     J-I+P   ].
```

Set `L=P-I`.  Four-regularity gives `L1=0`.  If `e` is the indicator of
one six-point part and `u=2e`, two-regularity of both incident bipartite
blocks gives

```text
Lu=1,   1^T u=12=0 mod 3.                 (4)
```

The rank equality follows exactly from kernels, not from a numerical
coincidence.  For `(a,x)` in the kernel of `D_T`,

```text
1^T x=0,
Lx=-a1.
```

Using (4), `(a,x)` maps to `x+a u` in `ker(L)`.  Conversely, for any
`y in ker(L)` and any scalar `a`, `(a,y-a u)` lies in `ker(D_T)`;
`1^T y=0` follows from `1=Lu`.  Therefore

```text
nullity(D_T)=nullity(L)+1,
rank_F3(D_T)=rank_F3(P-I).                 (5)
```

Because `D_T` is merely a principal submatrix of the global `D`, the only
global consequence is

```text
rank_F3(P_T-I) <= rank_F3(D)=r3-1.         (6)
```

Equality with the global rank is not claimed.  A hostile test deletes one
quotient edge; the verifier rejects the mutated object before applying
(5), because the four-regular/two-regular hypotheses fail.

## 4. Frozen 36-vertex local control

The independent checker parses the frozen 36 hexadecimal row masks and
checks symmetry and absence of loops before using them.  Its canonical
upper-triangle bit hash is

```text
b5a5d573b5eb1beba106e5735d5f4e2f71c8b23b036e0e44a1014718f0570984.
```

Exact reconstruction gives

```text
vertices / edges / degrees:       36 / 54 / {3}
connected / triangle-free:        yes / yes
fibre sizes:                       12+12+12
within each fibre:                one perfect matching
between each fibre pair:          one perfect matching
maximum quotient multiplicity:    1
quotient degree:                   4
each bipartite block degree:       2
rank_F3(P-I):                      10
rank_F3(D_T):                      10
```

The complete pair-codegree histogram is

```text
edge:0                         54
same-fibre nonedge:0          180
cross-fibre nonedge:0         296
cross-fibre nonedge:1          92
cross-fibre nonedge:2           8
```

Thus the submitted graph-local caps and absence of quotient double edges
check exactly.

For

```text
Q=12I-A_X+2J-RR^T-A_X^2,
```

the exact verifier finds

```text
entries 0/1/2/10:        52 / 616 / 592 / 36
diagonal:                10
row sum:                 60
minimum entry:           0
rank over Q:             34.
```

The two fibre-difference vectors lie in the kernel and the constant vector
has eigenvalue 60.  On the 33-dimensional orthogonal complement of the
fibre-indicator space,

```text
Q=(3I-A_X)(4I+A_X).
```

Since `A_X` is symmetric cubic, its spectrum lies in `[-3,3]`; connectedness
keeps eigenvalue `3` out of this complement.  Hence `Q` is positive there,
proving positive semidefiniteness and independently explaining rank 34.

## 5. Individual-column census

Each fibre supplies the 60 nonmatching pairs.  The checker exhausts all
`60^3=216000` triples.  It first requires the selected six vertices to
induce a matching.  It then imposes, coordinate by coordinate,

```text
d(b)=2*1-(I+A_X)b >= 0.
```

The independent totals are

```text
induced-matching survivors:       183596
mixed-equation survivors:         152399

mixed survivors by X-edge count:
0: 52517
1: 76540
2: 22610
3:   732
```

All match the frozen submitted JSON.  These are individual columns.  They
do not select sixty compatible columns and do not realize `BB^T`, the mixed
equation with a common `H`, or the `Y-Y` equation.

## Hostile scope audit and final classification

```text
signed C4 imbalance 200277:                 VERIFIED, conditional
ternary common w and rank(D)=r3-1:           VERIFIED, conditional
seven-row centered Gram rank 6:              VERIFIED, wording qualified
fixed-base rank(D_T)=rank(P-I):              VERIFIED, conditional
frozen core / rank 10 / BB^T properties:     VERIFIED, local finite object
183596 -> 152399 individual-column census:   VERIFIED, local finite census
simultaneous 60-column B:                    UNKNOWN
compatible H / 99-vertex graph:              UNKNOWN
rank-twelve endpoint exclusion:              NOT OBTAINED
upper bound below n3<=4158:                  NOT OBTAINED
novelty or literature priority:              UNKNOWN, not audited
n3=4158 / Conway-99:                         UNKNOWN
```

The rank-ten core refutes only the proposed inference from the listed
one-triangle/local constraints to a universal local rank floor of twelve.
It is positive evidence about the looseness of that relaxation, not evidence
that the full endpoint exists.
