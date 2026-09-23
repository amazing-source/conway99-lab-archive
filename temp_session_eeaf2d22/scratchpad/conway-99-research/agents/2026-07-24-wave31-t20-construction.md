# Wave 31 construction: exact T20 frame boundary

```yaml
role: construction
date_utc: 2026-07-24T06:50:20Z
git_commit: 31bc516a581decb6394bf5e780f07fb05d567274
claim_label: CANDIDATE
scope: >-
  Complete exact norm-four shell and line-pair geometry for the displayed
  Wave 30 T20 Gram; exact formulation of the 105-row second-moment,
  orientation, row-sum, alphabet, Q, B, and A4 gates; an exact rational
  relaxation witness; and a complete radius-two exchange search around one
  named integral near-frame. No unrestricted frame, obstruction, coupled
  endpoint, graph, n3=708 result, Conway-99 result, or novelty claim.
inputs:
  attempts/wave30-h729-construction/exact-results.json: 0d3723ba4c185dc7865858d16bfc6ada99fd87b4e21da616ef1b1d1ad6b67e11
  attempts/wave30-general-h729/exact-results.json: cb0a58195506a51ca6a39aaab197a3592344f7aef8b5b0c2af51770c7069ad6c
  verification/wave24-n3-708-index/independent-results.json: 726807402388c02909171a689f3a7fe2d8d1b74307c24e322ae013d0a9cd486a
  verification/wave28-simultaneous-neighbor/independent_check.py: 2c8021769d47faebbcd544b364649a2cb93c066a369f76f725cffab1588982db
method: >-
  Complete reverse-LDL enumeration through norm four; canonical antipodal
  line reduction without an automorphism quotient; complete exact pair-Gram
  scan; fraction-free Bareiss reconstruction of a rational box-relaxation
  witness; exact GF(2) rank; and a complete one/two-exchange scan using a
  sound modulo-2^64 linear fingerprint followed by entrywise collision checks.
command: |-
  cd attempts/wave31-t20-frame
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
outputs:
  attempts/wave31-t20-frame/exact_check.py: 81acefd270caa81900cb319ca0cb9db68d952f80ce3511edee1f23386c982f8e
  attempts/wave31-t20-frame/test_exact_check.py: 0c36af2f7cee4797b95c1d82b175274ed02f9674599181220900509777b4a365
  attempts/wave31-t20-frame/solver_scout.py: d362197857cbeddc446bedd7cb04945aff598783fbe2421b86a013212e967144
  attempts/wave31-t20-frame/exact-results.json: d2592a71e8600a894aa7d87e6ed1c8230010b919488b10f9854710bb77944152
  attempts/wave31-t20-frame/input-freeze.sha256: 2931d0c8de6e7000112b39aa72232338c5bf14cff54033452bede0842ef92086
  attempts/wave31-t20-frame/failure-ledger.md: 9c4ad5eb4cc9cd9234c49514a207304e6861799bfd308e2a34e03a629fcf4232
limitations:
  - The unrestricted Boolean second-moment problem remains open in this lane.
  - The complete negative search covers only a named radius-two exchange neighbourhood.
  - Optional MIP/SAT timeouts are telemetry and never nonexistence evidence.
  - No orientation is tested after the restricted second-moment nonhit.
  - No Q_A, B_A, A4_A, complement frame, graph lift, or target object is supplied.
  - A fresh independent verifier is required before any promotion.
```

## Result and status wall

This lane did not find an exact T20 frame and did not exclude one.  Its
publication-safe result is a sharper, fully reproducible boundary:

```text
complete T20 norm-four shell:                  CANDIDATE EXACT ENUMERATION
continuous second-moment relaxation:           CANDIDATE EXACT WITNESS
cap-one-coordinate restricted line domain:     CANDIDATE EXCLUSION
named radius-two near-frame neighbourhood:      CANDIDATE EXCLUSION
unrestricted Boolean second moment:             UNKNOWN
oriented zero-sum alphabet frame:               UNKNOWN
Q_A / B_A / A4_A package:                       UNKNOWN
coupled T20 plus U24 endpoint:                   UNKNOWN
n3=708, Conway-99, and novelty:                  UNKNOWN
```

The machine-readable result contains every canonical line, every rational
relaxation weight, the complete near-frame residual, all restrictions, and
the exact finite-search telemetry.

## 1. Complete short-vector alphabet

For the displayed Wave 30 Gram matrix `T20`, exact reverse-LDL enumeration
again gives

```text
norm-four vectors:      5076
antipodal lines:        2538
canonical-line hash:    25af9df21492a5b9022c1888424f4892e0e1cb56d82adee73b49197a536f569e
```

A canonical line is represented by the orientation whose first nonzero
coordinate is positive.  This convention names lines; it does not restrict
the later sign choice and assumes no automorphism.

All `2538` lines are pairwise distinct modulo two and also pairwise distinct
modulo three.  Their maximum absolute coordinate distribution is

| maximum coordinate | lines |
|---:|---:|
| 1 | 1196 |
| 2 | 1019 |
| 3 | 278 |
| 4 | 36 |
| 5 | 9 |

The complete unordered line-pair scan gives

| canonical inner product | pairs |
|---:|---:|
| `-2` | 80883 |
| `-1` | 671126 |
| `0` | 1382670 |
| `+1` | 923008 |
| `+2` | 161766 |

There are no distinct-line inner products of absolute value three or four.
Consequently the endpoint alphabet has a particularly clean exact form:

- a canonical `+2` pair must receive opposite orientation signs;
- a canonical `-2` pair must receive equal orientation signs;
- `0,+/-1` pairs impose no orientation restriction.

The absolute-two graph has `242649` edges.  Its full degree distribution is

