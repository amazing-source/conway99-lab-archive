# Wave 36 modular-reflection and finite-field rank attack

```yaml
role: proof_b
date_utc: 2026-07-26T22:38:58Z
git_commit: 697cc02bcbe16b69aaf08822298e03c66329c64c
claim_label: DERIVED
scope: >
  Conditional n3=4158 Smith-form, characteristic-three projective,
  characteristic-seven symmetric-cube, and lattice-index consequences of
  the verified Wave 35 integral reflection.
inputs:
  attempts/wave35-n3-upper-spectral/exact-results.json: ca1df07bede11642fb1639a2ae554c1a31ce9a58424d5b3e5031c90ad550a194
  verification/wave35-n3-upper-spectral/independent-results.json: c704d8fce8f1d5975204b9a06ada0098c66fbdb9e0de8016a1ff89d86e691305
  verification/wave35-n3-upper-spectral/run-report.yaml: 40ded0143abe9b0edcec1b87146621dd6ee0fae3483d3d522fec0c83417d6c95
  verification/wave23-index-pranks/2026-07-23T192952Z-audit.md: bfd02ebc39515e27e9e2c79d8e286905086f5747a02a310036ce27dd29ff3116
  verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md: 958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8
method: >
  Reciprocal Smith normal form from C^2=441I; finite-field symmetric Gram
  factorization; exact ternary quadratic-space point counts; a
  characteristic-seven symmetric-cube diagonal isolator; and the verified
  projector-index parity relation.
command: |
  .\.venv\Scripts\python.exe -B -m unittest -v attempts/wave36-modular-reflection/test_exact_check.py
  .\.venv\Scripts\python.exe -B attempts/wave36-modular-reflection/exact_check.py --output attempts/wave36-modular-reflection/exact-results.json
  .\.venv\Scripts\python.exe -B attempts/wave36-modular-reflection/exact_check.py --verify attempts/wave36-modular-reflection/exact-results.json
outputs:
  attempts/wave36-modular-reflection/exact_check.py: e31b19e0252f4da323ec123b1b0cc70e9e10dd1cdc2278a7858288aae137289c
  attempts/wave36-modular-reflection/test_exact_check.py: 28db660565a301a8132b98b62f326f7677a17704931bb0d89cc40dd34cb8e323
  attempts/wave36-modular-reflection/exact-results.json: 5efcd507565a55fcdc3323448bf123ebec31ddc6eb9506a83258eff3c1468607
  attempts/wave36-modular-reflection/input-freeze.sha256: dfba5ffea76b489e9e653219534fd677a0e2f9b3226aa6fe7a1c99abd7765f9b
  attempts/wave36-modular-reflection/failed-routes.md: 41b0cd7295b9ce82d97eb6892349d87e6e33bae81313ae37ed1f9d7f76215038
limitations:
  - Discovery-side derivation requiring independent adversarial verification.
  - No endpoint matrix, finite-field factor configuration, or graph is constructed.
  - The new modular rank floors remain below the rational rank ceiling 44.
  - No upper-bound improvement or endpoint exclusion is claimed.
  - No literature novelty claim is made.
```

## Result

The prism-free endpoint is not excluded, but its modular reflection is more
rigid than the Wave 35 report recorded.

Put

```text
C=2M-21I.
```

The verified endpoint package gives

```text
C^2=441I,
diag(C)=-13,
C_ij in {0,+2,-2},
(+2,-2,0) row counts = (32,36,162),
rank_Q(M)=44.
```

Write

```text
r3=rank_F3(M)=rank_F3(C),
r7=rank_F7(M)=rank_F7(C).
```

This lane proves the new necessary conditions

```text
r3>=8,
r7>=11,
r3+r7 even.                                      (1)
```

It also determines the complete Smith form of `C` once `(r3,r7)` is
specified.  The resulting 629 rank pairs are exact necessary arithmetic
survivors, not matrices or graphs.  Since all survivors still have
`r3,r7<=44`, (1) does not contradict the endpoint.  The rigorous upper bound
therefore remains

```text
n3<=4158.
```

Conway-99 remains `UNKNOWN`.

