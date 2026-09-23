# Wave143: binary S6 projection

Claim label: `DERIVED` for the rational projection interval and integral
equality-lattice residue; `UNKNOWN` for nonnegative integral feasibility,
code/graph realization, Conway-99, and novelty.

Wave141 supplied the exact signed sixth input shell

```text
S6 = 2024484 + (512/3)n3.
```

On a Wave137 Arf branch with sign `epsilon`, the ordinary image enumerator
therefore obeys

```text
M6 = sum_(w even) (-1)^(w/2) K6(w) A_w
   = epsilon*2^27*(2024484 + (512/3)n3).
```

This package adds that equation to the Wave137 rational ordinary and
distinguished-split projection, together with signed identities `M0` through
`M5` and all approved shadow inequalities

```text
|M_t| <= 2^27 binom(99,t),  t=6,...,99.
```

## Exact rational projection and target witnesses

Both Arf signs have exactly the same projected interval:

```text
0 <= n3 <= 838878579/128
             = 6,553,738.8984375.
```

The value near 6.55 million is the optimum of this weak projection, not a
known graph boundary.  It is retained in files named
`projection-optimum-*.json`.

Separate full rational witnesses at the graph-relevant values

```text
n3=708 and n3=4158
```

exist for both Arf signs.  All eight stored witnesses replay all 200 ordinary
MacWilliams rows, every forced lower/zero condition, all four Wave132 split
systems, the Arf/Krawtchouk identities, the S6 equation, and all 94 shadow
bounds.

Optimality of the weak projection is elementary once its witnesses are
known.  The minimum uses the explicit constraint `n3>=0`.  At the maximum
the sign-appropriate sixth shadow side gives

```text
2024484 + (512/3)n3 <= binom(99,6).
```

Thus this projection reproduces only the trivial signed-row ceiling.  It
does not improve the independent upper bound `n3<=4158`.

## Integral equality lattice

For an integral formal ordinary enumerator, introduce integral dual
coefficients `D_t` and write `n3=3k`.  An exact FLINT HNF computation on the
109-by-142 equality matrix gives rank 109, nullity 33, and projected kernel
step

```text
gcd(delta k) = 1.
```

The target equation itself proves necessity:

```text
3 M6 = epsilon*2^27*(3*2024484 + 512*n3).
```

Modulo three, the coefficient `2^27*512` is one, hence `n3=0 mod 3`.
Exact integral particular solutions at `k=0` and homogeneous steps
`delta k=1` for both signs show that no stronger residue restriction exists
at the equality-lattice level.  Those HNF solutions may have negative
coefficients; nonnegativity can still be much stronger.

The rational shadow ceiling and this residue give only
`n3<=6,553,737` for integral graph-count candidates.

## Integral scout

Hard-bounded searches imposed integral `A_w,D_t`, full MacWilliams
divisibility, nonnegativity/lower bounds, complement symmetry, all signed
moments and shadows, and the S6 equation.  Both a fixed `n3=4158` query and
an optimization query timed out for each Arf sign.  This is
`UNKNOWN_HARD_TIMEOUT`, not evidence of infeasibility.

## Reproduce

```powershell
.venv\Scripts\python.exe -B `
  attempts\wave143-binary-s6-projection\optimize_rational.py `
  --sign 1 --sense max `
  --output attempts\wave143-binary-s6-projection\projection-optimum-plus-max.json

.venv\Scripts\python.exe -B `
  attempts\wave143-binary-s6-projection\optimize_rational.py `
  --sign 1 --fixed-n3 4158 `
  --output attempts\wave143-binary-s6-projection\witness-plus-n3-4158.json

python -B attempts\wave143-binary-s6-projection\exact_check.py `
  attempts\wave143-binary-s6-projection\projection-optimum-plus-min.json `
  attempts\wave143-binary-s6-projection\projection-optimum-plus-max.json `
  attempts\wave143-binary-s6-projection\projection-optimum-minus-min.json `
  attempts\wave143-binary-s6-projection\projection-optimum-minus-max.json `
  attempts\wave143-binary-s6-projection\witness-plus-n3-708.json `
  attempts\wave143-binary-s6-projection\witness-plus-n3-4158.json `
  attempts\wave143-binary-s6-projection\witness-minus-n3-708.json `
  attempts\wave143-binary-s6-projection\witness-minus-n3-4158.json

.venv\Scripts\python.exe -B `
  attempts\wave143-binary-s6-projection\lattice_certificate.py --verify

python -B -m unittest discover `
  -s attempts\wave143-binary-s6-projection -p "test_*.py" -v
```

No binary code, graph, or adjacency matrix is constructed.
