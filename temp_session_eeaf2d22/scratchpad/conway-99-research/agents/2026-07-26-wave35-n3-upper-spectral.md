# Wave 35 endpoint signed-projector attack

```yaml
role: proof_b
date_utc: 2026-07-26T21:59:31Z
git_commit: 6d98cb5f73c1f56d227e97b1c3e70d363669bf87
claim_label: DERIVED_INCONCLUSIVE
scope: >
  Exact spectral, Smith, modular, Schur/Krein, interlacing, and
  incidence-local attack on the conditional endpoint n3=4158.
inputs:
  attempts/wave20-global-obstruction/exact-checks.json: 6aea5c4688880a33d358ccc8992ef3aa63d40be70b5c450a8a39bf83b4878dc2
  agents/2026-07-23-wave20-global-schur.md: 64352e1d96ed9a924e075c2d0659be8de887751194068a14b096e112a9320632
method: >
  Exact signed-projector algebra; invariant-factor bookkeeping; integral
  orthogonal-reflection reformulation; Schur-power collapse; primitive
  projector compression; incidence double counting; and exact local PSD
  controls.
command: |
  python -B -m unittest -v attempts/wave35-n3-upper-spectral/test_exact_check.py
  python -B attempts/wave35-n3-upper-spectral/exact_check.py --output attempts/wave35-n3-upper-spectral/exact-results.json
  python -B attempts/wave35-n3-upper-spectral/exact_check.py --verify attempts/wave35-n3-upper-spectral/exact-results.json
outputs:
  attempts/wave35-n3-upper-spectral/exact_check.py: 9146fd09b3ded2db31a1e9449eee1960b40247e0a4d78e67cadb4554cb4dd591
  attempts/wave35-n3-upper-spectral/test_exact_check.py: 8256c38aec55fa67ed85559828274cfd7c87d2b53ce24cb7b98e5d70341de8f5
  attempts/wave35-n3-upper-spectral/exact-results.json: ca1df07bede11642fb1639a2ae554c1a31ce9a58424d5b3e5031c90ad550a194
  attempts/wave35-n3-upper-spectral/failed-routes.md: bef6dce55d52bac94260c22f6a7710dcad15cd15b555d9331bd778bae9d7f692
limitations:
  - Discovery-side derivation pending independent review.
  - No endpoint matrix, incidence geometry, or Conway graph is constructed.
  - No upper-bound improvement or target resolution is claimed.
```

## Verdict

The endpoint survives this lane.

Conditional on `n3=4158`, the projector matrix has no `-2` off-diagonal
entries.  Writing

```text
M=4I+S
```

gives the frozen signed profile

```text
S row: +1^32, -1^36, 0^162,
S1=-4*1,
S^2=13S+68I,
spec(S)=17^44,(-4)^187.
```

The analysis produces two exact structural consequences:

```text
SNF(S)=diag(1^44,4^143,68^44),                       (1)
C=2S-13I=2M-21I,  C^2=441I.                         (2)
```

Neither is contradictory.  Raw Schur powers, every previously accepted
mixed primitive-projector Schur triple, the tested compression inequalities,
and the immediate incidence-local principal blocks all remain feasible.
Thus this lane does not improve the rigorous general ceiling

```text
n3<=4158.
```

Conway-99 remains `UNKNOWN`.

## 1. Frozen endpoint algebra

For a graph triangle `T`, let `q(T)=12-p(T)`, where `p(T)` is its number of
triangular-prism partners.  The equality `n3=4158` forces `q(T)=12` for all
231 triangles.  The fixed row profile is therefore

```text
(a0,a1,a2,a3)=(32,144,36,0).
```

The rank-44 integral projector scaling has

```text
M^2=21M,
M1=0,
M[T,T]=4,
M[T,U] in {+1,0,-1} for T!=U.
```

Subtracting `4I` gives `S`.  Its spectrum follows immediately from that of
`M`, and expansion gives

```text
S^2=(M-4I)^2=13S+68I.                                (3)
```

The diagonal of (3) is the row-support identity `32+36=68`; its row sum is
`32-36=-4`.

## 2. Exact Smith form of the signed matrix

Equation (3) factors as

```text
S(S-13I)=68I.                                        (4)
```

Thus every Smith invariant factor of `S` divides 68.  Also

```text
|det S|=17^44 * 4^187.                               (5)
```

The inherited rank argument gives `rank_F2(M)=44`: the sum of all principal
44-minors is the odd number `21^44`, while the rational rank is 44.
Since `S=M mod 2`,

```text
rank_F2(S)=44.                                       (6)
```

There are therefore 44 odd invariant factors and 187 even ones.  By (4),
each even factor has 2-adic valuation at most two.  Equation (5) has total
2-adic valuation `374=2*187`, so every even factor has valuation exactly two.

There are exactly 44 factors containing 17.  The invariant-factor
divisibility chain prevents an odd factor 17 from preceding a factor 4:
that would force every later factor to contain 17, exceeding the available
44 factors.  Hence the 44 odd factors are all one, the next 143 factors are
four, and the last 44 are 68.  This proves (1).