## 1. Reciprocal Smith form of the reflection

Let

```text
d1 | d2 | ... | d231
```

be the positive Smith invariant factors of `C`.  From

```text
C=441 C^(-1)
```

and integrality of `C`, every `d_i` divides 441.  If
`C=U diag(d_i) V` is a Smith decomposition, then

```text
441 C^(-1)
 =V^(-1) diag(441/d_i) U^(-1).
```

The Smith factors on the right, placed in divisibility order, are
`441/d_231,...,441/d_1`.  They must equal those of `C`.  Hence

```text
d_i d_(232-i)=441.                              (2)
```

For either `p=3` or `p=7`, let `r_p=rank_Fp(C)`.  Equation (2) forces the
complete `p`-adic exponent profile

```text
v_p(d_i): 0^r_p, 1^(231-2r_p), 2^r_p.           (3)
```

Because invariant-factor valuations are nondecreasing simultaneously, the
full Smith form is fixed by the pair `(r3,r7)`.

If `r3<=r7`, it is

```text
1^r3,
3^(r7-r3),
21^(231-2r7),
147^(r7-r3),
441^r3.                                         (4)
```

If `r7<=r3`, it is

```text
1^r7,
7^(r3-r7),
21^(231-2r3),
63^(r3-r7),
441^r7.                                         (5)
```

The middle invariant factor is always 21, as required by the odd order.
Equations (2)--(5) are restrictions, not an existence theorem.

## 2. Symmetric square-zero factorization over odd fields

The following elementary lemma is used twice.

> If a symmetric matrix `A` over a field of odd characteristic has rank
> `r`, then `A=V H V^T` for a full-column-rank `n`-by-`r` matrix `V` and a
> nondegenerate symmetric `r`-by-`r` matrix `H`.

Choose a basis of the column space of `A` for `V`; symmetry gives the
induced nonsingular coordinate form `H`.  If also `A^2=0`, then

```text
0=V H (V^T V) H V^T
```

and full column rank gives

```text
V^T V=0.                                        (6)
```

The rows `v_i` of `V` therefore have Gram matrix `A` for the `H`-form, while
their ordinary frame operator vanishes.  Only the Gram interpretation is
needed for the rank floors below.

Since `21=0` in characteristics three and seven,

```text
C=2M
```

there, so the ranks of `C` and `M` agree.  Every 45-minor of `M` vanishes
over the integers, giving

```text
r3,r7<=44.                                       (7)
```

## 3. Characteristic three forces rank at least eight

Modulo three,

```text
diag(C)=2,
C_ij in {0,1,2}.
```

In the factorization of Section 2, all 231 row vectors `v_i` therefore have
nonzero norm two.

### 3.1 The projective points are distinct

Suppose first that `v_i=v_j`.  Then rows `i,j` of `C` are congruent modulo
three.  The off-diagonal alphabet `{0,+2,-2}` has distinct residues, while
the diagonal residue equals that of `+2`.  Thus the two integer rows would
differ exactly by

```text
-15(e_i-e_j).
```

Its squared norm is 450.  But distinct rows of `C` are orthogonal and each
has squared norm 441, because `C^2=441I`; their difference must have squared
norm 882.  This is impossible.

If `v_i=-v_j`, the same argument applied to the row sum gives

```text
row_i(C)+row_j(C)=-15(e_i+e_j),
```

again with squared norms 450 and 882.  Thus neither equality nor antipodality
can occur.  Over `F_3`, these are the only nonzero projective scalings, so
the 231 vectors give 231 distinct norm-two projective points.

### 3.2 Exact quadratic-space counts

Every nondegenerate quadratic form over `F_3` is congruent to a diagonal
form

```text
diag(1,...,1,d),  d in {1,2}.
```

The exact checker brute-forces both determinant classes.  The numbers of
norm-two projective points in dimensions one through seven are

| dimension | square determinant | nonsquare determinant |
|---:|---:|---:|
| 1 | 0 | 1 |
| 2 | 2 | 1 |
| 3 | 6 | 3 |
| 4 | 12 | 15 |
| 5 | 36 | 45 |
| 6 | 126 | 117 |
| 7 | 378 | 351 |

