# Wave 108 independent verification of Wave 107

Verdict: `VERIFIED_SCOPED`.

The sealed Wave 107 claim is correct in its stated conditional scope. If a
hypothetical `srg(99,14,1,2)` contains the induced
`H=C4 Cartesian K3` motif, then the characteristic polynomial and every
listed graph invariant of the 87-vertex principal complement `D` are forced
exactly as Wave 107 states.

This verification does **not** find a spectral obstruction. It does not prove
or disprove a full motif extension, does not resolve Conway-99, and does not
establish literature novelty.

## Input and independence

Before any discovery code was run, the verifier checked that
`attempts/wave107-c4boxk3-spectrum/package-manifest.sha256` had SHA-256

```text
7e899602825d3cdf989affade8a1e5a6256f17ba911f6351ea8bfe4a3b05d2b0
```

and that all nine listed files matched their hashes.

The verifier did not import discovery code. It rebuilt the motif in a
different vertex order, computed its characteristic polynomial from exact
adjacency traces using Newton identities, checked each eigenspace dimension
by rational row reduction, and then performed its own resolvent/Jacobi
calculation. The discovery checker was replayed only after these independent
checks passed.

## Independent characteristic-polynomial derivation

For an adjacency matrix `A` of the hypothetical strongly regular graph,

```text
A^2 = 12I-A+2J
```

and its spectrum is `14^1, 3^54, (-4)^44`. Put
`q=(x-3)(x+4)`. Multiplying in the adjacency algebra gives

```text
(xI-A)^(-1) = ((x+1)I+A+2J/(x-14))/q.
```

The verifier checks the three coefficients directly:

```text
I: x(x+1)-12 = q
A: x-(x+1)+1 = 0
J: 2x/(x-14)-28/(x-14)-2 = 0.
```

The independently reconstructed motif has

```text
spec(H) = {4^1, 2^2, 1^2, 0^1, (-1)^4, (-3)^2}.
```

Jacobi's complementary-minor identity says

```text
chi_D(x) = chi_A(x) det(((xI-A)^(-1))_H).
```

Because `H` is 4-regular, `J` acts only on its all-ones eigenspace.
The all-ones determinant factor is

```text
(x-14)(x+5+24/(x-14)) = x^2-9x-46.
```

The other motif eigenspaces contribute `x+1+theta`. Cancelling the
12 powers of `q` and the single factor `x-14` gives

```text
chi_D(x)
 = (x-3)^42 (x+4)^32 (x^2-9x-46)
   (x+3)^2 (x+2)^2 (x+1) x^4 (x-2)^2.
```

The degree is 87, as required.

## Explicit refutation of the `-38` variant

The verifier independently enumerated all `2^12` possible motif
neighborhoods of one outside vertex against the SRG pair-codegree caps. The
maximum possible motif degree is 2. There are 120 motif-to-outside
incidences and 36 required outside incidences over motif pairs, forcing

```text
X0=3, X1=48, X2=36.
```

Thus the outside degrees are respectively 14, 13, and 12, and

```text
trace(D^2) = 3*14 + 48*13 + 36*12 = 1098.
```

For roots of `x^2-9x-c`, the second power sum is `81+2c`. With the other
spectral factors fixed, `c=38` gives `trace(D^2)=1082`, short by 16.
Therefore `x^2-9x-38` is `REFUTED`. With `c=46`, the trace is exactly
1098.

## Reproduced consequences

The first four spectral moments are

```text
trace(D)   = 0
trace(D^2) = 1098
trace(D^3) = 1002
trace(D^4) = 37518.
```

They force 549 edges and `1002/6=167` triangles. The degree census gives

```text
sum_v binom(deg(v),2) = 6393.
```

Using

```text
trace(D^4)
 = 2|E| + 4 sum_v binom(deg(v),2) + 8*C4(D)
```

gives `C4(D)=1356`.

Since a real symmetric adjacency matrix is diagonalizable, the factor
multiplicities also force

```text
nullity_Q(D) = 4
rank_Q(D-3I) = 45
rank_Q(D+4I) = 55.
```

## Perron vector, connectedness, and interlacing

Let `s` record each outside vertex's number of motif neighbors. The degree
equation and the off-diagonal block of the SRG matrix equation force

```text
D*one = 14*one-s
D*s   = 24*one-5s.
```

Thus `span{one,s}` has characteristic polynomial `x^2-9x-46`. For

```text
rho = (9+sqrt(265))/2,
```

the vector `(rho+5)one-s` is a `rho`-eigenvector. Because
`16^2<265<17^2` and every entry of `s` is at most 2, every coordinate is
strictly greater than `31/2`. The corrected characteristic polynomial makes
`rho` simple. A positive eigenvector restricts positively to every connected
component; simplicity therefore forces the outside graph to be connected.

An exact rational interval check places the other quadratic root in
`(-4,-7/2)` and `rho` in `(25/2,13)`. Every eigenvalue satisfies Cauchy
interlacing against `14^1,3^54,(-4)^44`. Hence the spectrum is consistent
and yields no exclusion.

## Status wall

- Spectral obstruction: none found.
- Motif excluded: no.
- Full motif extension: `UNKNOWN`.
- Conway-99: `UNKNOWN`.
- Literature novelty: `UNKNOWN`.

## Reproduction

```powershell
python -B verification\wave107-c4boxk3-spectrum\independent_check.py --verify
python -B -m unittest discover `
  -s verification\wave107-c4boxk3-spectrum -p "test_*.py" -v
python -B attempts\wave107-c4boxk3-spectrum\exact_check.py --verify
python -B -m unittest discover `
  -s attempts\wave107-c4boxk3-spectrum -p "test_*.py" -v
```

Verifier result: 10 tests passed. Discovery replay: 7 tests passed.