This is a restriction, not an obstruction: every factor divides 68, their
product is (5), and the modular rank is correct.

## 3. Integral orthogonal-reflection form

Put

```text
C=2S-13I=2M-21I.
```

Using (3),

```text
C^2=4S^2-52S+169I=441I.
```

Every row of `C` has:

```text
one diagonal -13,
32 entries +2,
36 entries -2,
162 zeroes.
```

Its row sum is `-21` and squared norm is

```text
13^2+4(32+36)=441.
```

Thus `C/21` is a rational orthogonal involution with `+1` multiplicity 44
and `-1` multiplicity 187.  This exact reformulation may be useful for a
future 2-adic or integral-orthogonal classification, but the displayed
determinant and parity data do not contradict it.

## 4. Schur powers collapse in the feasible direction

Since every off-diagonal entry is `0,+1,-1`,

```text
M^(o k)=M+(4^k-4)I,       k odd,
M^(o k)=W+(4^k-16)I,      k even, k>=2,
```

where `W=M o M`.  In particular,

```text
M o M o M=M+60I
```

is positive definite with eigenvalues

```text
81^44,60^187.
```

All forty previously accepted primitive-projector mixed Schur traces are
nonnegative at `n3=4158`.  Hence neither raw Schur powers nor their simplest
Krein compressions exclude the prism-free endpoint.

## 5. Unsigned-support compression has large slack

Let

```text
B=M o M-16I=S o S.
```

This is a 68-regular simple graph on the 231 triangle indices.  Scaling the
accepted mixed projector traces gives

```text
tr(E_18 B)=68,
tr(E_7 B)=-648/5,
tr(E_0 B)=-44,
tr(E_-3 B)=528/5.                                   (7)
```

They sum to zero as required.  Rank-wise Cauchy--Schwarz applied to the four
compressions consumes only

```text
126588/25
```

of

```text
tr(B^2)=231*68=15708.
```

The remaining exact slack is

```text
266112/25.
```

Thus these traces do not control enough of the off-block Frobenius mass for
an interlacing contradiction.

## 6. Incidence Frobenius bound also survives

Let `N` be the 99-by-231 vertex-triangle incidence matrix.  The inherited
identities give entries of `M N^T`:

```text
4  on the three points of T,
-2 on the 36 points adjacent to one point of T,
+1 on the remaining 60 points.
```

For `D=B N^T`, the corresponding values are

```text
0, 2, 1+2t_x,
```

where `0<=t_x<=3` and `sum t_x=36` over the final 60 points.  Convexity and
the integer bounds give

```text
492 <= ||D_T||^2 <= 780,
113652 <= ||D||_F^2 <= 180180.                       (8)
```

On the other hand, decomposing through the four `Gamma` eigenspaces gives

```text
||D||_F^2=97104+10x_7+3x_0,
x_theta=tr(E_theta B^2).
```

The traces in (7) give only

```text
x_7>=7776/25,
x_0>=44,
||D||_F^2>=501732/5=100346.4.
```

This is below (8).  The scalar values

```text
x_7=8208/5,
x_0=44,
x_-3=46992/5
```

meet all displayed trace and Cauchy conditions and attain the lower endpoint
113652.  They are not a matrix or graph; they show exactly why this scalar
route stops.

## 7. Immediate incidence-local blocks are positive

For adjacent original vertices, their two seven-triangle cliques share one
triangle.  After deleting it, the `6+6` cross-block is the negative
incidence matrix of two disjoint perfect matchings.  Their union is one of

```text
C12, C8+C4, C6+C6, C4+C4+C4.
```

Its operator norm is at most two, so the corresponding `4I` Gram block is
positive definite in every case.

For nonadjacent vertices, the exact checker gives a `7x7` control satisfying
the forced row and column sums

```text
(-2,-2,1,1,1,1,1),
```

the two shared-common-neighbor zero cells, and the two forced negative cells.
It has thirteen nonzero entries, so its operator norm is at most
`sqrt(13)<4`; the associated `14x14` Gram block is positive definite.

This is only a local relaxation.  It does not realize the full matrix
identity or a graph.

## 8. A precise remaining principal-minor target

Rank 44 forces every 45-row principal Gram matrix to be singular:

```text
det M[X]=0 for every |X|=45.
```

Equivalently, every such `S[X]` must have eigenvalue `-4`.  Therefore a
concrete sufficient obstruction is:

> Force 45 triangle indices whose internal absolute signed degree is at most
> three.

Then `4I+S[X]` is strictly diagonally dominant and positive definite,
contradicting rank 44.

No such set is constructed here.  Obtaining it, or an analogous
incidence-forced principal block with least `S` eigenvalue greater than
`-4`, is the cleanest continuation exposed by this lane.

## Boundary

The exact new consequences are the Smith form (1), the orthogonal
reformulation (2), and the sharpened principal-minor target.  The endpoint is
not excluded, no smaller upper bound is established, and no construction is
claimed.  The retained controls exist only in scalar or local relaxations.
Independent verification is required before promoting even these scoped
derivations.
