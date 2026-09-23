# Wave 3 fiber-coupling lane

```yaml
role: proof_a
date_utc: 2026-07-22T21:30:08Z
git_commit: 98ee7b3dac89d57f09c583f83a356b3ef9541b3e
base_commit: d1b6d3d237bac44d10123b7d190c46f092d74eee
claim_label: DERIVED
scope: exact necessary consequences of the unrestricted rooted residual equations
inputs:
  CONJECTURE.md: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  agents/2026-07-22-wave2-structural.md: a495e82d2df7c158c3845d6a2265aeab13cf87256a242673f183a657d32cea1f
method: block-matrix algebra, exact relation counting, synthetic boundary controls, and independent reconstruction
command: not_applicable_human_exact_derivation
outputs: not_applicable_no_computational_artifact
limitations: no contradiction; synthetic endpoint controls are not full residual graphs; novelty is unknown
```

Fix a root group `g={a,abar}` and index its two 12-vertex fibers by the 12
coordinates outside `g`: `u_x={a,x}` and `v_x={abar,x}`. Let `W_g` be the 60
labels avoiding `g`, and put

```text
A = B[F_a,F_a],       N = B[F_abar,F_abar],
P = B[F_a,F_abar],    E = B[F_a,W_g],
F = B[F_abar,W_g],    R = E F^T,       L = I_12.
```

Here `A,N,P` are permutation matrices, with `A,N` fixed-point-free matchings.
The cross-fiber block of the residual SRG equation gives

```text
R = 2J - L - P - AP - PN.                         (1)
```

Let `m_xy=(L+P+AP+PN)_xy`. Since `R` counts common `W_g` neighbors,
`R_xy=2-m_xy>=0`, so at most two marks can occupy a cell. The matrix `P` is
cell-disjoint from both `AP` and `PN`; the only otherwise possible triple is
`L=AP=PN=1`, which equation (1) also forbids. Therefore `R` has entries
`0,1,2`, every row and column sums to 20, and its row and column profiles are

```text
(number of 0s, number of 1s, number of 2s)
  (0,4,8), (1,2,9), or (2,0,10).
```

## Separated four-cycles

Let `z_g` count the cells occupied twice among `L,P,AP,PN`. There are 48
marks and no triple overlap, so

```text
S_g = number of R=2 cells = 96 + z_g,
0 <= z_g <= 24.                                    (2)
```

Each such cell determines exactly one residual four-cycle separated by group
`g`, and distinct cells give distinct cycles for that group. Hence the seven
groups contribute between 672 and 840 separation incidences. Since the
residual graph has 1,071 four-cycles, at least 231 are separated by no root
group. A single cycle can be separated by at most four groups. These are exact
counts, not a contradiction.

Abstract local permutation systems realize both `z_g=0` and `z_g=24`. This
only shows sharpness of the local algebra; it does not construct compatible
matrices `E,F`, a residual graph, or a Conway graph.

## Global relation algebra

With `Q=C^T C` and `D=C^T M C`, the incidence equation `CB=2J-C-MC` gives

```text
BQ = BD = 4J-Q-D,
B(Q-D)=0.                                           (3)
```

For a residual vertex `p`, let `(b_p,d_p,e_p)` count selected edges of types
`(Q,D)=(1,1),(0,1),(0,2)`. Equation (3) and the fixed two selected `Q=1`
neighbors force

```text
(b_p,d_p,e_p) in
{(2,0,0), (1,1,0), (0,2,0), (0,0,1)}.              (4)
```

The selected `D=2` edges form a matching. After removing their endpoints, the
selected `D=1` edges form a 2-factor. This packaging alone does not exclude
odd cycles. Equivalently,

```text
sum_{q:D_pq=1} x_pq + 2 x_{p,pbar} = 2.             (5)
```

If `x=e_11` and `y=e_02`, all selected edge-relation counts are

```text
e_10=84-x,  e_11=x,       e_02=y,
e_01=84-x-2y,             e_00=336+x+y,
x+2y<=84.                                             (6)
```

Finally, direct expansion gives

```text
B^3 = 13B - 12I + 18J + 2Q + D.                     (7)
```

After subtracting the 23 backtracking walks, an edge `pq` lies in
`8+2Q_pq+D_pq` residual four-cycles:

| edge type `(Q,D)` | cycles through edge |
|---|---:|
| `(1,0)` | 10 |
| `(1,1)` | 11 |
| `(0,0)` | 8 |
| `(0,1)` | 9 |
| `(0,2)` | 10 |

The total edge-cycle incidence is `4,284=4*1,071`, an independent checksum.
All identities were reconstructed by the independent Wave 3 verifier and
assume no nontrivial automorphism of the completed graph.
