# Derivation

## 1. The outside Gram matrix

Write the target adjacency matrix in blocks around an induced subgraph `H`:

```text
A = [ H  B ]
    [B^T C].
```

The top-left block of

```text
A^2 = 12I - A + 2J
```

is

```text
H^2 + B B^T = 12I - H + 2J.
```

Hence

```text
M_H := B B^T = 12I - H + 2J - H^2.             (1)
```

If `H` is triangle-free and cubic on eight vertices, the diagonal of `M_H`
is `12+2-3=11`.  Its off-diagonal entry is one on an edge of `H` and
`2-c_H(i,j)` on a nonedge, where `c_H(i,j)` is the number of common
neighbors inside `H`.

For the cube:

```text
12 edge pairs:       M_ij=1
12 distance-2 pairs: M_ij=0
 4 antipodal pairs:  M_ij=2.
```

For the Wagner graph:

```text
12 edge pairs:              M_ij=1
 8 cyclic-distance-2 pairs: M_ij=1
 8 cyclic-distance-3 pairs: M_ij=0.
```

Both matrices therefore have total off-diagonal pair multiplicity 20 and
off-diagonal row sum 5.

## 2. Explicit local factors

For each unordered pair `{i,j}`, insert `M_ij` copies of the binary column
`e_i+e_j`.  Each row then occurs in five pair columns.  Insert six singleton
columns `e_i` for each row, raising its squared norm to 11.  Finally insert
23 zero columns.

The column counts are

```text
pair:       20
singleton:  48
zero:       23
total:      91.
```

Off-diagonal products are `M_ij` by construction and diagonal products are
`5+6=11`, proving `B B^T=M_H`.  A support of size at most two always induces
maximum degree at most one in `H`, so it is compatible with the matching
structure of a target neighborhood.

This is an exact primal obstruction to any argument using only the local
Gram matrix, row sums, pair codegrees, and matching-support rule: both motifs
survive.

## 3. The point--triangle incidence profile

Every edge of `H` lies in one unique target triangle.  Because `H` is
induced and triangle-free, the third point of each such triangle lies
outside `H`.  Thus 12 triangle columns meet `V(H)` twice.

Each point lies in seven target triangles.  Its three internal `H`-edges
account for three of them, leaving four triangles that meet `V(H)` only in
that point.  Across eight points this gives `8*4=32` size-one columns.
The remaining `231-12-32=187` triangle columns are disjoint from `H`.

No scalar moment of this profile distinguishes the cube from the Wagner
graph.

## 4. Why the line graph is not yet enough

Associate to every edge of `H` its completing target triangle.  Two such
triangle nodes meet whenever the original `H`-edges share an endpoint, so
their triangle-intersection graph contains `L(H)`.

If two disjoint edges of `H` have completing triangles with the same outside
apex, the corresponding triangle nodes acquire an additional edge.  These
apex collisions are invisible in (1).  A line-graph interlacing argument
must either control them or retain them as explicit variables.

## 5. Induced 5-cycles as the first distinguishing shell

The cube is bipartite and has no induced 5-cycle.  The Wagner graph has eight:
each of its four opposite chords closes either of the two length-four paths
between its endpoints.

For an induced 5-cycle `F`, the same block calculation gives

```text
M_F = 12I - A_F + 2J - A_F^2 = 11I+J.
```

It too has an explicit binary factor: one column for each of the ten
unordered vertex pairs, eight singleton columns per row, and 44 zero
columns, for `10+40+44=94` outside columns.

The factor again omits outside adjacency.  A Wagner extension selects two
outside columns completing disjoint diagonals of `F` and a third outside
column forming the middle of a path between them while meeting the leftover
cycle vertex.  Since every Wagner graph contains eight induced 5-cycles,
double counting gives equation (2) in the README.

The next model should therefore retain the adjacency matrix on these
distinguished outside columns.  A lower bound on the extension sum in (2),
combined with a separately certified cube bound, is a concrete route toward
`W8-3*C8>=9356`.

