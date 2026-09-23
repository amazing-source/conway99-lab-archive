# Wave 148: marked order-eight consistency rows

Status: **DERIVED exact rows; independent verification required**.

Wave 147 constructed the two-root order-eight flag basis and ordinary
seven-to-eight deletion equations.  This package supplies the missing linear
rows that use the exact target parameters

```text
k=14, lambda=1, mu=2.
```

No graph automorphism or endpoint value is assumed.

## Result

For each rooted isomorphism type of an order-seven class, the package counts
an eighth vertex in two ways.

Marked vertex:

```text
m_tau*(14-d_tau)*x_H
  = sum_K e_vertex(tau,K)*x_K.
```

Pointwise ordered pair:

```text
m_tau*(lambda_or_mu-c_tau)*x_H
  = sum_K e_pair(tau,K)*x_K.
```

Here `m_tau` is the number of marks of the rooted type inside `H`, `d_tau`
is the marked vertex's internal degree, and `c_tau` is the marked pair's
internal common-neighbor count.

The exact artifact contains:

```text
marked-vertex rows:                944
vertex row nonzero terms:       10,872
pointwise ordered-pair rows:      4,440
pair row nonzero terms:          17,782
zero-capacity pair rows:            893
order-eight columns:                916
```

All 893 zero-capacity pair rows have empty right sides, as required by local
`lambda/mu` admissibility.  Pair types split into 1,670 edge-root types and
2,770 nonedge-root types.

## Controls

The checker independently aggregates the right sides for every order-eight
class `K`:

```text
sum of marked-vertex coefficients
  = sum_w degree_K(w)
  = 2|E(K)|,

sum of marked-pair coefficients
  = sum_w degree_K(w)*(degree_K(w)-1).
```

It also checks the corresponding left aggregates for all 208 order-seven
classes.  Five focused tests include an independent reconstruction of those
column totals and a hostile coefficient mutation.

## Boundary

No numerical solver was run.  These rows are necessary conditions to append
to the Wave 147 PSD model; they are not a graph and are not a bound by
themselves.  A future upper bound still requires assembling the combined
linear/PSD system and extracting an independently replayable rational dual
certificate.

```text
strict n3 upper bound:     UNKNOWN
rational dual certificate: NOT OBTAINED
Conway-99:                  UNKNOWN
```

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave148-marked-order8\exact_check.py `
  --verify attempts\wave148-marked-order8\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest `
  attempts.wave148-marked-order8.test_exact_check -v
```

The checker enforces the inherited 15% free-physical-memory floor.

