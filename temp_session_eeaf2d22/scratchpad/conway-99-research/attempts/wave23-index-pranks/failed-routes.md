# Wave 23 retained incomplete and failed routes

These routes are not evidence for nonexistence.  They are retained so that a
later run does not silently repeat the same rank inferences.

## 1. The characteristic-seven rank is not fixed by the displayed identities

Let `N` be the vertex/triangle incidence matrix and put

```text
R = 3I-A+J/9,
S = 2A-J+I.
```

The parameter-forced adjacency rank gives `rank_F7(N)=99`: if
`N^T x=0`, then `Ax=NN^T x=0`; the verified kernel of `A mod 7` is
`<1>`, but `N^T1=3*1` is nonzero.  Hence

```text
rank_F7(M)=rank_F7(R)=rank_F7(S),
```

where `5R=S mod 7`.  Exact adjacency-algebra multiplication gives

```text
S^2=49(I+J).
```

It is tempting to infer `rank_F7(S)=44` from its rational spectrum, but this
does not follow.  Modulo seven, `S` is merely square-zero; the rational
`+7` and `-7` eigenspaces have collided.  Their integral gluing is exactly
the missing Smith/index datum.  The general square-zero bound is only 49 on
the 98-dimensional sum-zero space, and the rational-rank bridge only lowers
the relevant rank to at most 44.  No lower bound of 44 was proved.

## 2. The characteristic-three incidence identity is too weak

The exact rational factorization gives

```text
NM=3(3I-A)N+J,
NM=J mod 3.
```

Also `rank_F3(NN^T)=rank_F3(A+I)=55`, while `N^T1=0`, so the elementary
bounds are

```text
55 <= rank_F3(N) <= 98.
```

The rank-one image of `NM` does not determine `rank_F3(M)`.  In particular,
it does not distinguish the endpoint possibilities

```text
h=1  -> rank_F3(M)=44,
h=9  -> rank_F3(M)=42.
```

No unsupported assumption that the triangle incidence columns generate the
entire sum-zero lattice modulo three is made.

## 3. Direct characteristic-polynomial classification was unnecessary

An attempted route was to classify every totally positive integral
characteristic polynomial of the near-identity endomorphism `B`.  The
two-moment optimization makes that classification unnecessary.  Abstract
integral positive matrices with spectra

```text
5,1^43
3,3,1^42
```

already meet `tr(B)=48`, `B=I mod 2`, and respectively give determinant
five and nine.  Thus moment and congruence data alone should not be described
as excluding those determinant values.  The endpoint closes only after the
separate lattice-index obstruction to `h=1`.

## 4. No claim about the value of h away from the endpoint

The new endpoint contradiction does not determine `h` for a hypothetical
target globally, and it does not prove either modular rank.  It only proves
that the already-audited endpoint package at `n3=705` is inconsistent.
