# Wave137: Arf/Krawtchouk branch checkpoint

Claim label: `CANDIDATE_EXACT` for replayed formal rational witnesses;
`UNKNOWN` for integral feasibility, code/graph realization, and Conway-99.

This package is deliberately split into two lanes.

## Binary Wave132 lane

The exact 41-variable Wave132 ordinary/split projection was branched by the
Arf sign

```text
G_R = sum_(w even) (-1)^(w/2) A_w = epsilon*2^27,
epsilon in {+1,-1}.
```

The redundant dual check is

```text
G_E = -G_R/32 = -epsilon*2^22.
```

Confirmed signed Krawtchouk identities were then added cumulatively through
degree five. Both signs remain exactly rationally feasible at every stage:

| stage | plus | minus |
|---|---|---|
| global Arf | feasible | feasible |
| + K1 | feasible | feasible |
| + K2 | feasible | feasible |
| + K3 | feasible | feasible |
| + K4 | feasible | feasible |
| + K5 | feasible | feasible |

Every witness passes exact replay of all 200 forward/inverse ordinary
MacWilliams rows, forced bounds, nonnegativity, the high-weight cut, and all
four Wave132 distinguished split systems.

The two K5 points initially violate only the lower shadow bounds at degrees
6 and 93. Adding exactly those two inequalities and resolving produces
`binary-shadow1-plus.json` and `binary-shadow1-minus.json`. Both pass every
approved bound

```text
|M_t| <= 2^27 * binom(99,t),  t=6,...,99.
```

They land on

```text
M_6 = M_93 = -2^27 * binom(99,6)
              = -150394890897850368.
```

This is a sharp rational boundary, not a code construction. Divisibility and
parity of `M_t/2^27` are intentionally reserved for a later integral layer.

## Z4 lane

`float_scout.py` tested both 1,119-variable Arf slices of the Wave135
torsion-tightened `Z4` relaxation. HiGHS returned only numerical failure or
unknown statuses under two solver configurations. These outputs are
non-evidentiary.

`row_generate_arf.py` stages exact GMP-rational reconstruction with terminal
replay, but was not run after the strategy moved first to the smaller binary
system. There is no exact Z4 branch result in this package.

## Reproduction

```powershell
python -B attempts\wave137-z4-arf-branches\exact_check.py `
  attempts\wave137-z4-arf-branches\binary-shadow1-plus.json `
  attempts\wave137-z4-arf-branches\binary-shadow1-minus.json

python -B attempts\wave137-z4-arf-branches\shadow_bounds.py `
  attempts\wave137-z4-arf-branches\binary-shadow1-plus.json `
  attempts\wave137-z4-arf-branches\binary-shadow1-minus.json `
  --output attempts\wave137-z4-arf-branches\shadow-bound-audit-round1.json

python -B -m unittest discover `
  -s attempts\wave137-z4-arf-branches -p "test_*.py" -v
```

No binary code, quaternary code, adjacency matrix, or graph is constructed.
Novelty remains `UNKNOWN`.