Dimensions at most six cannot hold 231 such points, so initially `r3>=7`.

There is one more endpoint datum.  Every row of `C` has 162 zero
off-diagonal entries, so each `v_i` has 162 orthogonal companions among the
other projective points.  If `r3=7`, the orthogonal complement of the
anisotropic vector `v_i` is a nondegenerate six-space.  The table shows that
such a space contains at most 126 norm-two projective points.  Since

```text
162>126,
```

rank seven is impossible.  Therefore

```text
r3>=8.                                          (8)
```

This count is characteristic-three projective geometry only; no
automorphism or restricted graph search is assumed.

## 4. Characteristic seven forces rank at least eleven

Modulo seven, the factor vectors satisfy

```text
(v_i,v_i)=1,
(v_i,v_j) in {0,+2,-2}.
```

Let

```text
w_i=v_i tensor v_i tensor v_i
```

in the third symmetric power of the `r7`-space.  Their Gram matrix is the
entrywise cube `C^(o3)`.  On the three off-diagonal values,

```text
t^3=4t mod 7,
```

while at the diagonal

```text
1=4(1+1) mod 7.
```

Consequently

```text
C^(o3)=4(I+C) mod 7.                             (9)
```

But `C^2=0 mod 7`, so

```text
(I+C)^(-1)=I-C.
```

The matrix in (9) is nonsingular.  Hence all 231 symmetric cubes `w_i` are
linearly independent.  In characteristic seven the third symmetric power
of an `r7`-space has dimension

```text
binom(r7+2,3).
```

Thus

```text
binom(r7+2,3)>=231.
```

The boundary values are

```text
binom(12,3)=220,
binom(13,3)=286,
```

which proves

```text
r7>=11.                                         (10)
```

This diagonal-isolating cubic is the strongest consequence found in the
modular-reflection lane.

## 5. Index parity and the finite survivor census

The independently verified projector-lattice formula is

```text
h=3^(44-r3) 7^(44-r7).                          (11)
```

The same verified package gives `h=1 mod 4`.  Since both 3 and 7 are
`-1 mod 4`, (11) implies

```text
(44-r3)+(44-r7) is even,
r3+r7 is even.                                  (12)
```

Combining (7), (8), (10), and (12) leaves exactly

```text
629
```

rank pairs.  In index language,

```text
v3(h)<=36,
v7(h)<=33.
```

The JSON records every surviving pair and representative Smith shapes.
This is a genuine finite reduction of the modular possibilities, but 629 is
far from an endpoint classification.

## 6. Exact replay and hostile boundaries

The standard-library suite passed:

```text
Ran 11 tests
OK
```

It:

- freezes all five inherited inputs by SHA-256;
- checks the endpoint row norm and the 450-versus-882 proportional-row
  contradiction;
- brute-forces both ternary determinant classes through dimension seven;
- actively confirms that lowering 162 to 126 destroys the `r3>=8` step;
- checks the characteristic-seven cubic on every allowed entry;
- verifies the active dimension boundary `220<231<=286`;
- checks both reciprocal Smith-form cases and the central equality case;
- enumerates all 629 parity-compatible rank pairs; and
- keeps `endpoint_excluded=false` and `target_status=UNKNOWN`.

No floating-point arithmetic or solver exit code is used.

## Boundary and continuation

The new exact conclusion is only

```text
8<=rank_F3(M)<=44,
11<=rank_F7(M)<=44,
rank_F3(M)+rank_F7(M) even,
SNF(C) fixed by those two ranks.
```

No endpoint matrix or finite-field factor configuration is constructed.
Conversely, no complete search proves that any of the 629 modular shapes is
realizable.  The endpoint `n3=4158` survives, the general upper bound does
not improve, and novelty is `UNKNOWN`.

The cleanest continuation exposed here is to transport the Wave 35 rooted
incidence partitions into the finite-field factor spaces.  A contradiction
would follow if those local constraints forced rank at least 45 modulo
three or seven, or forced more norm-two points in one orthogonal complement
than the relevant finite quadratic space contains.
