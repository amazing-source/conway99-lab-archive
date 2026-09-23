# Wave 33 rooted construction protocol freeze

Frozen before any Wave 33 sibling-package inspection or construction search.
Base commit: `b2595baa40d50e9c259051751fe27090bee6a449`.

## Exact labeled continuation domain

Fix two labeled support sets

```text
P={P0,...,P6}, R={R0,...,R6}.
```

Identify labels `0,...,6` with the nonzero vectors `1,...,7` in `F_2^3`.
Define the already-forced support cross-incidence matrix by

```text
C[p,r]=1 iff popcount((p+1)&(r+1)) is odd.
```

Thus `C` has row and column sums four and is the complement of a labeled
Fano-plane incidence matrix. There are no same-sign support edges.

Label the remaining 85 vertices without quotienting by any automorphism:

```text
E[p,r]             for each C[p,r]=1                 (28 vertices);
N[p,r,copy]        for each C[p,r]=0, copy in {0,1} (42 vertices);
Z[j]               for j=0,...,14                   (15 vertices).
```

Both `E[p,r]` and `N[p,r,copy]` are adjacent to exactly `Pp` and `Rr`
inside the support. Each `Z[j]` has no support neighbor. Let `A_S` be the
fixed 14-by-14 support adjacency and `B` the fixed 14-by-85
support-to-outside incidence matrix.

The only unknown is a symmetric binary 85-by-85 matrix `D` with zero
diagonal. The complete 99-vertex adjacency is

```text
A = [[A_S, B],
     [B^T, D]].
```

A complete target-extension witness is an exact edge list for `D` for which

```text
A 1 = 14 1,
A^2 = 12 I - A + 2 J.
```

Equivalently, after the already-checked support-support block, the exact
remaining equations are

```text
D 1 = 14 1 - B^T 1,
A_S B + B D = -B + 2 J_(14x85),
B^T B + D^2 = 12 I_85 - D + 2 J_85.
```

These equations are the complete finite labeled domain. Fixing this labeled
representative loses no solutions because Wave 32 already proved that every
rooted support is isomorphic to this design. No outside orbit, stabilizer,
lexicographic representative, or graph automorphism is assumed.

## Certificate standards

- A positive certificate is a complete machine-readable outside edge list.
  A standard-library checker must reconstruct all 99 vertices and verify
  every degree and every ordered matrix-square entry.
- A negative certificate must cover the complete finite domain above and be
  accepted by an independently checkable proof format. A timeout, solver
  exit code, restricted search, or absent witness is not nonexistence.
- Any proper subset of the equations or additional restriction is a bounded
  relaxation and must name every omitted equation and restriction.
- Partial objects may demonstrate consistency of a subset only. They are not
  extendibility evidence.

Initial status:

```text
complete target extension: UNKNOWN
complete-domain UNSAT certificate: NONE
rooted n3=708 endpoint: UNKNOWN
Conway-99 existence/nonexistence: UNKNOWN
novelty: UNKNOWN
```
