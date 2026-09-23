# Wave 82 independent verification

Status: `VERIFIED`, conditional on a hypothetical
`srg(99,14,1,2)` and the previously verified 7-primary Smith form of its
Seidel matrix.

The clean-room check confirms both directions of

```text
T = 9S+7J = 18A-2J+9I,
A = (T+2J-9I)/18.
```

It also confirms, for every surviving
`r in {28,30,32,34,36,38,40,42}`,

```text
SNF(T) =
diag(1, 9^(r-1), 63^(99-2r), 441^(r-1), 3969).
```

No rank row is excluded. No matrix or graph is constructed. Conway-99 and
literature novelty remain `UNKNOWN`.

## Reproduce

From the repository root:

```powershell
python -B verification/wave82-seidel-orthogonal/independent_verify.py `
  --verify verification/wave82-seidel-orthogonal/independent-results.json

python -B -m unittest -v `
  verification/wave82-seidel-orthogonal/test_independent_verify.py
```

The verifier uses only the Python standard library. Its 99-by-99 hostile
controls are bounded and leave well over the required 15 percent host memory
free.
