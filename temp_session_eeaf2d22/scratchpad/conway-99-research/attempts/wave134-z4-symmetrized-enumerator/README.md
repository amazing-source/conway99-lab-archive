# Wave134: full-problem quaternary-code checkpoint

Claim label: `DERIVED` for the exact conditional algebra and forced counts;
`UNKNOWN` for rational/integral feasibility and every realization claim.

This lane uses only the full `srg(99,14,1,2)` equations. It assumes no rank
endpoint, symmetry, motif, root, or value of `n3`.

## Exact checkpoint

The audited Smith data replay uniquely as

```text
SNF(A)=diag(1^45,3^9,6,12^43,84).
```

Thus

```text
C=row_Z4(A): type 4^54 2^1, order 2^109,
Cperp:       type 4^44 2^1, order 2^89.
```

The full-support word `2*1` is the extra order-two word in both codes.
Translation by it proves exact enumerator symmetry

```text
(n0,nodd,n2) <-> (n2,nodd,n0).
```

The raw 5,050-state symmetrized MacWilliams transform reduces to 1,119
primal orbits, 1,114 allowed dual orbits, and 161 exact dual zero orbits.
Each transform coefficient is generated sparsely as a product of two
integer Krawtchouk coefficients.

## Graph-forced words

The collision-checked primal table includes:

- signed rows, doubled rows, and torsion translates;
- every coefficient pattern in `{1,2,3}^S` on supports `|S|<=3`,
  including signed, doubled, and mixed odd/even patterns;
- all six exact Wave131 triple types.

Its 42 symmetry-orbit lower bounds (84 expanded compositions) represent
exactly 8,557,760 distinct words.

For the dual, `q_u+q_v` and `q_u-q_v` are both present and are distinct.
Their compositions are

```text
edge:     (72,24,3) and (75,24,0),
nonedge:  (71,26,2) and (73,26,0).
```

All even-sum coefficient patterns through three closed rows are included.
The resulting 22 dual orbits (44 expanded compositions) represent exactly
4,126,784 words.

## Search outcome

No exact rational primal and no exact Farkas certificate was obtained.
The provisional searches below used the earlier narrower 26/8-orbit table
and were invalidated before sealing:

- the complete exact rational system reached its 300-second hard wall;
- a floating-point HiGHS support pass ended in `Solve error` after severe
  coefficient-range warnings;
- a reduced exact solve with all 157 zero rows and only eight forced dual
  inequalities reached its 180-second hard wall in its first solve.

They make no claim about the corrected 42/22-orbit system. Corrected
rational and integral feasibility are `UNKNOWN_NOT_RUN`; none of the stale
outcomes is evidence for infeasibility.

The next exact boundary is to eliminate the 161 zero rows by rational linear
algebra in the symmetrized character basis, then run a cutting-plane solve in
the smaller affine face. This is a computational representation issue, not a
mathematical contradiction.

## Reproduction

```powershell
python -B attempts\wave134-z4-symmetrized-enumerator\exact_check.py `
  --verify attempts\wave134-z4-symmetrized-enumerator\exact-results.json

python -B -m unittest discover `
  -s attempts\wave134-z4-symmetrized-enumerator `
  -p "test_*.py" -v
```

No quaternary code, adjacency matrix, or graph is constructed. Conway-99,
integral feasibility, and novelty remain `UNKNOWN`.
