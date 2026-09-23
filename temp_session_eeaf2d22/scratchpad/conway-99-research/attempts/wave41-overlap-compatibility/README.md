# Wave 41 two-triangle overlap compatibility

Status: **CANDIDATE / exact bounded positive control**. The prism-free
endpoint and Conway-99 remain **UNKNOWN**.

This package tests the first genuinely overlapping pair of the new rank-33
one-triangle blocks. Start with the canonical Wave 41 lift around a base
triangle `T=(0,1,2)`. Its first fibre contains the matching edge `(3,4)`,
which forms the adjacent graph triangle

```text
T'=(0,3,4).
```

The two 39-vertex neighborhoods must overlap in 19 vertices: all 15 vertices
of `N[0]`, plus the four visible cross-fibre neighbors of `3` and `4`.

## Exact positive control

Two copies of the same canonical all-`222`, triangle-free, rank-33 local
block can be glued so that their induced graphs agree exactly on this
19-vertex overlap. Both principal `K39` blocks still have

```text
rank_F7(K39)=33.
```

Thus the induced overlap graph by itself does not rule out even the minimum
local rank case.

## Exhaustive first-order border census

The second block contributes twenty vertices outside the first block. For
each such vertex, the checker exhausts every choice of its still-unknown
neighbors in the first block subject to these necessary endpoint rules:

1. exactly two neighbors in each old 12-point fibre; and
2. the individual common-neighbor support cap: a selected old-core point has
   at most one selected core neighbor, and an unselected point has at most
   two.

Projecting each resulting Seidel column to the six-dimensional kernel of
the first `K39` gives a finite set of signatures. Dynamic programming over
the twenty signature sets gives exactly 70 terminal subspaces:

| signature-span dimension | subspaces |
| ---: | ---: |
| 1 | 13 |
| 2 | 56 |
| 3 | 1 |

The minimum is one, and the package emits an explicit simultaneous choice
attaining it. The symmetric border-congruence lemma therefore gives only

```text
rank >= 33 + 2*1 = 35,
```

far below the needed characteristic-seven contradiction.

## Precise boundary

The emitted 59-vertex object is a relaxation control. It fixes the two local
blocks and one individually admissible cross choice per new vertex, but it
does **not** impose:

- the simultaneous `BB^T` Gram matrix for all sixty outside vertices;
- pairwise compatibility among the twenty chosen columns;
- the eight-regular outside graph `H`;
- all SRG common-neighbor equations; or
- consistency across every rank-33 mask and every overlap class.

Consequently its union rank is diagnostic only. It is not a graph
construction and no sampled union rank is promoted to a theorem.

The useful lesson is sharp: the next overlap attack must couple columns
through `BB^T`, `BH`, and `B^TB+H^2`, or exhaust a complete overlap class.
The 19-vertex induced agreement and raw kernel signatures alone remain
compatible.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave41-overlap-compatibility\exact_check.py `
  --verify attempts\wave41-overlap-compatibility\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave41-overlap-compatibility -p "test_*.py" -v
```
