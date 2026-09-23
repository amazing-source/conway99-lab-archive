# Wave 39 edge-local rank: independent verification

Status: **VERIFIED**, scoped to the universal rank consequence and its stated
conditional endpoint refinements. The Conway 99-graph problem and the
prism-free endpoint remain **UNKNOWN**.

## Clean-room reconstruction

Fix an edge `xy` and let `z` be its unique common neighbor. Define

```text
X=N(x)-{y,z},  Y=N(y)-{x,z}.
```

The parameters `(99,14,1,2)` force `|X|=|Y|=12`. The graph induced by either
side is 1-regular, hence a perfect matching. For `u in X`, the nonadjacent
pair `u,y` has common neighbor `x` and exactly one further common neighbor in
`Y`; therefore the cross relation is also a perfect matching.

Relabel `X` to fix its matching and pull the labels of `Y` back through the
cross matching. The remaining freedom is an arbitrary perfect matching on
twelve labelled points:

```text
(11)!! = 11*9*7*5*3*1 = 10,395.
```

The verifier exhausts all 10,395 choices. Their 24-point union is 2-regular,
and its three edge colors force every component length to be divisible by
four. Thus the component lengths are `4m` for one of the eleven positive
partitions of six. No automorphism of a completed 99-vertex graph is assumed.

## Rank transfer

The frozen identity is

```text
N M N^T = 27I - 9A + J,
```

where `N` is vertex-triangle incidence and `M=21E0` is symmetric. Also

```text
N^T N M = (3I+Gamma)M = 3M.
```

Over `F_7`, `3` is invertible. If `v` lies in `im(M)` and `Nv=0`, then
`0=N^T Nv=3v`, so `v=0`. Hence `N` is injective on `im(M)`. This gives

```text
rank_F7(NM)=rank_F7(M),
rank_F7(MN^T)=rank_F7(M),
rank_F7(NMN^T)=rank_F7(M).
```

Modulo seven, the transported matrix is `J-I-2A`. For every one of the
10,395 local configurations, the verifier independently builds its 27 by 27
principal block and performs Gaussian elimination over `F_7`. For a positive
partition `pi` of six, the exhaustive table satisfies

```text
local rank = 25 - 2*(number of even parts of pi).
```

The minimum is 19, at `2+2+2`. A principal block cannot have rank larger than
the full transported matrix, so every hypothetical target graph satisfies

```text
rank_F7(M) >= 19.
```

## Conditional prism-free consequences

A part `1` is a four-cycle in the three-matching union. Together with `xy`,
its four vertices form exactly an induced triangular prism containing `xy`.
Thus the conditional prism-free endpoint permits precisely:

| partition | local rank over `F_7` |
| --- | ---: |
| `2+2+2` | 19 |
| `2+4` | 21 |
| `3+3` | 25 |
| `6` | 23 |

Using the previously verified ranges `12<=r3,r7<=44` and parity
`r3+r7` even leaves

```text
17*13 + 16*13 = 429
```

arithmetic rank pairs. If `r3=12`, then `r7` is even and at least 20.
Moreover, conditionally at the endpoint:

- `r7<=20` forces every edge to have type `2+2+2`;
- `r7<=22` permits only `2+2+2` or `2+4`;
- `r7<=24` excludes edge type `3+3`.

These are necessary conditions only. They do not couple the types of
different edges, exclude the endpoint, improve `n3<=4158`, construct a
graph, or certify literature novelty.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave39-edge-local-rank -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave39-edge-local-rank\independent_check.py `
  --verify verification\wave39-edge-local-rank\independent-results.json
```

The test suite contains fourteen tests, including hostile mutations of the
partition ranks, universal floor, endpoint status, novelty status, frozen
parameters, matching validity, and JSON structure.
