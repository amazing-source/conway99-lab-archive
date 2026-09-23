# Wave 38 proof A: higher-order endpoint restrictions

```yaml
role: proof_a
date_utc: 2026-07-27T01:16:03Z
git_commit: 3014f3b1c010cdde1687b8878d4ec58d2bb90f03
claim_label: DERIVED
scope: >
  Conditional n3=4158 signed four-cycle imbalance,
  characteristic-three vertex-clique centering, fixed-triangle quotient-rank
  bridge, and a local rank-ten positive control.
inputs:
  attempts/wave38-higher-order/input-freeze.sha256: 7e7f6fd8aa9182a85e1bc5119d0407ac3f6346eb21b6bc6a7f54e53e4043fd49
method: >
  Exact signed closed-walk subtraction; finite-field Gram centering;
  contraction of the nineteen triangles meeting a base triangle; exact
  rational and finite-field elimination; and exhaustive individual-column
  enumeration for a frozen local core.
command: |
  .\.venv\Scripts\python.exe -B attempts\wave38-higher-order\exact_check.py --output attempts\wave38-higher-order\exact-results.json
  .\.venv\Scripts\python.exe -B attempts\wave38-higher-order\exact_check.py --verify attempts\wave38-higher-order\exact-results.json
  .\.venv\Scripts\python.exe -B -m unittest -v attempts\wave38-higher-order\test_exact_check.py
outputs:
  attempts/wave38-higher-order/exact_check.py: 24897ec7cb87aebb77f374a5a2429fb0d2ecff161ed11c95e4d6b4dd9aff9965
  attempts/wave38-higher-order/test_exact_check.py: f64065a36a028deead10fd377b5763bb20c480cc830637a99f8f58fdf06762ff
  attempts/wave38-higher-order/exact-results.json: 7d3229234e5eda3f432ff88eb07670a18611b37a64ef3a7949f4a505f274c782
  attempts/wave38-higher-order/failed-routes.md: 834543e67f8f2d1d4e61d46b93ab0044de4a5855dbf06c36557beaf07c5507c0
  attempts/wave38-higher-order/run-report.yaml: 7c0b99f74e44fcf2c9267d9529384fde7f53e4b079aeac1821e7716c4a220ba4
limitations:
  - Discovery cannot verify itself; independent reconstruction is required.
  - The fourth-order count is necessary but not contradictory.
  - The frozen core has no simultaneous 60-column B or compatible H.
  - The frozen core is not a 99-vertex graph or endpoint construction.
  - No endpoint exclusion, P>=1 theorem, upper-bound improvement, or novelty claim is made.
```

## Result

The prism-free endpoint survives this lane.  Two exact structures are added:

```text
balanced signed support C4 - unbalanced signed support C4 = 200277,
rank_F3((C+J)[the 19 triangles meeting T])=rank_F3(P_T-I).
```

Here `P_T` is a simple four-regular tripartite graph on `6+6+6` labels,
with every bipartite block two-regular.  The rank identity connects the
actual seven-triangle cliques through the vertices of `T` to the surviving
ternary rank `r3`.

The hoped-for shortcut

```text
rank_F3(P_T-I)>=12
```

does not follow from the one-triangle core axioms.  An exact frozen connected
core satisfies all graph-local pair caps, has a nonnegative positive
semidefinite required `B B^T` of rational rank 34, and leaves 152,399
individual columns after the mixed cut, but it has

```text
rank_F3(P_T-I)=10.
```

This is a positive control for a relaxation, not a graph construction.
Simultaneous `B/H` completion or compatibility among different base
triangles is still missing.  Consequently

```text
P>=1:                    NOT PROVED
n3 upper bound:          4158
n3=4158 and Conway-99:   UNKNOWN
```

## 1. A fourth-order signed count

At the endpoint, put `S=M-4I`.  The verified input gives

```text
S^2=13S+68I,
spec(S)=17^44,(-4)^187,
```

and every row of `S` has 68 nonzero off-diagonal entries, each equal to
`+1` or `-1`.  Therefore

```text
tr(S^4)=44*17^4+187*4^4=3722796.
```

A closed signed walk of length four that does not have four distinct
vertices has one of the two backtracking identifications

```text
v0=v2  or  v1=v3.
```

There are `231*68^2` of each kind.  The walk that alternates on one edge is
in both classes, so inclusion-exclusion gives

```text
231*68*(2*68-1)=2120580
```

non-simple closed walks.  Every remaining walk runs around a simple
four-cycle; each undirected cycle has eight starting-point/orientation
representations, all with the same sign product.  Hence

```text
balanced C4 - unbalanced C4
 = (3722796-2120580)/8
 = 200277.                                             (1)
```

The previously derived triangle counterpart is recovered as

```text
balanced triangles - unbalanced triangles
 = tr(S^3)/6
 = 34034.
```

Equation (1) is a new fourth-order necessary count in this repository.  It
does not contradict nonnegativity of the two unknown cycle counts.

## 2. Every vertex clique has the same ternary sum

Reduce the endpoint reflection

```text
C=2M-21I
```

modulo three and take a symmetric rank factorization

```text
C=V H V^T.
```

Let `v_T` be the factor row indexed by graph triangle `T`.  For an original
graph vertex `x`, define

```text
w_x=sum_(T contains x) v_T.
```

