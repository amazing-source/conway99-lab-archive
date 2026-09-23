# Wave145 verification: Wave139 GF(4) lower-bound aggregation

Verdict: `REFUTED` for the Wave139 `max` aggregation and its pure-`Y`
weight-8/10/12 zero rows; `VERIFIED` for the corrected summed lower bounds
and the Rains shadow convention. Corrected enumerator feasibility remains
`UNKNOWN`.

## Frozen scope

The verifier froze the 12-entry Wave139 package at manifest SHA-256
`fa1d00ddc9ab25d00126bc82f32d7e0c5a703c4a7efe355ed49dc111dda2058d`
and independently checked every manifest entry. It also froze the Wave136
three-class support table and the Wave131 image/kernel distributions.

The graph-state codeword indexed by \(x\in\mathbf F_2^{99}\) is

```text
(x,Ax).
```

In the state order `(nI,nY,nR)`, `nR` merges the `X` and `Z` symbols.

## The aggregation error

Wave139 combines three certified word families:

```text
mixed:  (x,Ax), 1 <= wt(x) <= 3
pure Y: (y,y),  y in im(A)
pure X: (k,0),  k in ker(A).
```

The nonzero families are pairwise disjoint:

1. The first component makes \(x\mapsto(x,Ax)\) injective.
2. Every frozen mixed row has `wt(Ax)` between 14 and 36, so no mixed word
   is pure `X`.
3. Every frozen mixed row has `nR>0`, so no mixed word is pure `Y`.
4. `(y,y)=(k,0)` forces `y=k=0`; the two pure axes share only the zero word.

None of these arguments assumes an image or kernel minimum greater than
eight.

Therefore lower bounds from mixed and pure-`X` families that land in the
same three-class state must be **summed**, not merged with `max`:

| state `(nI,nY,nR)` | mixed | pure `X` | Wave139 `max` | corrected sum |
|---|---:|---:|---:|---:|
| `(84,0,15)` | 99 | 99 | 99 | **198** |
| `(73,0,26)` | 4,158 | 4,158 | 4,158 | **8,316** |
| `(66,0,33)` | 70,686 | 79,002 | 79,002 | **149,688** |
| `(62,0,37)` | 27,720 | 27,720 | 27,720 | **55,440** |
| `(60,0,39)` | 231 | 231 | 231 | **462** |

The common zero word remains coefficient one and is not summed twice.
No other mixed/pure-axis state collision occurs in the frozen tables.

## Pure-`Y` zero-row correction

The frozen structural result is only
\(d(\operatorname{im}A)\ge8\). Since the image code is even, it proves
pure-`Y` weights 2, 4, and 6 vanish. It does **not** prove weights 8, 10,
or 12 vanish. Wave139 imposed those three unsupported equalities, so they
are vetoed.

Weights 94, 96, and 98 do vanish by a separate argument that uses no
stronger minimum. If \(y\in\operatorname{im}A\), idempotence gives \(Ay=y\).
Put \(z=\mathbf1+y\). Since \(A\mathbf1=0\), \(Az=y\), while the union bound
over weight-14 rows gives

```text
wt(Az) <= 14 wt(z).
```

For `wt(y)=94,96,98`, the complement weights are `5,3,1`, and respectively
`94>70`, `96>42`, `98>14`, contradictions. The corrected pure-`Y` zero
set is therefore exactly

```text
{2,4,6,94,96,98}
```

at the present verified strength.

## Quantum-shadow convention

Rains's [Quantum shadow enumerators](https://arxiv.org/abs/quant-ph/9611001),
Theorems 8 and 10, gives

```text
S_j = 2^-n sum_t (-1)^t K_j^(4)(t) H_t >= 0,
K_j^(4)(t) = [z^j](1+3z)^(n-t)(1-z)^t.
```

The normalization was also checked independently from the graph code. For
a simple graph with degree-parity vector \(d\),

```text
wt(x,Ax) mod 2 = (1+d) dot x.
```

Thus the shadow is the explicit coset

```text
(0,1+d) + {(x,Ax)}.
```

For the target 14-regular graph this becomes
`(0,1)+{(x,Ax)}`. The verifier exhaustively compared the transform with
direct coset enumeration for all 1,099 simple graphs through order five:
all 6,504 coefficients agreed exactly. The triangle control maps ordinary
distribution `[1,0,3,4]` to shadow distribution `[0,3,0,5]`.

The formula and normalization are therefore verified for this layer. No
shadow inequality was needed to establish the aggregation correction.

## Reproduction

```powershell
python -B verification\wave139-gf4-lower-aggregation\independent_verify.py

python -B -m unittest discover `
  -s verification\wave139-gf4-lower-aggregation `
  -p "test_*.py" -v
```

The verifier reports `PASS_WITH_WAVE139_VETO`; all eight hostile tests pass.

## Status wall

The corrected 2,550-state relaxation was not solved exactly. An attempted
floating scout did not start because the default Python lacked NumPy, and
no numerical result is included. There is no rational primal point, dual
upper bound, or Farkas certificate. No graph or adjacency matrix is
constructed or excluded, no improved `n3` upper bound follows, and
Conway-99 remains `UNKNOWN`.
