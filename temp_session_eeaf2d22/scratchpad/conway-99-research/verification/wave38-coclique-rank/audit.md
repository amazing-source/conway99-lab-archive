# Wave 38 coclique-rank adversarial audit

Verdict: **PASS for the scoped universal and conditional implications**.

Every putative `srg(99,14,1,2)` has an independent set of size 13. Its
vertex-triangle incidence rows force

```text
rank_F7(M) >= 13.
```

At the conditional endpoint `n3=4158`, the reflection satisfies
`C=2M (mod 7)`, so `r7=rank_F7(C)>=13`. Combining this with the previously
verified parity `r3+r7` even gives

```text
r3=12  ==>  r7 is even and r7>=14.
```

This is a necessary restriction, not an endpoint contradiction. The endpoint,
Conway-99, and novelty remain `UNKNOWN`, and the general upper bound remains
`n3<=4158`.

## 1. The 13-coclique

Choose an edge `xy`. Because `lambda=1`, it has a unique common neighbor
`z`, so `xyz` is its unique triangle. Put

```text
X=N(x)\{y,z},   Y=N(y)\{x,z}.
```

Both sets have 12 vertices and they are disjoint: any vertex in both would be
a second common neighbor of `xy`.

For any neighbor `u` of `x`, its neighbors inside `N(x)` are exactly the
common neighbors of the adjacent pair `x,u`. There is exactly one. Thus
`G[N(x)]` is a perfect matching on 14 vertices. The edge `yz` is one matching
edge, so `G[X]` is a perfect matching on 12 vertices. Symmetrically, `G[Y]`
is another perfect matching.

The potentially dangerous step is the triangle mate. For the edge `xz`, the
vertex `y` is already its unique common neighbor. Therefore `z` has no
neighbor in `X`. The same argument with `yz` shows that `z` has no neighbor
in `Y`.

Now take `u in X`. It cannot be adjacent to `y`, because then it would be a
second common neighbor of `xy`. Hence `u,y` is a nonadjacent pair and has
exactly two common neighbors. One is `x`; the other cannot be `z` by the
previous paragraph and must lie in `Y`. It is unique. The symmetric argument
gives degree one from `Y` into `X`, so the cross edges form a perfect
matching.

The induced graph on `X union Y` is therefore exactly the union of the two
local matchings and the cross matching. Every vertex has one local and one
cross edge, so every component is a cycle with alternating edge types.
Returning to the starting side uses an even number of cross edges; hence
every cycle length is divisible by four. Alternating vertices around each
cycle gives an independent set containing exactly half of the 24 vertices.
Adding `z`, which is nonadjacent to all 24, gives a 13-coclique.

The checker normalizes the cross matching to the identity and exhausts all
`11!!=10,395` pulled-back local matchings on the second side. The only cycle
partitions are:

```text
24
20+4
16+8, 16+4+4
12+12, 12+8+4, 12+4+4+4
8+8+8, 8+8+4+4, 8+4+4+4+4
4+4+4+4+4+4
```

Every part is divisible by four and every alternating selection has size 12.
This finite census checks the parity step but is not needed in place of the
general proof.

## 2. Incidence-projector transport

Let `N` be the `99 x 231` vertex-triangle incidence matrix, `Gamma` the
triangle-intersection graph, and `E0` the orthogonal projector onto
`ker(Gamma)`. The exact incidence identities are

```text
N N^T=7I+A,
N^T N=3I+Gamma,
M=21E0.
```

The adjacency spectrum is `14^1,3^54,(-4)^44`, so `NN^T` has eigenvalues
`21,10,3` with the same multiplicities. Because
`N^T N=3I+Gamma`, `E0` is the projector onto the eigenvalue-three space of
`N^T N`. Singular-value transport through `N` sends it to the
eigenvalue-three space of `NN^T`, which is precisely the `A=-4` eigenspace.
On that space,

```text
N E0 N^T=3I,
```

and it vanishes on the other two adjacency eigenspaces. Thus

```text
N M N^T=63P_-4.
```

Solving `P_-4=alpha I+beta A+gamma J` on the three adjacency eigenspaces
gives

```text
P_-4=(27I-9A+J)/63.
```

Therefore

```text
N M N^T=27I-9A+J.
```

## 3. Rank transfer from the coclique

Restrict the preceding identity to the 13 independent vertices `I`. Since
`A[I]=0`,

```text
N_I M N_I^T=27I_13+J_13.
```

The all-one direction has eigenvalue `27+13=40`, while its 12-dimensional
orthogonal complement has eigenvalue 27. Hence

```text
det(27I_13+J_13)=27^12*40.
```

Modulo seven this is

```text
(-1)^12*5=5,
```

so the matrix has rank 13 over `F_7`. For matrices over any field,

```text
rank(N_I M N_I^T) <= rank(M).
```

Therefore `rank_F7(M)>=13`. This is a lower bound only; the verifier
explicitly rejects promotion to `rank_F7(M)=13`.

## 4. Endpoint consequence

At `n3=4158`, the previously verified reflection is

```text
C=2M-21I.
```

Modulo seven, `21I=0` and two is invertible, so

```text
C=2M,   rank_F7(C)=rank_F7(M)>=13.
```

The independently verified endpoint index constraint gives `r3+r7` even.
When `r3=12`, `r7` must therefore be even. The first even integer at least
13 is 14, proving the displayed conditional strengthening. With the
previously verified `12<=r3<=44`, the new ranges and parity leave 528
arithmetic rank pairs. They are survivors, not realizable endpoint matrices.

## 5. Hostile controls and status boundary

The ten-test suite rejects:

- a 12-vertex substitution for the proven coclique size;
- a determinant residue other than five;
- any coefficient mutation in `27I-9A+J`;
- promotion of the rank lower bound to an exact rank;
- an extra `z`-to-side edge;
- novelty/attribution inflation; and
- endpoint, upper-bound, or Conway-status inflation.

The 13-coclique was reported by the discovery lane as prior public
mathematics. This verifier did not perform a literature-priority audit and
makes no novelty claim.

Final scoped status:

```text
13-coclique implication:        VERIFIED
rank_F7(M)>=13:                 VERIFIED
endpoint r3=12 => r7>=14 even: VERIFIED CONDITIONAL
n3=4158:                        UNKNOWN
general upper bound on n3:      4158
Conway-99:                      UNKNOWN
novelty/priority:               UNKNOWN
```