The verified incidence calculation says that the entries of `M N^T` are

```text
4   if x lies in the base triangle,
-2  if x is adjacent to one of its vertices,
1   otherwise.
```

Twice all three values are `2 mod 3`.  Thus, for every triangle `U`,

```text
(v_U,w_x)=2.                                          (2)
```

The `v_U` span the nondegenerate factor space, so (2) implies that every
`w_x` is one common vector `w`.  The seven distinct triangles through one
vertex meet pairwise, hence their factor rows are mutually orthogonal.
Their norms are two, so

```text
(w,w)=7*2=2 mod 3.                                    (3)
```

Center the rows by

```text
z_T=v_T-w.
```

Equations (2)--(3) give

```text
(z_T,z_T)=0,
(z_T,w)=0,
(z_T,z_U)=C_TU+1.                                    (4)
```

Moreover,

```text
sum_(T contains x) z_T=w-7w=0.                       (5)
```

The `z_T` span `w`-orthogonal: the `v_T=z_T+w` span the full factor space,
while anisotropy of `w` keeps it outside the span of the `z_T`.  Since the
restriction to `w`-orthogonal is nondegenerate,

```text
D=C+J is the z-row Gram matrix,
rank_F3(D)=r3-1.                                      (6)
```

Thus each original vertex supplies seven isotropic rows with pairwise inner
product one and their unique displayed sum relation.  Their `7 x 7` Gram
matrix has exact rank six.

## 3. The nineteen-triangle local rank bridge

Fix a graph triangle `T={t0,t1,t2}`.  Besides `T`, six graph triangles meet
`T` at each `ti`, for a total of nineteen.

Contract each of those six triangles to the matching edge that it cuts out
in the twelve-point fibre `Xi`.  Between the six labels at `ti` and the six
labels at `tj`, the base edge `ti tj` already supplies one cross edge.
Every endpoint of a fibre matching edge has a unique neighbor in the other
fibre.  The possible second cross edges therefore form a bipartite
two-regular multigraph.  Prism-freeness says that no label pair receives two
such edges, so it is simple.

Let `P=P_T` be the union of the three bipartite blocks.  It is a simple
four-regular tripartite graph on `6+6+6` vertices.  In the order

```text
T | six through t0 | six through t1 | six through t2,
```

equation (4) gives the local Gram matrix

```text
        [ 0     1^T       ]
D_T  =  [ 1  J-I+P ].                                 (7)
```

Put `L=P-I`.  Modulo three, `L*1=0`.  If `e` is the indicator of one of the
three six-point parts, then

```text
L(2e)=1,
1^T(2e)=12=0 mod 3.                                   (8)
```

Equations (7)--(8), by elementary row and column elimination, give

```text
rank_F3(D_T)=rank_F3(P-I).                             (9)
```

Since `D_T` is principal in `D`, (6) and (9) imply the exact local-to-global
ceiling

```text
rank_F3(P_T-I)<=r3-1.                                 (10)
```

Consequently, forcing rank at least twelve for even one base triangle would
raise the endpoint bound to `r3>=13` and exclude the previously surviving
square rank-twelve case.

## 4. Exact rank-ten local control

The checker freezes a 36-row binary adjacency encoding and reconstructs it
without graph libraries.  Exact checks give:

```text
vertices / edges / degree:              36 / 54 / 3
connected / triangle-free:              yes / yes
within each fibre:                       perfect matching
between each pair of fibres:             perfect matching
same-fibre nonedge X-codegree:           0
cross-fibre nonedge X-codegree:          0,1,2 only
doubled quotient edges:                  none
component partition in fibre units:      [12]
rank_Q(required B B^T):                  34
minimum entry of required B B^T:         0
rank_F3(P-I):                            10
rank_F3(D_T):                            10
```

The required Gram is positive semidefinite.  On the two fibre-difference
vectors it is zero; on constants it has eigenvalue 60; and on the
33-dimensional orthogonal complement it is

```text
(3I-A_X)(4I+A_X).
```

Because `A_X` is a connected cubic graph, its spectrum lies in `[-3,3]`;
the displayed product is positive on that complement.  This also explains
the exact rational rank `34`.

An exhaustive `60^3` individual-column pass gives:

```text
induced-matching survivors: 183596
mixed-equation survivors:   152399

by internal X-edge count:
0:52517, 1:76540, 2:22610, 3:732.
```

These many surviving columns do not form a simultaneous design.  The
control's purpose is negative: a proof of the desired rank-twelve local
lemma must use information absent here.

## 5. Exact boundary

The smallest clean missing lemma exposed by this lane is:

> Every full simultaneous endpoint completion `(B,H)` forces at least one
> base triangle `T` with `rank_F3(P_T-I)>=12`.

The rank-ten control proves that one must use simultaneous 60-block
compatibility, the mixed and `Y-Y` equations with an actual `H`, or
compatibility among multiple base triangles.  One cannot derive the lemma
from the cubic one-triangle core, the exact local common-neighbor caps,
nonnegative/positive-semidefinite required `B B^T`, component balance, or
the individual-column mixed cut alone.

The exact regeneration passed and the focused suite reports:

```text
Ran 9 tests
OK
```

The derivations remain `DERIVED`, not `VERIFIED`, until a separate verifier
reconstructs them.  No literature novelty claim is made.
