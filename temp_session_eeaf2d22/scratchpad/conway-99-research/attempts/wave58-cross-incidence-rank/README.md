# Wave 58: cross-incidence rank synthesis

Status: `DERIVED_INCONCLUSIVE`.

This package combines prior verified Wave 36 cross-incidence rank identities
with the sealed Wave 57 star-complement ledger. It does not claim the rank
identity as new.

## Result

With `kappa=components(A_X)`, `a=mult_Y(3)`,
`b=mult_Y(-4)`, and `q=C4(X)`, prior Wave 36 gives

```text
rank(B)=35-kappa,
a=18,
b=7+kappa,
kappa in {1,2,3}.
```

Wave 57's 18 multiplicity rows therefore collapse to

```text
(a,b,kappa) = (18,8,1), (18,9,2), (18,10,3).
```

The cubic-wedge argument improves `q<=89` to `q<=27`. Exact component
censuses sharpen this to:

```text
kappa=1: 0<=q<=27
kappa=2: 0<=q<=24
kappa=3: q in {6,8,10,12,14,16,18}.
```

All three lanes retain exact local A_X and scalar residual-spectrum controls.
These controls are separate; no simultaneous `B`, compatible `A_Y`, endpoint
graph, or contradiction is constructed.

The restricted replay of one canonical Wave 40 rank-11 all-`222` quotient
checks all 262,144 endpoint masks. Its 37,378 triangle-free lifts all have
components `[12,24]` and `4<=q<=14`, positively preserving `kappa=2` in that
restricted lane.

## Reproduce

```powershell
python -B attempts\wave58-cross-incidence-rank\exact_check.py `
  --verify attempts\wave58-cross-incidence-rank\exact-results.json

python -B -m unittest discover `
  -s attempts\wave58-cross-incidence-rank -p "test_*.py" -v
```

The checker uses exact integer arithmetic, validates frozen upstream hashes,
and enforces at least 15 percent free physical memory.

## Boundary

- rank/multiplicity identities: prior `VERIFIED` Wave 36 input
- Wave 57 row collapse and component-cycle synthesis: `DERIVED`
- excluded surviving rows: none
- endpoint: `UNKNOWN`
- Conway-99: `UNKNOWN`
