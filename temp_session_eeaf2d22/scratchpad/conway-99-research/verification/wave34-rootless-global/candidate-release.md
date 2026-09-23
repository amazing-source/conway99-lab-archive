# Wave 34 rootless actual-incidence candidate release

Released: 2026-07-24T20:25:22Z

Discovery base:
`0fa5b8161baf8b2a5404a67051b7d61cbc906da3`

Orchestrator checkpoint before release:
`52c94e915927f791d30f680d12181a08567248fb`

## Quarantined claim

```text
overall label: UNKNOWN
scoped fixed-point/matching reformulation: DERIVED, verification pending
global R3 edge/triangle cap: DERIVED, verification pending
45-vertex local control: CANDIDATE
motif positivity: UNKNOWN
rootless endpoint: UNKNOWN
n3=708: UNKNOWN
Conway-99: UNKNOWN
novelty: UNKNOWN
```

The discovery package does not construct a graph or endpoint and does not
exclude the rootless branch. Its local control is deliberately partial.

## Frozen candidate bytes

| path | SHA-256 |
|---|---|
| `agents/2026-07-24-wave34-rootless-global.md` | `71f5b49622629a65ffafea2636c552bccaecaadc7584326c70d8819f54e997ed` |
| `attempts/wave34-rootless-global/check_local_model.py` | `33577962a44241cf3fd9d5a6b5948c35ddd757aed5975bd755c384ded00deed6` |
| `attempts/wave34-rootless-global/exact-results.json` | `fd4ff04bd13128a26d9a5ecb4bd1c2a8832d29d0056a592d4d90074747a0c331` |
| `attempts/wave34-rootless-global/local-control.json` | `a25d19e3eda3ec77b55065b7f39a68345fa911b80eafbff0e4c37b1857e10301` |
| `attempts/wave34-rootless-global/test_local_model.py` | `21d4dc17c19098ee826202af4688611dbbf5982d0ab9216bb87da6839452a378` |
| `attempts/wave34-rootless-global/artifact-manifest.sha256` | self-hash intentionally omitted |

The manifest lists the five discovery bytesets and omits its own impossible
self-hash.

## Orchestrator replay before release

Environment:

```text
Python 3.13.14
standard library only
seed: none
```

Commands:

```powershell
python -B attempts/wave34-rootless-global/check_local_model.py `
  --max-witnesses 1

python -B -m unittest discover `
  -s attempts/wave34-rootless-global `
  -p 'test_*.py' -v
```

Observed:

```text
deterministic local checker: PASS
tests: 12/12 PASS
combined wall time: 3.3 seconds
```

This replay uses candidate-owned code and does not confer `VERIFIED`.

## Comparison wall

The verifier's Stage-1 precomparison reconstruction must be byte-frozen
before candidate inspection. Stage 2 must:

1. validate every frozen input and candidate hash;
2. independently derive the three-fibre permutation model;
3. independently derive all four relation-degree formulas, `sum q=472`,
   and the 1,150 `R3`-edge count;
4. check the factor of two in the mixed-trace overlap formula;
5. verify that the rank-44 projector Gram makes an `R3` edge admit at most
   one `R3`-triangle completion;
6. distinguish the resulting upper cap from any missing positive lower
   bound;
7. independently rebuild and attack the 45-vertex control without treating
   it as extendible; and
8. leave every global status `UNKNOWN`.
