# Independent graphicality derivation

Claim label: `VERIFIED`, conditional on the frozen and previously verified
Wave 81 43+7 outside type-degree histogram domain.

## 1. Conditional domain and indexing

The input contains 43 distinct histogram triples at `t=0` and seven at
`t=1`, where `t` is the number of edges induced by the eight `X2`
vertices. The verifier checks that:

- the only source keys are `0` and `1`;
- the lane lengths are exactly 43 and seven;
- all 50 histogram triples are distinct;
- each histogram has the stated width, nonnegative integral entries, and
  populations `|X0|=11`, `|X1|=64`, and `|X2|=8`.

Rows retain their source-list order. For example, `t0-row-40` denotes
zero-based source index 39. This makes the finite audit complete and
unambiguous.

## 2. Reconstructing all six degree sequences

For a vertex in `Xd`, let `a` be its number of neighbors in `X2`. The
previously verified local equations are

```text
b = 16-5d-2a,     c = a+3d-2,
```

where `b` and `c` are its degrees into `X1` and `X0`. Thus every histogram
triple fixes the following six subgraph degree sequences:

| subgraph | first-side degree | second-side degree |
|---|---:|---:|
| `X0` induced | `a-2` | - |
| `X0-X1` | `16-2a` on `X0` | `a+1` on `X1` |
| `X0-X2` | `a` on `X0` | `a+4` on `X2` |
| `X1` induced | `11-2a` | - |
| `X1-X2` | `a` on `X1` | `6-2a` on `X2` |
| `X2` induced | `a` | - |

The machine-readable artifact records run-length encoded sequences and
degree sums for all six pairs in all 50 rows: 300 exact checks.

## 3. Independent exact criteria

For each induced graph the primary checker applies the
Erdos-Gallai inequalities to the sorted degree sequence `d`:

```text
sum_{i<=k} d_i
  <= k(k-1) + sum_{i>k} min(k,d_i)
```

for every `k`, together with integral bounds and even total degree. A
separate Havel-Hakimi reduction must return the same answer.

For each bipartite graph the primary checker applies the Gale-Ryser
inequalities to the two sorted side sequences. A separate bipartite
Havel-Hakimi reduction must agree. There are no disagreements.

The tests additionally enumerate every simple graph through six vertices
and every `3 x 3` bipartite graph. The exact criteria match these
brute-force oracles on every possible tiny degree-sequence input.

## 4. Exact rejection set

Exactly three rows fail, all in the `t=0` lane and only for the `X0`
induced graph:

| row | `X0` induced sequence | first failed Erdos-Gallai inequality |
|---|---|---|
| `t0-row-40` | `[4,3,1,1,1,0^6]` | `k=2`: `7>5` |
| `t0-row-42` | `[4,2,2,2,0^7]` | `k=1`: `4>3` |
| `t0-row-43` | `[3,3,3,1,0^7]` | `k=2`: `6>5` |

For the third row, the inequality at `k=3`, namely `9>7`, also fails; the
independent implementation reports the earlier failure at `k=2`. This is
only a witness-order clarification and does not change the source claim.

The per-pair census is:

```text
X0 induced: 47 graphical, 3 nongraphical
X0-X1:      50 graphical, 0 nongraphical
X0-X2:      50 graphical, 0 nongraphical
X1 induced: 50 graphical, 0 nongraphical
X1-X2:      50 graphical, 0 nongraphical
X2 induced: 50 graphical, 0 nongraphical
```

Therefore the exact strengthened necessary census is:

```text
t=0: 40
t=1:  7
```

## Boundary

Graphicality of each degree sequence separately does not imply that all
six type-pair subgraphs can be realized simultaneously, much less that
the vertex-by-vertex strongly regular common-neighbor equations hold.
No 83-vertex outside graph is constructed. The norm-16 branch remains
live; Conway-99 and novelty remain `UNKNOWN`.
