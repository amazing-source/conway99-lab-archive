# Wave 39 edge-local characteristic-seven rank

Status: **CANDIDATE pending independent verification**.

Choose an edge `xy` in a hypothetical `srg(99,14,1,2)` and let `z` be its
unique common neighbor. Put

```text
X=N(x)-{y,z},  Y=N(y)-{x,z}.
```

Both `X` and `Y` have twelve vertices and induce perfect matchings. The
nonadjacent-pair rule gives a perfect matching between `X` and `Y`. Their
three matchings form cycles of length divisible by four, indexed by one of
the eleven positive partitions of six.

Let `N` be the vertex--triangle incidence matrix and `M=21E_0` the integral
triangle projector. The previously verified identity

```text
N M N^T = 27I - 9A + J
```

has the same rank as `M` modulo seven. Indeed,
`N^T N M=(3I+Gamma)M=3M`, so `N` is injective on the column space of `M`;
symmetry gives the same statement on the other side. Modulo seven the
transport matrix is also the Seidel matrix

```text
J-I-2A.
```

Therefore every principal block on the 27 forced vertices

```text
L={x,y,z} union X union Y
```

to lower-bound `rank_F7(M)`. Exact elimination for every normal form gives

```text
rank_F7((27I-9A+J)[L,L])
  = 25 - 2*(number of even parts).
```

At most three positive even parts can sum to six, so every putative target
graph necessarily satisfies

```text
rank_F7(M) >= 19.
```

The prism-free endpoint permits only:

| partition | local rank over `F_7` |
| --- | ---: |
| `2+2+2` | 19 |
| `2+4` | 21 |
| `3+3` | 25 |
| `6` | 23 |

Combining the candidate floor with the previously verified
`12<=r3,r7<=44` ranges and even `r3+r7` leaves 429 arithmetic pairs, down
from 528. If `r3=12`, then `r7` must be even and at least 20.

This is not an endpoint exclusion. In particular the `2+2+2` normal form
survives. The next exposed low-rank boundary is:

```text
r7<=20  ==>  every graph edge has local partition 2+2+2.
```

Run:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave39-edge-local-rank -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave39-edge-local-rank\exact_check.py `
  --verify attempts\wave39-edge-local-rank\exact-results.json
```
