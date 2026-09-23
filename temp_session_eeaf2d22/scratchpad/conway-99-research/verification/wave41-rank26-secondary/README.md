# Wave 41 rank-26 secondary verification

Verdict: **PASS** for the universal theorem

```text
rank_F7(M) >= 26
```

for every hypothetical `srg(99,14,1,2)`.

This is a second skeptical verification, independent of both the discovery
implementation and the primary verifier through the mathematical-result
freeze. It does not construct a graph, exclude `n3=4158`, improve
`n3<=4158`, or establish novelty.

## Independence and freeze

Only verified Wave 39/40 inputs were opened initially. Their hashes are in
`input-freeze.sha256`. Before any Wave 41 artifact was read, the checker,
17-test core suite, and exact result were frozen in
`precomparison-freeze.sha256`; the full replay matched the stored result.

After comparison began, the checker was amended only to expose two
already-computed canonical-set cardinalities mechanically: 52 right kernels
and 164,278 kernel/target pairs. No graph construction, finite-field
reduction, partition or permutation search, matching universe, equality
test, or verdict changed. The final bytes were then replayed again.

No automorphism of a completed graph is assumed. All local matchings and
border permutations remain labelled throughout.

## Independent 39-block reduction

For one edge `xy`, its triangle mate `z`, the two 12-point endpoint fibres,
and `Z=N(z)-{x,y}`, construct

```text
K39 = [ S    U  ],       K=J-I-2A over F7.
      [ U^T W_R]
```

Here `S` is the verified 27-point block, `U` is determined by a permutation
between the endpoint fibres, and `W_R=J-I-2R` for one of the 10,395 perfect
matchings `R` on `Z`.

Let the rows of `H` span `ker(S)`, put `F=H U`, and let the columns of `Z0`
be the canonical right-kernel basis of `F`. Solve `S X=U Z0` and put
`T=Z0^T U^T X`. Exact congruence gives

```text
rank(K39)
  = rank(S) + 2 rank(F) + rank(Z0^T W_R Z0 - T).
```

If the local partition has `e` even parts, then
`rank(S)=25-2e` and Wave 40 gives `rank(F)>=e`. Therefore

```text
rank(K39)=25
iff
rank(F)=e and Z0^T W_R Z0=T.                    (1)
```

The checker verifies this identity against direct dense ranks for all eleven
types. Basis choice and the particular solution `X` do not affect (1).

## Complete eleven-type audit

The checker independently enumerates all `(11)!!=10,395` labelled matchings
against a fixed matching. Their component census is:

```text
6:3840, 5+1:2304, 4+2:1440, 4+1+1:720,
3+3:640, 3+2+1:960, 3+1+1+1:160,
2+2+2:120, 2+2+1+1:180, 2+1+1+1+1:30, 1^6:1.
```

This recovers exactly the eleven positive partitions of six and the local
rank formula `25-2e`.

For the four all-odd types, `F=0`. A rank-25 completion first requires every
selected Schur-target diagonal to vanish:

| type | maximum zero-diagonal matching | candidate permutations | `W_R` hits |
| --- | ---: | ---: | ---: |
| `5+1` | 10 | 0 | 0 |
| `3+3` | 12 | 1 | 0 |
| `3+1+1+1` | 6 | 0 | 0 |
| `1^6` | 0 | 0 | 0 |

The sole `3+3` candidate has 18 off-diagonal entries outside the legal
`W_R` alphabet `{1,6}`, so it is absent from all 10,395 matching blocks.

For the seven types with an even part:

| type | minimum-`F` permutations | canonical kernels | canonical targets | rank-25 hits |
| --- | ---: | ---: | ---: | ---: |
| `2+1+1+1+1` | 80,640 | 2 | 80,038 | 0 |
| `2+2+1+1` | 192 | 8 | 184 | 0 |
| `2+2+2` | 32 | 32 | 32 | 0 |
| `3+2+1` | 80,640 | 2 | 80,632 | 0 |
| `4+1+1` | 768 | 2 | 736 | 0 |
| `4+2` | 64 | 4 | 64 | 0 |
| `6` | 2,592 | 2 | 2,592 | 0 |
| **total** | **164,928** | **52** | **164,278** | **0** |

For rank-one `F`, a structurally different exact check partitions the 10,395
matchings by the mate of a canonical pivot: 11 branches of `9!!=945`.
The diagonal equations reject all eleven branches for every permutation.
For ranks two and three, NumPy is used only as a vectorized integer array
engine; every upper-triangle entry is reduced modulo seven and compared for
all 10,395 matchings for every minimum-`F` permutation. A direct positive
control finds exactly one matching when the target is deliberately set to a
legal `W_R`.

Thus no equality case in (1) survives. Every 39-point principal block has
rank at least 26. The verified transport

```text
rank_F7(N M N^T)=rank_F7(M)
```

then proves the stated universal floor.

## Post-freeze comparison

The requested discovery result hash is exactly

```text
8a9e58aaa1073ae4a87e183f904ce7f43eaa620bbac5a6f5d1f8445dd795dc85.
```

The secondary counts agree partition-by-partition with that discovery result
and with the frozen primary verifier: 164,928 minimum permutations, 52
canonical right kernels, 164,278 targets, and zero survivors. The methods
differ: discovery/primary scan 10,395 matchings once per canonical kernel,
whereas this checker uses pivot-mate reconstruction for rank one and
per-permutation vector scans for ranks two and three.

No theorem discrepancy was found. A transient positive-control lift bug
reported during primary-verifier development is absent from the frozen
primary result and did not affect any legal-matching absence count.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave41-rank26-secondary -p "test_*.py" -v

.\.venv\Scripts\python.exe -B `
  verification\wave41-rank26-secondary\secondary_check.py `
  --verify verification\wave41-rank26-secondary\secondary-results.json

.\.venv\Scripts\python.exe -B `
  verification\wave41-rank26-secondary\comparison_check.py `
  --verify verification\wave41-rank26-secondary\comparison.json
```

## Scope wall

```text
universal rank_F7(M)>=26:       VERIFIED
endpoint n3=4158:               UNKNOWN
general upper bound below 4158: NOT PROVED
best rigorous interval:         708 <= n3 <= 4158
Conway-99 existence:            UNKNOWN
graph construction:             NONE
novelty and priority:           UNKNOWN
```
