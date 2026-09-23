# Wave 41: all rank-eleven all-222 quotient lifts

Status: **CANDIDATE pending independent verification**. Conway-99 and the
prism-free endpoint remain **UNKNOWN**.

This package closes the finite gap left by Wave 40 between the eight
normalized rank-eleven all-`222` quotients around a graph triangle. It also
adds exact triangle-free endpoint-pairing counts to the complete 4,050-form
all-`222` quotient census.

## Exact result

The eight normalized rank-eleven records are not eight different
fibre-coloured structures. Exact source-to-target vertex maps prove that
they are one fibre-preserving isomorphism class.

For each quotient isomorphism, the checker constructs the induced affine
bijection

```text
F_2^18 -> F_2^18
```

on the omitted endpoint-pairing bits. It checks all `8*2^18=2,097,152`
source masks against that bijection. Triangle-freeness is preserved exactly,
and each transported lift is graph-isomorphic after independent swaps of
the two endpoints at its eighteen contracted matching edges.

One canonical `2^18` census performs exact Gaussian elimination over
`F_7`; each of the other seven complete censuses is then transported through
its certified graph isomorphism. Every case has:

| quantity | exact value |
| --- | ---: |
| endpoint-pairing masks | 262,144 |
| triangle-free masks | 37,378 |
| `rank_F7(K39)=33` | 264 |
| `rank_F7(K39)=34` | 7,348 |
| `rank_F7(K39)=35` | 29,766 |

Thus the minimum is 33 for **all eight**, not only the Wave 40 canonical
record. Every case includes an explicit rank-33 witness checked by both
sparse symmetric elimination and independent dense elimination.

## Conditional candidate theorem

Assume jointly:

```text
n3=4158,
r3=rank_F3(M)=12,
all 693 graph edges have local type 2+2+2.
```

For every graph triangle `T`, the independently verified quotient bridge
gives

```text
rank_F3(2I+A_P)<=r3-1=11.
```

The complete quotient census leaves exactly the eight cases above. Hence

```text
rank_F7(K[T union N(T)])>=33
```

for every `T`. A submatrix cannot have rank larger than the full matrix, so
the joint branch has `r7>=33`; the existing parity condition makes this

```text
r7 even and r7>=34.
```

This is a **CANDIDATE** until independently reconstructed. It is not an
endpoint exclusion because the hypotheses do not prove that every endpoint
edge has type `222`.

## Extended 4,050-form census

For every normalized all-`222` quotient, the checker converts each quotient
triangle into one forbidden three-bit assignment. Python integer bitsets
then count all triangle-free masks exactly.

The quotient-rank ranges are:

| quotient rank over `F_3` | forms | triangle-free masks per form |
| ---: | ---: | ---: |
| 11 | 8 | 37,378 |
| 12 | 1 | 10,648 |
| 13 | 400 | 31,768--164,864 |
| 14 | 46 | 28,512--262,144 |
| 15 | 2,616 | 65,664--160,000 |
| 16 | 979 | 46,656--262,144 |

All 4,050 forms admit a triangle-free local lift. Nineteen forms have no
quotient triangles at all and therefore allow all `2^18` pairing masks.
The complete 29-cell joint distribution is in `exact-results.json`.

## Scope wall

The quotient and a pairing mask determine only the cubic 36-vertex graph
`X=G[N(T)-T]` around one base triangle. They do not supply:

- the sixty outside vertices or their `36 x 60` incidence matrix `B`;
- the compatible eight-regular outside graph `H`;
- agreement between overlapping triangle neighborhoods;
- a 99-vertex graph or a prism-forcing contradiction.

In particular, 264 rank-33 lifts survive in every normalized rank-eleven
case. The local relaxation therefore does not solve the endpoint.

## Rank-33 border roadblock

The tempting raw border-rank continuation fails for a structural reason.
Every `K39` has three independent fibre-star kernel vectors. For fibre `i`,
put `(4,1,1)` on `T`, with `4` at its corresponding base vertex; put `1` on
all twelve vertices of fibre `i`; and put `0` on the other fibres.

Every outside vertex is nonadjacent to `T` and has exactly two neighbors in
each 12-point fibre. Its `K`-column therefore pairs with the corresponding
fibre-star vector as

```text
(4+1+1) + (10-2) = 14 = 0 mod 7.
```

At local rank 33 the kernel dimension is six, but three independent kernel
vectors already annihilate every possible balanced outside column. Hence

```text
rank(H^T U) <= 3
```

automatically. The full-rank-at-most-44 condition would require only
`rank(H^T U)<=5`, so the symmetric border lemma cannot force rank 45 here.

The next useful certificate must use structure beyond raw border rank:
simultaneous binary realization of `B`, the compatible outside graph `H`,
the full `K^2=0` identities, or overlap compatibility among different base
triangles.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave41-allquotient-lifts -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave41-allquotient-lifts\exact_check.py `
  --verify attempts\wave41-allquotient-lifts\exact-results.json
```
