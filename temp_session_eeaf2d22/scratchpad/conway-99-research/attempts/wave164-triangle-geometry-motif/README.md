# Wave164 draft: triangle geometry and cubic eight-sets

Status: `DRAFT_UNEXECUTED`.

This package was prepared while host free memory was below the user-mandated
15 percent floor.  Its checker has deliberately **not** been run.  Nothing in
this directory is `VERIFIED`, and no manifest or run report is supplied yet.

## Exact reduction prepared for replay

Let `H` be an induced triangle-free cubic graph on eight vertices in a
hypothetical `srg(99,14,1,2)`.  Ordering the vertices of `H` first gives

```text
A = [ H  B ]
    [B^T C].
```

The strongly regular graph identity implies

```text
B B^T = 12 I - H + 2 J - H^2.                 (1)
```

For both the 3-cube and the Wagner graph, the right side has diagonal 11 and
off-diagonal row sum 5.  The draft checker constructs an explicit binary
`8 by 91` factor for each graph:

- one pair column `e_i+e_j` for every unit off-diagonal entry;
- two such columns for every off-diagonal entry equal to two;
- six singleton columns `e_i` per row;
- 23 zero columns.

There are 20 pair columns and 48 singleton columns.  Every column support
induces a matching in `H`, as required by the fact that every neighborhood
of the target is `7 K2`.

Consequently the local binary Gram equation, row sums, pair codegrees, and
matching-support condition are feasible for **both** motifs.  These
first/second-moment conditions cannot prove the missing comparison

```text
W8 - 3*C8 >= 9356.
```

## Incidence-geometry translation

Each of the 12 edges of `H` lies in a unique target triangle.  In the
point-versus-triangle incidence graph, the eight selected points therefore
have the same triangle-column profile for both motifs:

```text
intersection size 2:  12
intersection size 1:  32
intersection size 0: 187
```

The 12 completing triangle nodes contain the line graph `L(H)`.  Additional
edges can occur when completing triangles of disjoint `H`-edges share the
same outside apex.  Those collisions, and adjacency among the outside
columns of `B`, are not encoded by equation (1).

## Next-order target

The Wagner graph has eight induced 5-cycles; the cube has none.  For a fixed
induced 5-cycle `F`, its outside block satisfies

```text
B_F B_F^T = 11 I + J.
```

A Wagner extension of `F` is controlled by adjacency among three outside
columns: the two endpoint columns complete two disjoint diagonal pairs of
`F`, and a middle column joins those endpoints while meeting the remaining
cycle vertex.  Double counting pairs `(Wagner copy, induced 5-cycle in it)`
gives

```text
8*W8 = sum_F extensions_to_Wagner(F).          (2)
```

Equation (2) identifies a graph-valued next layer.  A useful continuation
must bound these outside-column adjacencies, not repeat scalar incidence
moments or the feasible Gram factor.

## Reproduction gate

When free host memory is safely above 18 percent:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B `
  attempts\wave164-triangle-geometry-motif\exact_check.py
```

After that run, the result still requires an independent verifier before any
claim can be promoted.