```text
degree 160:  108 lines
degree 178:  840 lines
degree 196: 1242 lines
degree 214:  330 lines
degree 232:   15 lines
degree 322:    3 lines.
```

This enumerates the complete allowed T20 short-vector input.  It does not
select a frame.

## 2. Exact 105-row hierarchy

Let `v_l` be the canonical lines and let `z_l` be selection variables.  The
first gate is

```text
z_l in {0,1},
sum_l z_l=105,
sum_l z_l v_l v_l^T = G20 = 21 T20^(-1).       (1)
```

There are `2538` Boolean variables and `210` upper-triangular equations.
Modulo two, the moment equations plus odd row count have rank `210`, one
dependency, and no contradiction.

For signs `epsilon_l in {+1,-1}`, the next gates are

```text
sum_l z_l epsilon_l v_l=0,                     (2)
epsilon_l epsilon_m <v_l,v_m> in {0,1,-1,-2}. (3)
```

Only after (1)--(3) may one define the actual row matrix `X_A` and test

```text
M_A=X_A T20 X_A^T,
W_A=M_A o M_A,
Q_A=X_A^T W_A X_A,
B_A=T20 Q_A=I_20+2C_A.                         (4)
```

The surviving endpoint requires

```text
Q_A even integral positive definite,  det(Q_A)=5,
tr(B_A)=36,                        det(B_A)=3645.
```

No arbitrary determinant-five form may replace the Schur definition in (4).

## 3. Exact rational relaxation witness

The continuous box relaxation of (1),

```text
0<=z_l<=1,
```

is exactly feasible.  A basic witness uses `33` unit weights and `210`
strictly fractional weights.  The checker reconstructs those weights by
fraction-free elimination and verifies all `210` moment entries and the
weight sum using `Fraction`.

Its weight-certificate hash is

```text
2e7f5d482685db1c98f99fe239021f87e3f7c27f0506d92611e935a0617af161.
```

Thus a continuous Farkas separator cannot obstruct this line formulation.
The weights are not Boolean, so this is not a frame.

As a small complete hostile restriction, if every selected line is required
to have maximum absolute coordinate at most one, coordinate `1` has moment at
most `105`, while `(G20)[1,1]=266`.  That restricted domain is excluded.  It
says nothing about the remaining `1342` lines.

## 4. Complete radius-two exchange search

The retained support `W31-T20-NEAR-105-001` consists of `105` distinct
canonical lines.  It is explicitly not a solution:

```text
Frobenius moment-residual score:   121
nonzero upper-triangular entries:   63
maximum absolute residual entry:     2.
```

The checker completely scans:

```text
105 one-line removals against 2433 additions,
5460 two-line removals against 2958528 addition pairs.
```

It finds no exact repair.  The scan uses a linear fingerprint modulo `2^64`;
exact vector equality necessarily gives fingerprint equality, and every
fingerprint collision is checked entrywise.  Therefore hash collisions can
only add work, not hide a repair.

The exact conclusion is only

```text
no second-moment selection lies within two exchanges of
W31-T20-NEAR-105-001.
```

Selections three or more exchanges away and all other initial supports remain
unsearched by this certificate.

## 5. Forced row data if a frame exists

For a T20 row, all `126` cross-block entries are zero.  If `c_i` denotes its
number of internal `-2` entries, the full endpoint row equations become

```text
internal +1:     32-c_i,
internal -1:     36-3c_i,
internal -2:     c_i,
internal zero:   36+3c_i,
0<=c_i<=12.
```

The T20 block trace forces

```text
sum_(i in A)c_i=1044,
```

and hence the directed internal totals

```text
+1: 2316,   -1: 648,   -2: 1044,   0: 6912.
```

In actual-graph notation `q_i=12-c_i`,

```text
sum_(i in A)q_i=216.
```

These are necessary counts, not a candidate matrix.

## 6. Exact complement coupling

The Wave 30 survivor forces `B_U=I_24`, hence `Q_U=U^-1`.  With

```text
A4_U=M_U (M_U o M_U) M_U,
M_U=X_U U X_U^T,
Q_U=X_U^T (M_U o M_U) X_U,
```

direct substitution gives

```text
A4_U=M_U.                                      (5)
```

Every complement diagonal is therefore four.  At `n3=708`, the inherited
global diagonal budget has `84` excess units, so all `84` lie on the T20
block:

```text
(A4_A)[i,i]=4(1+e_i),  e_i>=0 integer,
sum_i e_i=84,
tr(A4_A)=756.
```

This is a genuine necessary coupling beyond the bare second-moment frame.
It does not require choosing a particular rank-24 unimodular Gram matrix.

At the matrix-only level, the complement tensor calculation still permits

```text
c in {9,10,11},
n_9=n_11+4,
n_10=122-2n_11.
```

If the separately proved actual-graph gap `q=0 or q>=2` is imposed, then
`q=1`, equivalently `c=11`, is forbidden and the complement profile becomes

```text
n_9=4, n_10=122, n_11=0.
```

That graph-only sharpening was not imposed on the narrower matrix search.

## 7. Bounded solver telemetry

Full Boolean second-moment scouts in HiGHS, CP-SAT, CP-SAT with explicit
mod-two XORs, and SCIP all reached their `40`--`45` second limits without an
incumbent or a proof.  The full signed zero-sum/alphabet CP-SAT model likewise
returned `UNKNOWN`.  Exact versions, seeds, domains, commands, and outputs
are retained in `failure-ledger.md` and `solver_scout.py`.

These results are noncertifying.  The strongest justified conclusion remains:

```text
the continuous relaxation is nonempty;
one named radius-two integer neighbourhood is empty;
the unrestricted T20 frame problem is UNKNOWN.
```
