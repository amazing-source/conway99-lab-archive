# Exact extension equations for the `C4 box K3` motif

Claim labels: `DERIVED` for the necessary equations, `CANDIDATE` for the
linear witness, and `UNKNOWN` for full extension.

## 1. Block equations

Let `H` be the adjacency matrix of the induced 12-vertex motif, let `P` be
the `87 by 12` outside-to-motif incidence matrix, and let `D` be the
adjacency matrix on the 87 outside vertices. A full target adjacency matrix
would be

```text
A = [H   P^T]
    [P    D ].
```

The strongly regular graph equation is

```text
A^2 = 12I-A+2J.
```

Its three block equations are

```text
H^2+P^T P = 12I-H+2J,                    (1)
D P+P H   = 2J-P,                        (2)
D^2+P P^T = 12I-D+2J.                    (3)
```

Equation (1) fixes the complete multiset of motif neighborhoods of the
outside vertices. There are exactly

```text
3 rows of weight 0,
48 rows of weight 1,
36 rows of weight 2.
```

Thus the outside types are `|X0|=3`, `|X1|=48`, and `|X2|=36`. There are
120 boundary incidences and 36 pair incidences.

## 2. Exact linear layer

Each outside vertex has outside degree `14-|N_H(v)|`. Equation (2) fixes,
for every outside vertex and every motif vertex, the exact number of
neighbors of each motif-incidence kind.

The archived [linear witness](linear-witness.json) is a 0-1 symmetric
87-vertex graph with 549 edges. It directly passes every degree equation
and all 1,044 distinct rows of (2). Its upper-triangle hash is

```text
feb948f5d0095b4baaba139fddda02b6ededcb7898e0d1ead3d2c251c6786fde
```

This is a genuine feasibility result for the entire linear layer. It is not
a target graph: equation (3), the outside-pair common-neighbor equation, is
not asserted for this witness.

## 3. Aggregate second moments

Write `t=e(X0)`. The three-vertex graph on `X0` has four isomorphism types,
so `t=0,1,2,3` is a complete encoding-symmetry split. Exact degree and
double-counting equations force the six type-edge counts:

```text
e00 = t          e01 = 12-4t       e02 = 30+2t
e11 = 156+4t     e12 = 300-4t      e22 = 51+t.
```

For an outside vertex of type `i` with `c` neighbors in `X2`, its neighbor
counts in `(X0,X1,X2)` are

```text
(c+4i-10, 24-5i-2c, c).
```

Summing the six unordered neighbor-pair moments leaves respectively

```text
18, 11, 5, 1
```

integer degree-histogram rows for `t=0,1,2,3`. Applying Erdős-Gallai to the
three induced type graphs and Gale-Ryser to the three bipartite type graphs
removes one row in the `t=2` branch, leaving `18,11,4,1`.

These are necessary aggregate conditions, not simultaneous graph
realisations.

## 4. Complete nonlinear encoding

For distinct outside vertices `i,j`, equation (3) is equivalent to

```text
D_ij + sum_k D_ik D_kj = 2-(P P^T)_ij.                (4)
```

The bounded solver encodes each conjunction `D_ik D_kj` in both directions
and imposes (4) as an exact cardinality row. Together with all degree and
incidence rows, this covers the full extension domain conditional on the
motif. It uses:

```text
3,741 outside-edge variables,
317,985 common-neighbor conjunction variables,
321,726 variables total.
```

All four 45-second branches returned `UNKNOWN_TIMEOUT`. The runs neither
construct an extension nor prove that none exists.

## 5. Mathematical boundary

The motif is therefore not eliminated by:

- induced `lambda/mu` caps;
- spectral interlacing;
- aggregate type moments and graphicality; or
- the complete linear block equation.

Any exclusion must use genuinely nonlinear compatibility in (3), a
stronger proof-producing formulation, or a new theorem that compresses
those pair constraints. Conversely, a full SAT model is accepted only
after direct replay of `A^2=12I-A+2J`.

No conclusion about the existence of `srg(99,14,1,2)` follows at this
checkpoint.
