# Failed and incomplete routes

## Direct PSD or rank contradiction

**Result:** refuted as a strategy at this level.

The exact prism-free witness has an entrywise nonnegative forced Gram matrix
of rank 32, while a 36-by-60 incidence factor may have rank as large as 36.
The exact character certificate proves PSD. Thus neither a negative
eigenvalue nor excessive rank can exclude the endpoint.

## First binary-factor stage

Within each 12-row group, the 60 columns of a binary factor must correspond
exactly to the 60 nonmatching pairs of `K_12`. After fixing group zero, the
first inter-group factor is a permutation between two sets of 60 pairs.

This was encoded with 3,600 binary variables:

- 60 row and 60 column permutation equations;
- 144 vertex-pair intersection equations prescribed by `G_01`.

Two discovery attempts were made on 2026-07-28:

- SciPy/HiGHS MILP, 60-second limit: time limit, no incumbent.
- Z3 pseudo-Boolean equalities, 120-second limit: `unknown`.

These statuses are **not evidence of infeasibility**. No exact candidate and
no exact negative certificate were produced. The route remains `UNKNOWN`.

## Simultaneous three-group factor

If the first pair permutation is found, the second can be searched with a
linear exact model imposing both `G_02` and `G_12`. This stage was not reached
because the first mapping had no incumbent within the bounded scouts.

## Residual B block

No search for the 60-by-60 matrix `D` was run. It should begin only after an
exact binary `C` factor is available. Solver statuses before exact replay
must remain exploratory.
