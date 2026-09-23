# Wave 131: binary symplectic/LCD enumerator shift

Claim labels: `DERIVED`, `CANDIDATE`, and `UNKNOWN`.  Independent
verification is required.

Modulo two, a hypothetical target adjacency matrix is a symmetric
idempotent.  Its image is an even LCD `[99,54]` code and therefore a
54-dimensional binary symplectic space; its kernel is the dual LCD
`[99,45]` code and contains the all-one word.

The two maps

```text
S -> A 1_S,           S -> (I+A) 1_S
```

are injective on all vertex subsets of size at most three.  This follows
from the independently verified minimum-weight-eight bounds: equality of
two images would place their symmetric difference, of weight at most six,
in the opposite code.

An independent three-set census reproduces every requested forced
coefficient:

```text
im(A):
A14>=99, A24>=4158, A26>=693, A30>=70686,
A32>=41580, A34>=36036, A36>=8547.

ker(A):
B15>=99, B24>=693, B26>=4158, B31>=41580,
B33>=79002, B35>=8316, B37>=27720, B39>=231,
```

together with `B_w=B_(99-w)`.

The ordinary MacWilliams system does not contradict these data.  The
stored witness has exact nonnegative rational coefficients, image minimum
weight 14, dual minimum weight 15, the correct code sizes, complement
symmetry, and all 200 forward/inverse MacWilliams rows.  It is not an
integral enumerator or a realized code.

A hard-bounded integral formal-enumerator scout ended
`UNKNOWN_HARD_TIMEOUT` after 15 seconds.  This is telemetry only and is not
evidence of infeasibility.

The next boundary is a distinguished-row or joint enumerator.  The 99
weight-14 neighborhood rows do more than inhabit `im(A)`:

```text
<row_u(A),row_v(A)> = A_uv  over F2.
```

Thus their symplectic Gram matrix is the unknown graph itself.  Similarly,
the 99 weight-15 rows of `I+A` have Gram `I+A`, and the two row systems are
orthogonal.  Ordinary weight enumerators discard exactly these labelled
intersection data.

No binary code, adjacency matrix, graph, rank exclusion, or Conway-99
resolution is obtained.  Novelty remains `UNKNOWN`.

## Reproduce

```powershell
python -B attempts\wave131-binary-lcd-enumerator\exact_check.py `
  --verify attempts\wave131-binary-lcd-enumerator\exact-results.json

python -B -m unittest discover `
  -s attempts\wave131-binary-lcd-enumerator -p "test_*.py" -v
```

The rational discovery script and bounded integral scout use the repository
virtual environment's Z3 package.  The exact replay uses only Python's
standard library.
