# Wave 41 all-quotient lift verification

Status: **`VERIFIED_SCOPED_CONDITIONAL`**.

Conditional on

```text
n3=4158,
rank_F3(M)=12,
every graph edge has local type 2+2+2,
```

every base-triangle 39-vertex transported principal block has rank at least
33 over `F_7`.  Consequently `r7>=33`, and the verified modular-rank parity
condition sharpens the branch to even `r7>=34`.

The independent checker reconstructs all 4,050 normalized all-`222`
quotients.  Exactly eight have ternary rank eleven; they are eight distinct
labelled graphs in one strict fibre-coloured isomorphism class.  A complete
18-bit lift census and exact affine transport give, for each:

```text
triangle-free lifts: 37378
rank_F7(K39):         33:264, 34:7348, 35:29766.
```

The package also records a hostile scope guard: a three-dimensional
structural part of the rank-33 block kernel annihilates every legal outside
column, so the result cannot be inflated to rank 45 by a full
six-dimensional border-projection claim.

Reproduce:

```powershell
python -B verification\wave41-allquotient-lifts\independent_check.py `
  --verify verification\wave41-allquotient-lifts\independent-results.json
python -B -m unittest discover `
  -s verification\wave41-allquotient-lifts -p "test_*.py" -v
```

The endpoint, the all-`222` and `r3=12` assumptions, a graph, endpoint
exclusion, a bound below `4158`, and novelty remain unproved or `UNKNOWN`.
