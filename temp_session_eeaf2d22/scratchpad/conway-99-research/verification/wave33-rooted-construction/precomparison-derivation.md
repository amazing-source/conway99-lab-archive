# Wave 33 rooted construction: clean-room precomparison derivation

This note, `independent_check.py`, its adversarial tests, and the first
machine-readable result were written before inspection of the Wave 33 rooted
construction discovery package.  The only inputs were the public Wave 32
rooted support conclusion and the frozen claim synopsis.

## Public support reconstruction

Write the signed support as two seven-sets `P,N`.  Their cross adjacency `C`
is the public symmetric `2-(7,4,2)` design.  The 70 support-adjacent outside
labels `O` are forced as follows:

- a cross support edge has one `O` label adjacent to its endpoints;
- a cross support nonedge has two such `O` labels.

Thus the exact support/O incidence matrix `B` is `14 x 70`, every row has
degree 10, and every column has degree 2.  Together with the support
adjacency, it independently satisfies the support block of

```text
A^2 = 12 I - A + 2 J.
```

No outside-vertex automorphism is assumed; all 70 labels are retained.

## Necessary O-Q equations

The remaining 15 support-isolated vertices are denoted `Q`.  Let

```text
F = O-Q incidence,  70 x 15,
D = O-O adjacency,  70 x 70.
```

If every row of `F` has degree 3, every column has degree 14, and every pair
of columns intersects twice, then

```text
F^T F = 12 I + 2 J.
```

Equivalently, the 70 row supports of `F` are a simple `2-(15,3,2)` design
when no row repeats.  This exactly supplies the `Q-Q` block equation and
saturates every `Q` degree, forcing the `Q-Q` adjacency block to be zero.

The support/Q block independently requires all 210 integer equations

```text
B F = 2 J_(14 x 15).
```

These equations are not implied by the design parameters.  A valid
`2-(15,3,2)` design with a nonzero `BF-2J` defect is therefore an exact
hostile partial object, not a graph construction.

If `D` is empty, each `O` vertex has only

```text
2 support neighbors + 3 Q neighbors = 5
```

neighbors, while all 14 support vertices and all 15 `Q` vertices have degree
14.  The resulting degree histogram is `5^70,14^29`, so it fails the full
matrix certificate immediately.  Even after `BF=2J`, a complete extension
would still need a 9-regular `D` satisfying the remaining exact block
equations, including

```text
C B + B D = 2 J - B,
D F = 2 J - F,
B^T B + D^2 + F F^T = 12 I - D + 2 J.
```

## Restricted MILP boundary

For one fixed simple design with 70 distinct blocks, variables
`x[o,block]` together with 70 row-sum and 70 column-sum equalities encode
exactly the `70!` bijections from those blocks to the fixed `O` labels.
Adding the 210 support-point equations encodes `BF=2J` for that one design.

This does not range over other nonisomorphic simple `2-(15,3,2)` designs.
A 25-second SciPy/HiGHS status-1 time limit with no primal proves neither
feasibility nor infeasibility of even that restricted instance.  Since no
balanced `F` was returned, no active `D` phase was entered.

## Precomparison fixture boundary

`precomparison-fixture.json` uses an independently generated union of two
disjoint Steiner triple systems on 15 points and the identity block
assignment.  It is deliberately a checker fixture, not the submitted hostile
object.  The checker recomputes that this fixture is a simple
`2-(15,3,2)` design but has 146 `BF=2J` violations with squared defect 444
and empty `D`.  The purpose is to freeze the validator and its status gates
before candidate release; those fixture numbers make no claim about the
discovery bytes.
