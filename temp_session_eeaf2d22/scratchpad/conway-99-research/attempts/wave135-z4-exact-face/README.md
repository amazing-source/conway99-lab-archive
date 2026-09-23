# Wave135: exact affine-face reduction

Claim label: `DERIVED` for the exact rank and dependency certificates;
`UNKNOWN` for rational/integral enumerator feasibility and every realization
claim.

This checkpoint continues the corrected Wave134 full-problem symmetrized
`Z4` weight-enumerator lane. It assumes no endpoint rank, graph automorphism,
rooted motif, or value of `n3`.

## Exact result

The 161 forbidden dual-orbit equations form an integer matrix with 1,119
primal-orbit columns. Exact rational row reduction gives

```text
rank_Q(forbidden rows) = 143
nullity_Q              = 976
```

The 18 row dependencies are explicit primitive integer relations in
`face-rank.json`. They split as follows:

```text
dual b=2:  49 rows, rank 44, 5 dependencies
dual b=4:  48 rows, rank 44, 4 dependencies
dual b=6:  47 rows, rank 44, 3 dependencies
dual b=92: 4 rows, rank  1, 3 dependencies
dual b=94: 3 rows, rank  1, 2 dependencies
dual b=96: 2 rows, rank  1, 1 dependency
```

Thus `5+4+3+3+2+1=18`. In the three high shells, the displayed rows are
literal scalar multiples on the restricted primal orbit domain. In each low
shell, the last target compositions are exact linear combinations of the
first 44.

Adding normalization and `A_0=1` raises the affine rank to 145. The independent
torsion-shell identity

```text
sum A_(a,0,c) = 2^54
```

raises it once more to 146, leaving an exact affine dimension of
`1119-146=973`. Coefficient and augmented ranks agree, so the equalities alone
are consistent.

## Exact search

The row generator translates the 42 forced primal lower bounds out:

```text
x = lower + z,    z >= 0.
```

It then uses only 143 independent forbidden rows, normalization, `A_0=1`, and
the torsion-shell identity. The 22 forced dual lower rows are loaded first.
After each exact GMP-rational LP solve, every one of the 1,119 primal and
1,114 allowed dual inequalities is replayed and the most violated rows are
added.

The original unshifted run is preserved in
`row-generation-unshifted.json`. It reached its 180-second wall after five
replays and ended with 451 violated inequalities. This is `UNKNOWN_WALL`, not
an infeasibility result.

The final shifted-run classification is recorded in `search-status.json`.
Only a witness that passes independent exact replay of all inequalities and
all 161 forbidden rows may be labelled `EXACT_RATIONAL_FEASIBLE`. No solver
status or truncated trace is a certificate.

## Why this representation is useful

The problem is now the intersection of a 973-dimensional rational affine
space with a polyhedral cone. There are two natural continuation spaces:

1. **Primal cone:** continue exact row generation and search for one rational
   enumerator.
2. **Dual cone:** search for an exact Farkas multiplier, a nonnegative weighted
   combination of inequalities that contradicts the affine right-hand side.

The dual route is attractive because a contradiction can be sparse even when
every primal feasible point would be dense. A separate complementary route is
to add further exact code identities (higher moments or split enumerators),
each of which can reduce the 973-dimensional face before another LP solve.

## Reproduction

```powershell
python -B attempts\wave135-z4-exact-face\face_rank.py

python -B attempts\wave135-z4-exact-face\exact_check.py

python -B -m unittest discover `
  -s attempts\wave135-z4-exact-face `
  -p "test_*.py" -v
```

No rational enumerator is promoted unless the terminal replay succeeds. No
quaternary code, adjacency matrix, graph, Conway-99 resolution, or novelty
claim follows from this checkpoint.
