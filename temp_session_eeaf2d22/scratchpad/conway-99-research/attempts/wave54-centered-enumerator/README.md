# Wave 54 centered ternary formal enumerator

Status: `CANDIDATE`, pending independent reconstruction.

The conditional prism-free endpoint would supply the centered projective
self-orthogonal ternary code described in Wave 39.  This package asks a
strictly smaller question: do its currently recorded *ordinary* weight
enumerator constraints already contradict one another?

They do not.  An exact integral formal distribution is

```text
A_0   =      1
A_18  =      2
A_144 = 53,316
A_153 = 19,798
A_159 = 98,496
A_162 =  5,072
A_198 =    462
```

and every other `A_i` is zero.  Exact integer arithmetic gives:

```text
sum A_i:                          3^11 = 177,147
all nonzero multiplicities even: yes
all occupied weights divisible 3: yes
all 232 MacWilliams coefficients: nonnegative integers
B_1, B_2:                         0, 0
B_i >= A_i for every i:           yes
recorded dual lower bounds:       passed
```

This is a hostile control, not a construction.  A formal ordinary enumerator
need not be the weight enumerator of any linear code.  It forgets the separate
counts of symbols `1` and `2`, the configuration of the 99 distinguished
weight-seven dual words, triple intersections, and the centered polar Gram
relations.  Those are the places where a code-theoretic continuation must
become genuinely stronger.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave54-centered-enumerator\exact_check.py `
  --verify attempts\wave54-centered-enumerator\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave54-centered-enumerator -p "test_*.py" -v
```

No actual code, endpoint graph, strict `n3` upper bound, Conway-99 resolution,
or novelty claim follows.
