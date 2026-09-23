# Wave 40 endpoint rank floor: independent verification

Status: **VERIFIED**, narrowly for the conditional theorem

```text
n3=4158  ==>  rank_F7(M)>=22.
```

The prism-free endpoint itself remains **UNKNOWN**, the general bound remains
`n3<=4158`, and literature novelty remains **UNKNOWN**. This verifier was
written clean-room and neither imports nor executes the discovery program.

## 1. Local graph forced by the SRG axioms

Assume a hypothetical `srg(99,14,1,2)`. Fix an edge `xy`. The parameter
`lambda=1` says that `x` and `y` have a unique common neighbor `z`. Put

```text
X=N(x)-{y,z},  Y=N(y)-{x,z},  L={x,y,z} union X union Y.
```

Both `X` and `Y` have 12 vertices. If `u in X`, then the edge `xu` has one
common neighbor. It is neither `y` nor `z`, so it is another point of `X`.
Thus `X` induces a perfect matching; the same argument applies to `Y`.
Because `u` and `y` are nonadjacent, `mu=2` gives them common neighbor `x`
and exactly one common neighbor in `Y`. Counting from both sides proves that
the `X--Y` edges are a third perfect matching.

The union of these three matchings on `X union Y` has components of length
`4m`. At the endpoint `n3=4158`, equivalently the triangular-prism-free
case, no part `m=1` occurs. For ranks at most 21, only the two canonical
local types below need to be reconstructed:

| type | component lengths | rank of `K[L,L]` over `F_7` |
| --- | --- | ---: |
| `2+2+2` | `8,8,8` | 19 |
| `2+4` | `8,16` | 21 |

The verifier constructs each block directly from the three matchings and
checks their matching degrees and component sizes before elimination.

## 2. Why the twelve `z`-neighbors form a bijection

Let

```text
Z=N(z)-{x,y}.
```

It has size 12. No member of `Z` lies in `X` or `Y`: otherwise the edge
`xz` or `yz` would have a second common neighbor, contradicting
`lambda=1`. Hence `Z` lies outside `L`.

For `w in Z`, the nonedge `wx` already has common neighbor `z`; `mu=2`
forces exactly one additional common neighbor in `X`. Similarly, `w` has
exactly one neighbor in `Y`. Conversely, for each `u in X`, the nonedge
`uz` already has common neighbor `x` and therefore has exactly one further
common neighbor in `Z`. Since both sets have size 12, the `X--Z` incidence
is a perfect matching. The same holds for `Z--Y`. Eliminating `Z`, the
twelve required patterns are therefore a genuine bijection `X->Y`, not
twelve arbitrary or repeated choices.

There are exactly

```text
12*12=144
```

possible individual patterns. For such an outside vertex `w`, the
restricted transported column is

```text
K[L,w]=1-2 A[L,w],
```

with entries `6=-1` at `z`, the chosen `X` point, and the chosen `Y` point,
and entries 1 elsewhere.

## 3. Rank-completion quotient

The inherited, independently verified incidence identities are

```text
K=N M N^T=J-I-2A                    over F_7,
N^T N M=3M.
```

Since 3 is invertible modulo seven, `N` is injective on `im(M)`. Symmetry
then gives

```text
rank_F7(K)=rank_F7(M)=r7.
```

Write the global transported matrix in blocks as

```text
K = [ B   C  ],  B=K[L,L].
    [ C^T D  ]
```

If `R=col([B C])` is the restriction of the global column space to the rows
in `L`, then

```text
col(B) subseteq R,
dim(R)<=rank(K),
dim(R/col(B))<=rank(K)-rank(B).       (1)
```

Because `B` is symmetric,

```text
col(B)=ker(B)^perp.
```

Dot products with a basis of `ker(B)` therefore give exact quotient
syndromes. Zero syndrome means membership in `col(B)`.

## 4. Independent finite-field census

For type `2+2+2`, `B` has rank 19 and nullity eight. All 144 `Z` patterns
have nonzero syndrome. Their projective syndromes occupy 66 lines:

```text
60 lines contain 2 patterns,
 6 lines contain 4 patterns.
```

Every projective line includes all six nonzero scalar multiples in `F_7`;
the implementation tests this explicitly.

The two-space normalization is important. There are

```text
binom(66,2)=2,145
```

raw unordered pairs of observed lines, but only **1,923 distinct
dimension-two row spaces** after canonical RREF normalization. Thus 222 is
the count of duplicate pair descriptions, not an additional family of
spaces. The exact matching census is

| maximum bipartite matching | two-spaces |
| ---: | ---: |
| 2 | 480 |
| 4 | 1,251 |
| 6 | 168 |
| 8 | 24 |

For type `2+4`, `B` has rank 21 and nullity six, and again none of its 144
`Z` syndromes is zero.

## 5. The conditional theorem

Assume the endpoint and suppose `r7<=21`.

- If `r7=19`, every edge must have type `2+2+2`. Equation (1) gives
  quotient dimension zero, but none of the required `Z` columns lies in
  `col(B)`.
- If `r7=20`, every edge again has type `2+2+2`. The twelve distinct
  perfect-matching patterns must lie on one quotient line, but a line
  contains at most four patterns.
- If `r7=21` and some edge has type `2+4`, its local rank already equals the
  global rank. Equation (1) again gives quotient dimension zero, while all
  144 required syndromes are nonzero.
- Otherwise every edge has type `2+2+2`. The twelve patterns must fit in a
  quotient two-space, but every relevant two-space has matching number at
  most eight.

All possibilities `r7<=21` are contradicted. Therefore

```text
n3=4158  ==>  rank_F7(M)>=22.        VERIFIED
```

## 6. Positive stopping boundary

The verifier also canonicalizes all three-spaces generated by triples of
the 66 observed lines:

```text
raw unordered triples:              45,760
raw independent triples:            45,556
distinct generated three-spaces:    25,744
three-spaces with a perfect match:       32
```

A complete witness is stored in `independent-results.json`. This is a
positive control for the local quotient method: quotient dimension three
can hold all twelve patterns. It does **not** construct a global graph,
prove a rank-22 completion, or exclude any higher rank.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave40-rank19-equality -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave40-rank19-equality\independent_check.py `
  --verify verification\wave40-rank19-equality\independent-results.json
```

The 15 hostile tests reject a wrong `X--Y` matching, a non-bijective
`Z` witness, omitted projective scalars, malformed local ranks or censuses,
and endpoint, general-bound, or novelty status inflation.
