# Failed and surviving routes

## Hypergraph Gram PSD: survives

With `Z` the 84-by-140 point/block incidence matrix,

```text
D+5I = ZZ^T,
R+3I = Z^T Z.
```

Thus `lambda_min(D)>=-5`, `lambda_min(R)>=-3`, and `R` has eigenvalue `-3`
with multiplicity at least 56. These restrictions are consistent. The
package includes an exact 84-point, 140-block local positive control.

## Finite fields: necessary ranks only

Modulo 3, `Z^T 1=0`, hence `rank_3(Z)<=83`. The analogous Gram-rank
statements modulo 2, 5, and 7 do not exclude the endpoint. The positive
control supplies exact ranks as a null calibration.

## Fourth moments: a transfer identity, not a contradiction

Every point gives a `K5` among the blocks, contributing 15 four-cycles.
Exact Gram moments give

```text
c4(R)=1260+c4(D).
```

Since `D` is a subgraph of a target `B`, and `c4(B)=1071`, a target must have
`1260<=c4(R)<=2331`. The interval is nonempty.

## One-point averaged PSD: survives all 43 integer parameters

The scaffold average of `D+5I` has six rational eigenvalue blocks. Every
block is nonnegative for every `y=0,...,42`; the minimum is `12/5`. This is
only a necessary averaged condition.

## Scalar spectral overlap: survives

Writing `w=tr(T E_3)`, exact mixed traces and `-2I<=T<=2I` give

```text
64/5 <= w <= 16,
5376 <= tr(B^3 T) <= 5712,
tr(B^4 T)+3 tr(B^3 T)=52416.
```

The package records the exact feasible value `w=14`. Scalar projector traces
therefore do not encode the missing entrywise compatibility.

## First missing layer

The first unresolved invariant is noncommutative and two-rooted: the relative
placement of the 140 columns of `Z` and the transition 2-factor `T` inside the
fixed 84-label scaffold, subject entrywise to

```text
(T+D)^2+(T+D)=10I+2J-Q.
```

The local positive control demonstrates why degrees, local triangles,
factorization PSD, and low moments alone cannot replace this coupling.
