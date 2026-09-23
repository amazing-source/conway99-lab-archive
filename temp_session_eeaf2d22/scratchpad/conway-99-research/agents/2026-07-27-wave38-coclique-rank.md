# Wave 38 coclique and characteristic-seven rank strengthening

```yaml
role: proof_a
date_utc: 2026-07-27T01:16:58Z
git_commit: 3014f3b1c010cdde1687b8878d4ec58d2bb90f03
claim_label: CANDIDATE
scope: >
  A necessary characteristic-seven rank condition for every hypothetical
  srg(99,14,1,2), and its conditional consequence at n3=4158.
method: >
  Combine a public 13-coclique construction with the integral
  triangle-projector identity, then restrict the resulting Gram matrix and
  calculate its determinant exactly modulo seven.
limitations:
  - The 13-coclique construction is prior public mathematics.
  - The combined rank consequence is pending independent verification.
  - No endpoint matrix, graph, contradiction, or upper-bound improvement is supplied.
  - Novelty and priority remain UNKNOWN.
```

## Result

Every hypothetical Conway 99-graph contains an independent set of size
thirteen.  If `M=21E_0` is the integral rank-44 projector on the zero
eigenspace of the triangle-intersection graph, then

```text
rank_F7(M) >= 13.                                  (1)
```

The previous project floor was eleven.  At the conditional prism-free
endpoint, `C=2M-21I` is congruent to `2M` modulo seven, so

```text
rank_F7(C) >= 13.                                  (2)
```

Together with the previously verified parity condition

```text
rank_F3(M)+rank_F7(M) is even,
```

this says that the surviving ternary equality case `rank_F3(M)=12` requires
`rank_F7(M)>=14`.

These are necessary restrictions only.  They do not exclude `n3=4158`, so
the general bound remains `n3<=4158`.

## 1. A forced 13-coclique

Let `xy` be any edge and let `z` be its unique common neighbor.  Put

```text
X = N(x) \ {y,z},
Y = N(y) \ {x,z}.
```

Both sets have twelve vertices.  The local graph on `N(x)` is seven
disjoint edges: every neighbor of `x` has exactly one neighbor inside
`N(x)`, because adjacent pairs have exactly one common neighbor.  One of
those edges is `yz`, so `X` carries a perfect matching.  The same argument
gives a perfect matching on `Y`.

No point of `X` is adjacent to `y`, since otherwise the edge `xy` would have
a second common neighbor.  For `a in X`, the nonedge `ay` has exactly two
common neighbors.  One is `x`; the other is a unique vertex of `Y`.
Symmetry shows that these unique vertices form a perfect matching between
`X` and `Y`.

On the 24 vertices `X union Y`, combine the two local matchings with this
cross matching.  Every vertex has degree two.  Edges alternate between a
local edge and a cross edge.  Any closed walk returns to the same fibre only
after an even number of cross edges, so every component cycle has length
divisible by four.  The graph is bipartite and either color class contains
twelve vertices.

Finally, `z` is adjacent to none of `X union Y`: in `N(x)` its unique
neighbor is `y`, and in `N(y)` its unique neighbor is `x`.  Adding `z` to a
twelve-point color class gives a 13-coclique.

The exact checker enumerates the eleven integer partitions of six, which
are the normal forms for the alternating cycle half-lengths, and verifies a
twelve-point independent color class in every form.  This finite control
accompanies the general proof; it does not replace it.

This construction was publicly described by Misha Lavrov in a 2025
Mathematics Stack Exchange discussion.  No novelty is claimed for it.

## 2. The triangle-projector identity

Let `N` be the 99-by-231 vertex-triangle incidence matrix.  Every vertex is
in seven graph triangles, adjacent vertices share one graph triangle, and
nonadjacent vertices share none.  Therefore

```text
N N^T = 7I + A.                                   (3)
```

The triangle-intersection adjacency matrix is

```text
Gamma = N^T N - 3I.
```

Its zero eigenspace is the image under `N^T` of the `-4` eigenspace of `A`.
If `E_0` projects onto that 44-dimensional space and `M=21E_0`, then

```text
N M N^T = 63 E_{-4}(A).                           (4)
```

The spectral projector of `A` onto eigenvalue `-4` is

```text
E_{-4}(A) = (A-14I)(A-3I)/126.
```

Using `A^2=12I-A+2J` in (4) gives the exact integer identity

```text
N M N^T = 27I - 9A + J.                           (5)
```

## 3. Restriction to the coclique

Let `I` now denote the thirteen vertices of the coclique and let `N_I` be
the corresponding thirteen rows of `N`.  Since the off-diagonal entries of
`A_I` vanish, (5) becomes

```text
N_I M N_I^T = 27 I_13 + J_13.                     (6)
```

For a matrix `aI+bJ` of order `m`, the all-one direction has eigenvalue
`a+bm` and its orthogonal complement has eigenvalue `a`.  Consequently

```text
det(27I_13+J_13) = 27^12 (27+13)
                  = 27^12 * 40
                  = 5 (mod 7).                    (7)
```

The Gram block (6) is therefore nonsingular over `F_7`.  Because

```text
rank(N_I M N_I^T) <= rank(M)
```

over every field, (1) follows.

## 4. Exact replay and boundary

The standard-library discovery suite passes eight tests and records:

- all eleven alternating-cycle normal forms;
- an independent twelve-set in every form;
- the exact matrix `27I_13+J_13`;
- its determinant residue five and rank thirteen modulo seven;
- the projector polynomial on all three adjacency eigenspaces; and
- conservative status fields retaining the endpoint and target as unknown.

At the discovery freeze, the result was awaiting a separately written
verifier. Even after verification its exact scope remains:

```text
rank_F7(M)>=13:                 candidate
rank_F7(C)>=13 at n3=4158:      candidate
n3=4158:                        UNKNOWN
general upper bound:            n3<=4158
Conway-99:                      UNKNOWN
novelty:                        UNKNOWN
```

## Independent-verification addendum

The separate verifier subsequently returned `PASS_SCOPED` after reconstructing
the proof without importing discovery code and exhausting all 10,395 local
matching states. Its ten hostile tests pass. The promoted consequences are

```text
13-coclique implication:        VERIFIED
rank_F7(M)>=13:                 VERIFIED
endpoint r3=12 => r7>=14 even: VERIFIED conditional
remaining arithmetic rank pairs: 528
```

The endpoint, general bound, target, and novelty statuses are unchanged. See
`verification/wave38-coclique-rank/audit.md`.
