# Wave 34 rooted-structural candidate release

Released: 2026-07-24T20:16:57Z

Discovery base:
`0fa5b8161baf8b2a5404a67051b7d61cbc906da3`

Orchestrator checkpoint before release:
`0d27dc5169b58e8b9296b079b73eaff39a1a4022`

## Quarantined claim

```text
label: DERIVED
scope: strict unrestricted reparameterization of the verified Wave 33
       rooted six-block graph criterion
binary solution:  UNKNOWN
complete exclusion: UNKNOWN
rooted endpoint: UNKNOWN
n3=708: UNKNOWN
Conway-99: UNKNOWN
novelty: UNKNOWN
```

The discovery candidate claims an exact cycle-space and integral rank-16
projector reduction. It does not claim a graph or an infeasibility
certificate. The independent verifier must reconstruct the mathematics
before comparing bytes and may downgrade or reject every claim.

## Frozen candidate bytes

| path | SHA-256 |
|---|---|
| `agents/2026-07-24-wave34-rooted-structural.md` | `535d237abcb841609835b1b8da11f2193cf17314c3dfe1dc427a3eec0a710246` |
| `attempts/wave34-rooted-structural/check_results.py` | `9a4912cb4875d0ec7e54366491484fdf21c218ba2361858ea5d28a0e9af9ad1c` |
| `attempts/wave34-rooted-structural/reduction.py` | `c3ad0a5b764e6e5045082ba28fc7c5ddfb2727859eac990f2845a8e5dd4c60e1` |
| `attempts/wave34-rooted-structural/results.json` | `bd68070b172329e161f46d85e634aecf2348da16de785331e60e4b93a1f4dfc5` |
| `attempts/wave34-rooted-structural/test_reduction.py` | `3e9f2f95d44fda18c0733267a58fd101fa904bc94e283baa75b7b1616dcede4f` |
| `attempts/wave34-rooted-structural/artifact-manifest.sha256` | self-hash intentionally omitted |

The outer manifest lists the five discovery bytesets and omits its own
impossible self-hash.

## Orchestrator replay before release

Environment:

```text
Python 3.13.14
standard library only
seed: none
```

Commands:

```powershell
python -I -B attempts/wave34-rooted-structural/check_results.py --full-census

$env:WAVE34_FULL_CENSUS='1'
python -B -m unittest discover `
  -s attempts/wave34-rooted-structural `
  -p 'test_*.py' -v
```

Observed:

```text
deterministic result regeneration: PASS
tests: 7/7 PASS
full-census checker plus tests wall time: 87.2 seconds
```

This replay checks candidate-owned code and therefore does not confer
`VERIFIED`.

## Comparison wall

The verifier's Stage-1 precomparison package must be byte-frozen before the
candidate paths above are inspected. Stage 2 must:

1. validate this release and every input hash;
2. bind the candidate's canonical signed-Fano arrays to the exact Wave 33
   label order;
3. independently check the SNF witness and full two-factor census;
4. audit both directions of every projector and integral-numerator
   equivalence;
5. distinguish a single-column count from compatible 15-column tuples;
6. preserve every modular non-exclusion and failed route; and
7. leave all global statuses `UNKNOWN`.
