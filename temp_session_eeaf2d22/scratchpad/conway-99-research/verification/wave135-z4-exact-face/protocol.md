# Wave135 verification protocol

## Clean-room boundary

The rank derivation uses the frozen Wave134 mathematical statement and pinned
`exact-results.json` only. It does not import or inspect a Wave135 discovery
implementation. Discovery artifacts may be compared only after an explicit
seal supplies their manifest, schema, and hashes.

## Exact matrix convention

Columns are the 1,119 primal zero/two-swap orbit representatives
`(n0,nodd,n2)` with `n0>n2`. Rows are the 161 forbidden dual orbit
representatives.

For source `(a,b,c)` and target `(*,r,s)`, the full coefficient contributed by
the source and its swap is

```text
2^(r+1) K_r(a+c,c) K_s(99-r,b).
```

The verifier removes the nonzero row factor `2^(r+1)`. This preserves rank,
zero equations, and rational feasibility when dual lower bounds are scaled
consistently.

## Exact rank certificate

For fixed target odd count `r`, entries factor through the active source odd
counts `b`. This bounds the eight row-block ranks by

```text
r:      0   2   4   6  92  94  96  98
rank:   7  44  44  44   1   1   1   1
```

Their sum is 143. A deterministically selected square minor is reduced modulo
the prime `1,000,000,007`; a nonzero determinant proves the same integer
minor is nonzero over the rationals. Appending the identity, total-size, and
torsion-size rows is certified the same way.

## Rational primal contract

Schema `wave135-z4-rational-primal-v1` requires all 1,119 source coordinates
exactly once. Accepted values are integers, exact rational strings, or
`[numerator, denominator]` with positive denominator. Floats are rejected.

The checker verifies:

- every primal lower bound;
- all 161 exact zero rows;
- identity and total size;
- primal and dual torsion-shell sizes for the torsion-tightened model; and
- every one of the 1,114 allowed dual coefficients and forced lower bounds.

A passing rational witness remains only a formal rational enumerator.

## Farkas contract

Schema `wave135-z4-farkas-v1` uses the convention

```text
E x = h,  G x >= l,
z >= 0,  y E + z G = 0,  y h + z l > 0.
```

Multipliers are sparse exact objects; omitted entries are zero. Every key,
sign, stationarity coordinate, and the strict contradiction margin is checked
exactly. The declared model distinguishes the two-row affine face from the
torsion-tightened face.

## Logical wall

No solver status, floating-point vector, partial support, or timeout is a
certificate. Integer shell divisibility is recorded separately from rational
feasibility. Without an exact accepted primal or Farkas artifact, rational
feasibility, integral feasibility, code/graph realizability, novelty, and
Conway-99 all remain `UNKNOWN`.
