# Wave 41 multi-edge rank packing

Status: **CANDIDATE scoped result; universal target unresolved**.

This package asks whether the independently verified Wave 40 theorem

```text
rank_F7(M) >= 25
```

can be strengthened by restoring the full matching in the third fibre or by
packing several overlapping triangle blocks. It produces one scoped
improvement and one exact obstruction:

```text
If some graph edge has an all-odd alternating partition, then
rank_F7(M) >= 26.                                      (1)

Every 39-point triangle block has a three-dimensional kernel subspace
whose vectors are already killed by all 60 outside columns. (2)
```

The four all-odd types in (1) are

```text
1+1+1+1+1+1,  1+1+1+3,  1+5,  3+3.
```

The seven types containing an even part remain unresolved. Consequently this
package does **not** improve the unconditional rank floor 25.

## 1. Full three-fibre normal form

Fix a graph triangle and write its three twelve-point outside-neighbour
fibres as `X,Y,Z`. Each fibre induces a perfect matching, and each pair of
fibres is joined by a perfect matching. After local relabelling, let

```text
P = standard matching on X,
Q = matching on Y,
R = matching on Z,
F = permutation matrix for the Y-Z matching,
```

with both `X-Y` and `X-Z` matchings normalized to the identity. This is a
local coordinate choice, not an automorphism assumption.

For the cubic 36-point core adjacency matrix `A_core`, put

```text
L = 3I - A_core  over F7.
```

The exact Wave 40 identity, reconstructed here for all eleven types, is

```text
rank_F7(K39) = 1 + rank_F7(L),                       (3)
```

where `K39` is the principal `J-I-2A` block on the triangle and its 36
outside neighbours.

## 2. Excluding rank 25 for all-odd types

The `X-X` diagonal block of `L` is `3I-P`, with exact inverse

```text
(3I-P)^(-1) = 3I+P                                  (4)
```

because `(3I-P)(3I+P)=8I=I` in `F7`. Eliminating the `X`
coordinates leaves, up to multiplication by `-1`,

```text
H = [ P+Q       F+(3I+P) ]
    [ F^T+(3I+P)   P+R   ].                         (5)
```

When every part of the alternating partition of `(P,Q)` is odd, `P+Q` is
invertible. A rank-25 equality in (3) would therefore force the entire
Schur complement in (5) to vanish:

```text
P+R = (F^T+3I+P)(P+Q)^(-1)(F+3I+P).                 (6)
```

The left side has zero diagonal. For every one of the four canonical
all-odd types, the checker exhausts the `12*12=144` possible
`(F`-preimage, column) pairs and tests the required diagonal quadratic form.
This is complete because each column of a permutation has exactly one
preimage.

- Types `1^6`, `1^3+3`, and `1+5` each have a column with no admissible
  preimage.
- Type `3+3` has exactly one admissible preimage in every column. These
  preimages form one permutation, but (6) then forces an `R` containing
  field entries `2` and `3`, not a zero-one perfect matching.

Thus the fully specified 39-block has rank at least 26 for all four types.
The transport `rank_F7(M)=rank_F7(J-I-2A)` makes (1) the candidate global
consequence. Discovery cannot promote it to `VERIFIED`.

## 3. Why the obvious border packing fails

Let `A` now denote the 99-vertex graph adjacency matrix and

```text
K=J-I-2A.
```

For every graph vertex `v`, define

```text
h_v = (A+4I)e_v.
```

It has value four at `v`, value one on the fourteen neighbours of `v`, and
zero elsewhere. The strongly regular identity

```text
A^2=12I-A+2J
```

gives the exact integer polynomial calculation

```text
(J-I-2A)(A+4I)=14J-7A-28I,
```

so

```text
K h_v=0  over F7.                                   (7)
```

If `v` lies in a triangle `T`, the entire support of `h_v` lies in the
39-point block `T union (N(T)-T)`. The three vectors belonging to the three
vertices of `T` are independent: on `T` their matrix has diagonal four and
off-diagonal one, which has rank three over `F7`.

They are also killed by every outside column. An outside vertex is
nonadjacent to all three vertices of `T` and has exactly two neighbours in
each twelve-point fibre. Against `h_v`, the exact integer dot product is

```text
(4+1+1) + (10-2) = 14 = 0 mod 7.                    (8)
```

Therefore, if `H` is any basis matrix for the kernel of the 39-block and
`U` is its `39*60` border, then

```text
dim ker(H^T U) >= 3.                                (9)
```

This is the precise obstruction to a naive use of the symmetric-border
lemma. The local kernel directions are not independent resources belonging
to different blocks: they are the globally repeated vertex-star columns
`(A+4I)e_v`. Any successful multi-block proof must quotient or couple these
directions explicitly.

## 4. Exact low-rank controls

Two fully specified three-fibre controls delimit what a one-triangle proof
can claim.

| control | core components | core triangles | `nullity_F7(3I-A_core)` | `rank_F7(K39)` |
| --- | --- | ---: | ---: | ---: |
| generic | `12+12+12` | 6 | 9 | 28 |
| locally prism-free | `18+18` | 0 | 8 | 29 |

The first is valid forced matching data but contains local prisms. The second
has a triangle-free core and is therefore compatible with the one-triangle
prism-free condition. Neither includes the remaining 60 vertices, and
neither is a partial or completed Conway graph.

These controls show that forced 39-point data alone cannot prove a universal
floor above 28 or a prism-free local floor above 29. Global compatibility
could still force larger ranks.

## 5. Seven-star 49-block route

Greedy deletion guarantees an independent seven-set in any 14-regular graph
on 99 vertices. Its seven disjoint vertex-stars give 49 graph-triangle
indices. At the prism-free endpoint, their diagonal `7*7` blocks in `M` are
`4I`; every pairwise cross block has row and column sums

```text
(-2,-2,1,1,1,1,1)
```

after labelling the two common-neighbour triangles. Since
`rank_Q(M)=44`, the assembled 49-block must have nullity at least five.

This is a sharp finite target, not a result. The 21 pair blocks cannot be
chosen independently: they reuse graph edges, common-neighbour vertices, and
triangle labels, and the completed matrix must satisfy `M^2=21M`. Wave 35
only supplies a relaxation for one pair. This package found no exact gluing
model or contradiction.

## 6. Boundary

The current status after this lane is:

```text
all-odd edge type => rank_F7(M)>=26: CANDIDATE
universal rank_F7(M)>=26:             NOT PROVED
universal verified rank floor:        25
endpoint n3=4158:                     UNKNOWN
general upper bound on n3:            4158
Conway-99:                             UNKNOWN
novelty/priority:                      UNKNOWN
```

The remaining exact finite question is whether any of the seven even-part
types admits rank 25 after the `Z-Z` perfect matching is imposed. No
rank-25 positive control and no complete exclusion certificate was obtained.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave41-multiedge-rank-packing\exact_check.py `
  --verify attempts\wave41-multiedge-rank-packing\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave41-multiedge-rank-packing -p "test_*.py" -v
```

The stored JSON is regenerated byte for byte, and the ten discovery tests
must pass.
