# Wave 121: orbit theta and scalar C4 Jacobi reductions

Status: `DERIVED` discovery. Independent verification is required.

This package tests the `q=14`, `rank_F7(S)=30` row of the level-seven
lattice transfer. It replaces a literal enumeration of either enormous
discriminant group by the smallest orbit aggregates justified without any
graph or lattice automorphism:

```text
zero class
nonzero isotropic classes
one class for each exact nonzero quadratic value in F7
```

The exact-value qualification matters. Projectivizing would merge data that
Wave 80 distinguishes by evaluation symbols, and Wave 97 already showed
that abstract projective orthogonal orbits erase useful short-vector
information.

## Outcome

The vector-valued shift gives two new families of exact nonnegative
coefficients:

```text
x_(7m) - y_m >= 0
y_(7n) - x_n >= 0
```

They count nonzero isotropic classes in the two natural level-seven
quotients. The package checks them together with `y1,...,y77>=0`.

They do **not** raise the verified Wave 101 optima:

```text
x7+...+x10 >= 389888/57, hence at least 6842 lattice vectors;
x7+...+x11 >= 4675706896/9307, hence at least 502388.
```

Both old exact rational optimizers satisfy every new constraint.

A useful conditional sharpening does appear. If

```text
x7=x8=x9=0
```

so the norm-14, norm-16, and norm-18 shells are empty, exact identities give

```text
x10 >= 2,729,216
x10+x11 >= 4,144,144.
```

The first bound has an exact even-integral formal control satisfying all
tested orbit inequalities through `y77`. The second rational optimum has
fractional `y` coefficients and is deliberately not parity-rounded.

The quotient-code upper bound for either exact anisotropic value is

```text
7^30 (7^13 + 7^6),
```

which is vastly larger than the lower bounds. There is no contradiction.

## Scalar C4 Jacobi sharpening

A second exact reduction improves the verified Wave 116 C4 route. For an
alternating C4 sign vector `epsilon`, the vector

```text
d_C=sum epsilon_i u_i
```

already lies primitively in `L` and has norm 20. Therefore
`b_C=sqrt(7)d_C in K` gives an ordinary one-variable Jacobi marking of
index 70, with Fricke partner index 10. Wave 116's index-630 marking was
`3b_C`.

The divisibility of `b_C` in `K` is seven, so the ordinary 140 theta
residues reduce to 20, or 11 after evenness. At norms 14, 16, and 18,

```text
sum epsilon_i t_i=4
```

is equivalent to the exact alternating unit pattern. The target coefficient
is therefore `zeta^28`, not `zeta^84`.

An exact truncated coefficient control satisfies support, positivity,
symmetry, row sums, and all 52,812 required incidences. Hence those
elementary constraints do not prove the desired upper bound. The next
proof-producing target is the weight-`43/2`, 20-component K/L Fricke
module. No spanning basis or upper dual is claimed here.

## Exact boundary

- No graph or lattice is constructed.
- The formal even-integral prefix is not asserted to be a theta series.
- Norm-20 and norm-22 coordinate compositions are not determined by the
  frozen inputs and are retained as `UNKNOWN`, not merged.
- The `q^10 zeta^28` Jacobi coefficient has no frozen exact alternating
  incidence interpretation.
- The rank-30 row survives.
- The rank-28 row survives the scalar Jacobi reduction.
- Conway-99 and literature novelty remain `UNKNOWN`.

## Replay

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave121-vector-theta-orbits\exact_check.py --verify

.\.venv\Scripts\python.exe -B `
  attempts\wave121-vector-theta-orbits\scalar_jacobi_check.py --verify

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave121-vector-theta-orbits -p "test_*.py" -v
```
