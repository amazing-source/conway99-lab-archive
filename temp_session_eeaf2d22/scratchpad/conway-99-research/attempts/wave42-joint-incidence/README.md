# Wave 42 canonical joint-incidence reduction

Status: **DERIVED, pending independent verification**. The prism-free
endpoint and Conway-99 remain **UNKNOWN**.

This package attacks the simultaneous outside-incidence problem for the
canonical Wave 41 rank-33 lift, mask `51739`, under the joint assumptions

```text
n3=4158,
rank_F3(M)=12,
every graph edge has local type 2+2+2.
```

No automorphism or outside-vertex symmetry is assumed.

## Exact reduction

For the canonical 36-vertex core `X`, the forced identity is

```text
BB^T = 12I-A_X+2J-RR^T-A_X^2.
```

The core has two connected components of sizes `12+24`, meeting each of the
three fibres in `4+8` points. For the small component indicator `u`, the
Gram identity gives

```text
sum_y |b_y intersect C|   = 120,
sum_y |b_y intersect C|^2 = 240.
```

Cauchy--Schwarz has the same lower bound `120^2/60=240`, so equality forces

```text
|b_y intersect C|=2
```

for every one of the sixty outside blocks.

Within each fibre the six matching pairs have Gram multiplicity zero and
all sixty other pairs have multiplicity one. Every outside block selects one
pair per fibre, so each fibre's sixty nonmatching pairs is used exactly once.
Thus every possible `B` is a three-way matching of three explicitly retained
60-element pair sets.

The component counts force the sixty blocks to have exactly

```text
4 each:  (2,0,0), (0,2,0), (0,0,2)
16 each: (1,1,0), (1,0,1), (0,1,1).
```

Complete enumeration then gives:

| necessary filter | candidate six-sets |
| --- | ---: |
| all pair triples | 216,000 |
| positive forced Gram support | 118,718 |
| component equality | 49,736 |
| mixed `BH` target nonnegative | 45,032 |

The remaining `B` question is exact: choose sixty of these 45,032 candidates
so that each named fibre-pair is used once and every cross-fibre point pair
has its forced Gram multiplicity. This is exhaustive and has no symmetry
restriction.

## Exact positive control

`exact-results.json` contains a full 60-entry permutation pairing all
fibre-0 nonmatching pairs with all fibre-1 nonmatching pairs. Direct
reconstruction verifies every entry of the required `12 x 12` concurrence
matrix `Q_01`.

This rules out a contradiction based only on one or two fibres. It is not a
three-fibre `B`: no fibre-2 choice is attached.

## What `H` would still have to satisfy

The canonical core has ten four-cycles. If a simultaneous `B` exists, its
1,770 unordered column pairs have overlap census

```text
overlap 0 / 1 / 2: 458 / 1004 / 308.
```

Any compatible simple eight-regular outside graph must have

```text
96 overlap-zero edges,
144 overlap-one edges,
0 overlap-two edges,
32 triangles,
181 four-cycles,
```

and satisfy simultaneously

```text
BH            = (J/3-I-A_X)B,
B^TB + H^2    = 12I-H+2J.
```

The package does not construct or exclude such a `B` or `H`.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave42-joint-incidence\exact_check.py `
  --verify attempts\wave42-joint-incidence\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave42-joint-incidence -p "test_*.py" -v
```

