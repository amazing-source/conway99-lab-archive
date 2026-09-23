# Wave 31 failed routes and hostile controls

## Superseded local tensor route

Before the incidence commutator was found, the surviving Wave 30 split was
attacked blockwise.  On the rank-24 block,

```text
B_U=I  ==>  K_U=I  ==>  A4_U=M_U W_U M_U=M_U.
```

Thus every one of its 126 diagonal entries is four.  With
`q_i=12-c_i`, tensor Cauchy gives

```text
[6(q_i-2)]^2<=4*16,
```

so `q_i` lies in `{1,2,3}`.  The independently verified graph-local gap
`q_i!=1` leaves `{2,3}`.  Since the block cubic trace gives
`sum_U q_i=256`, the aggregate profile is uniquely

```text
122 rows q=2 (c=10),
  4 rows q=3 (c=9),
  0 rows q=1 (c=11).
```

This sharpens the 62 Wave 30 count profiles to one, but it does not construct
or exclude a symmetric `M_U`.  The commutator theorem supersedes this route
by excluding the whole rootless decomposable split before any Schur-block
profile is needed.

## Scalar characteristic data do not close the rank-20 block

All global `C` invariants lie on the rank-20 block because `C_U=0`.
The inherited facts give

```text
tr(C_A)=8,
tr(C_A^2)>=10,
det(B_A)=3645.
```

The local Smith data are compatible with

```text
SNF(S_A)=1^14,3^6,
SNF(Q_A)=1^19,5,
SNF(B_A)=1^14,3^5,15.
```

The scalar hostile spectrum

```text
spec(C_A)={0^13,1^6,2},
spec(B_A)={1^13,3^6,5}
```

has the required traces, determinant, modular nullities, and
`tr(C_A^2)=10`.  It is not a matrix or lattice construction, but it prevents
an unsupported claim that the Smith data or lower trace-square bound alone
give a contradiction.  No upper bound `tr(C_A^2)<=10` was obtained, and no
integer spectrum is assumed in the published proof.

## Essential scope walls

1. **Actual graph incidence is stronger than the abstract endpoint matrix
   package.**  The new proof uses the vertex-triangle incidence matrix `N`,
   the target adjacency matrix `A`, the triangle-intersection matrix
   `Gamma`, and the fact that every adjacent pair has one common neighbor
   completing its unique graph triangle.  A free-standing abstract
   `X,M,S,Q,B` package with the same scalar identities need not carry this
   transport.

2. **Rootlessness is essential.**  Minimum four makes every norm-four frame
   row live in one integral orthogonal block.  If two blocks have norm-two
   vectors, a row can split as `2+2`; then `M` and `E=M/21` need not be
   coordinate-block diagonal and the sign matrix `D` need not commute with
   `E`.

3. **The edge signs must come from triangle signs.**  For adjacent `x,y`,
   the only common neighbor `z` completes their triangle, so

   ```text
   (ZA-AZ)_xy=Z_xz-Z_zy=0.
   ```

   Mutating the two edge signs to `+1,-1` makes this contribution two.  The
   transported equation then permits `d_x-d_y=-3`, so the constant-degree
   conclusion disappears.  The exact checker retains this mutation.

4. **Symmetry of `K` is active.**  Preservation of the `-4` eigenspace alone
   does not make an arbitrary operator commute with its orthogonal
   projector.  Here `K=NDN^T` is symmetric, so it also preserves the
   orthogonal complement.

5. **A multiple of 33 is not a construction.**  The sizes
   `0,33,...,231` are only necessary for a commuting coordinate sign
   involution.  No nontrivial such involution, projector, frame, or graph is
   asserted to exist.

6. **The theorem does not classify determinant-729 lattices.**  It excludes
   their rootless integrally decomposable endpoint origin.  Rooted forms,
   rootless indecomposable forms, rational decompositions, and bare lattices
   without target-graph origin remain outside scope.

## Status boundary

```text
nontrivial rootless integral orthogonal endpoint split: DERIVED IMPOSSIBLE
Wave 30 rank-20 plus rank-24 decomposable boundary:     DERIVED IMPOSSIBLE
rooted endpoint forms:                                  UNKNOWN
rootless indecomposable endpoint forms:                 UNKNOWN
n3=708, Conway-99, and novelty:                         UNKNOWN
```
