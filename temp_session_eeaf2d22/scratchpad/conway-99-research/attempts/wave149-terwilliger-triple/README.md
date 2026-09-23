# Wave 149: triangle-root Terwilliger projection

Status: **verified null projection; Conway-99 unknown**.

This lane reformulates the `n3=4158` endpoint around a triangle rather than
around six-set weight distributions. At the endpoint, the order-six prism
count is zero because

```text
N1 = 1386 - n3/3.
```

For a root triangle, the remaining vertices split as `12+12+12+60`. The
strongly regular identity

```text
A^2 = 12 I - A + 2 J
```

forces all three 12-by-12 cross-blocks to be permutation matrices and
determines the Gram matrix of the three 12-by-60 incidence blocks.

## Exact result

The package contains an explicit prism-free system of six permutations. Its
forced 36-by-36 Gram matrix:

- has only nonnegative integer entries;
- has diagonal 10 and every row sum 60;
- is positive semidefinite by an exact character calculation;
- has rank 32, below the available factor dimension 60.

Therefore first-level triangle-root triple-intersection nonnegativity, PSD,
and rank cannot force a prism and cannot improve `n3<=4158`.

The exact Gram certificate has SHA-256
`1cfd0442e69b621c4a82fbeddeec9e7afbfcd04cd8eb458e29170cfd345c7ffc`.

## Next obstruction

The displayed Gram matrix is not yet a binary incidence factor. The next
sharp question is whether it admits `G=C C^T` with `C` binary 36-by-60, each
row of weight 10, and every column having two ones in each 12-row group. If
so, the residual 60-vertex adjacency block must then be a symmetric
zero-diagonal 8-regular matrix satisfying both the linear mixed-block
identities and its quadratic block identity.

Solver timeouts in this package are discovery logs only and are not negative
evidence.

## Reproduce

```powershell
python attempts/wave149-terwilliger-triple/exact_check.py `
  --verify attempts/wave149-terwilliger-triple/exact-results.json

python -m unittest discover `
  -s attempts/wave149-terwilliger-triple -p "test_*.py" -v
```
