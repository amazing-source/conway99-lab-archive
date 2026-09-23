# Wave 82: Seidel integral-orthogonal reduction

Status: `DERIVED_DISCOVERY_ONLY`.

This package gives a new exact reformulation of a hypothetical
`srg(99,14,1,2)`.  It does not construct or exclude the graph.

For the Seidel matrix

```text
S = 2A - J + I,
```

define

```text
T = 9S + 7J = 18A - 2J + 9I.
```

Then `T` is a symmetric integer matrix of order 99 with

```text
diagonal entries:  7
edge entries:     16
nonedge entries:  -2
T 1 = 63 1
T^2 = 63^2 I.
```

Conversely, every symmetric matrix with these entry conditions, row sum, and
square identity recovers a Conway graph by

```text
A = (T + 2J - 9I)/18.
```

Thus Conway-99 is exactly an integral orthogonal-matrix existence problem with
a three-valued coordinate alphabet.

If `r=rank_F7(S)`, the complete conditional Smith form is

```text
SNF(T) =
diag(1, 9^(r-1), 63^(99-2r), 441^(r-1), 3969).
```

The verified Wave 66 restriction leaves
`r in {28,30,32,34,36,38,40,42}`.  Every one of those eight abstract Smith
profiles is arithmetically consistent, so this is a reduction rather than an
obstruction.

## Reproduce

From the repository root:

```powershell
python -B attempts/wave82-seidel-orthogonal/exact_check.py `
  --verify attempts/wave82-seidel-orthogonal/exact-results.json

python -B -m unittest discover `
  -s attempts/wave82-seidel-orthogonal -p "test_*.py" -v
```

The checker uses only the Python standard library and refuses to run below
20 percent available physical memory on Windows.

## Boundary

- Discovery cannot certify itself; independent verification is required.
- The matrix `T` has not been constructed.
- A valid Smith form is necessary, not sufficient.
- No rank row is removed.
- Conway-99 and literature novelty remain `UNKNOWN`.

