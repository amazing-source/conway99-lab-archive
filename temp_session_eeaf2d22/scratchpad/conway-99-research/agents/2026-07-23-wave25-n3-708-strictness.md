# Wave 25 strictness at the `n3=708` determinant boundary

```yaml
role: proof_b
date_utc: 2026-07-23T22:02:41Z
git_commit: 7103ddfe755a8c3430ef79e9a76e3323f1e00e1d
claim_label: DERIVED
scope: >-
  Conditional strict refinement at n3=708 for a putative
  srg(99,14,1,2): exclusion of the tr(C^2)=8 equality case, the resulting
  trace and determinant bounds, and complete arithmetic h/det(Q)
  enumeration. This does not exclude n3=708 or resolve Conway-99.
inputs:
  verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md: 45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268
  verification/wave23-index-pranks/2026-07-23T192952Z-audit.md: bfd02ebc39515e27e9e2c79d8e286905086f5747a02a310036ce27dd29ff3116
  verification/wave23-endpoint-crosscheck/2026-07-23T200645Z-correction-audit.md: 791d74340c8a84a9993f9a5179c66baf0b2f7e431df5fb7eda2f593195f9bf53
  verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md: 958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8
  verification/wave24-n3-708-index/independent-results.json: 726807402388c02909171a689f3a7fe2d8d1b74307c24e322ae013d0a9cd486a
  verification/wave24-n3-708-index/survivor-certificate.json: a217ec7211128f51e684030a7fe8d3c60ac80935f356ba5193dc34d36d4077a2
  verification/wave24-n3-708-index/theorem-applicability.md: bea67ef5cac84c34ed7ed336ee947532a25a27b05dda653a50693af52cc4b2d1
method: >-
  Equality analysis in the integral self-adjoint endomorphism, an integral
  orthogonal image/kernel split, scaled-dual even forms, the classical
  even-unimodular signature obstruction, trace-square parity, equality
  analysis in the verified Wave 24 logarithmic bound, and complete finite
  3,7-smooth factor enumeration with hostile mutations.
command: |-
  cd attempts/wave25-n3-708-strictness
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
outputs:
  attempts/wave25-n3-708-strictness/exact_check.py: 4da24d38e19583c73724a5bf7ed2ee279ad6b31a8b49cbb367b56ed7f7ca81b8
  attempts/wave25-n3-708-strictness/test_exact_check.py: a431bd0a97e7d670d6cb6fc85c9f81d915a9ce60993b02cf04dec28093a819d4
  attempts/wave25-n3-708-strictness/exact-results.json: 6da9200adf19a5305913178c271ac584e9825aa4f3594fad20717f9418d2b40e
  attempts/wave25-n3-708-strictness/input-freeze.sha256: d7b2f8a24e7e481c920bbbc9a5a3af920b48f7540874760f4c9d218c98ebb203
  attempts/wave25-n3-708-strictness/failed-routes.md: f1b9f4277a2a56b6b1a07332f01a7a7cff897d588e9a01b3f8e6199117c45452
limitations:
  - Discovery-agent derivation only; a fresh independent verifier is required
    before promotion to VERIFIED.
  - The conclusion is conditional on the frozen projector-lattice premises
    for a putative target at n3=708.
  - The same eight h values survive, and 323 arithmetic factor pairs remain.
  - The Wave 24 h=9, det(B)=81 object remains only an abstract
    coordinate-lattice survivor, not a primitive embedding, projector,
    Schur-square realization, or graph.
  - Target existence and literature novelty remain UNKNOWN.
```

## Result and status wall

Under the independently verified Wave 24 premises, equality in the old
trace-square floor is impossible:

```text
tr(C^2) != 8.
```

Because `tr(C^2)` is an even integer, this gives

```text
tr(C^2) >= 10,
tr(B^2) >= 116.
```

Equality in the Wave 24 logarithmic determinant bound would force the same
excluded case.  Therefore

```text
det(B) < 6561.
```

The direct congruence `det(B)=1 mod 4` lowers the integer cap to `6557`.
Using the full factorization

```text
det(B)=h det(Q)
```

and the separate congruences for `h` and `det(Q)` gives the sharper complete
arithmetic cap

```text
det(B) <= 6525=9*725.
```

This is not an endpoint exclusion.  The eight Wave 24 index values all
remain:

```text
h in {9,21,49,81,189,441,729,1029}.
```

The verified abstract `h=9`, `det(Q)=9`, `det(B)=81` survivor has
`tr(C^2)=32`, so it passes every new bound.

The publication-safe discovery status is:

```text
strict conditional refinement: DERIVED
n3=708 exclusion:              NOT OBTAINED
Conway-99 existence:           UNKNOWN
novelty:                       UNKNOWN
```

## 1. Frozen setup and notation

Let `L` be the rank-44 primitive projector lattice, and choose an integral
basis with Gram matrix `G`.  The frozen Wave 21--24 audits give an integral
positive-definite endomorphism `B`, self-adjoint for `G`, with

```text
B=I+2C,
tr(B)=60,
tr(C)=8.
```

They also give

```text
21L* subset L,
Q=GB/21,
Q even, integral, and positive definite,
det(B)=h det(Q),
h=3^a 7^b,
h=1 mod 4,
h!=1,
det(Q)=1 mod 4,
det(Q)>=5.
```

The Wave 24 logarithmic argument proves

```text
det(B)<=3^8=6561.                            (1)
```

The equality analysis below uses no assumed graph, modular rank, or lattice
classification beyond these frozen facts.

## 2. The equality case makes `C` an integral idempotent

Let `r=rank(C)` and let `mu_1,...,mu_r` be its nonzero eigenvalues.  Positive
form self-adjointness makes them real and makes `C` diagonalizable.  The
integral characteristic polynomial gives a nonzero integral
pseudodeterminant, so the verified Wave 24 estimates are

```text
tr(C^2)>=r,
tr(C^2)>=64/r.                               (2)
```

For `1<=r<=44`, the unique way the combined lower bound in (2) can equal
eight is

```text
r=8.
```

If `tr(C^2)=8`, Cauchy is also an equality:

```text
(sum_i mu_i)^2
  =8^2
  =8 sum_i mu_i^2.
```

Thus all eight nonzero eigenvalues are equal.  Their sum is eight, so each is
one.  The remaining 36 eigenvalues are zero.  Since `C` is diagonalizable,

```text
C^2=C,
rank(im C)=8,
rank(ker C)=36.                              (3)
```

The integrality of `C` is crucial.  For every `x in L`,

```text
x=Cx+(I-C)x
```

is a decomposition into lattice vectors in `im(C)` and `ker(C)`.
The intersection is zero, hence

```text
L=im(C) direct_sum ker(C)                    (4)
```

as an integral direct sum.  Self-adjointness gives orthogonality:

```text
<Cu,y>=<u,Cy>=0
```

for `y in ker(C)`.  Therefore (4) is an integral orthogonal split.

## 3. The scaled-dual form `S` is even

Define

```text
S=21G^-1.                                    (5)
```

This step needs both integrality and evenness.

If `X` is the chosen basis matrix for `L`, then `XG^-1` is the dual basis.
The inclusion `21L* subset L` says exactly that every column of
`21G^-1` is integral, so `S` is integral.  It is symmetric and positive
definite because `G` is.

For the `i`-th vector in the 21-scaled dual basis, its squared norm is

```text
||21 X G^-1 e_i||^2
  =441 (G^-1)_ii
  =21 S_ii.                                  (6)
```

That vector lies in the even lattice `L`, so (6) is even.  Since 21 is odd,
`S_ii` is even.  Hence

```text
S is an even integral positive-definite form. (7)
```

The product identity is

```text
S Q
 =21G^-1 (GB/21)
 =B.                                         (8)
```

It is important that (8) is `SQ=B`, not `SQ=I` globally.

## 4. Equality would create an impossible rank-36 kernel form

Choose integral bases of the two summands in (4).  In the combined basis,
orthogonality and (3) give block matrices

```text
G = G_1 direct_sum G_0,
C = I_8 direct_sum 0_36,
B = 3I_8 direct_sum I_36.
```

Consequently `S=21G^-1` is block diagonal.  So is
`Q=GB/21`.  Both restricted blocks retain integrality, evenness, and
positive definiteness.  Restricting (8) to `K=ker(C)` gives

```text
S_K Q_K=I_36.                                (9)
```

The positive integral determinants in (9) multiply to one.  Thus

```text
det(S_K)=det(Q_K)=1.
```

In particular, `S_K` is an even positive-definite unimodular integral form
of rank 36.  Equivalently, the same is true of `Q_K`; the proof has a
redundant even-form route here.

The classical van der Blij signature theorem says that the signature of an
even unimodular lattice is divisible by eight.  A positive-definite
rank-36 form has signature

```text
36=4 mod 8,
```

which is impossible.  This contradicts the equality assumption.  Therefore

```text
tr(C^2)>8.                                   (10)
```

## 5. Parity sharpens the trace floor to ten

For every integral matrix `C`,

```text
tr(C^2)
 =sum_i C_ii^2 + 2 sum_{i<j} C_ij C_ji
 =tr(C) mod 2.                               (11)
```

Here `tr(C)=8`, so `tr(C^2)` is even.  Combining its integrality, (10), and
(11) gives

```text
tr(C^2)>=10.                                 (12)
```

Since `B=I+2C`,

```text
tr(B^2)
 =44+4tr(C)+4tr(C^2)
 >=44+32+40
 =116.                                       (13)
```

The checker exhausts all 16 two-by-two residue matrices as a hostile check
of (11); the displayed algebra proves it in every rank.

## 6. The Wave 24 determinant inequality is strict

Wave 24 proved for every nonzero eigenvalue `mu` of `C`

```text
log(1+2mu)
 <=mu log(3)-(log(3)-2/3)log|mu|.            (14)
```

The inequality is strict on `-1/2<mu<0` and has equality on the positive
domain only at `mu=1`.  Summing (14), using `tr(C)=8`, and using the nonzero
integral pseudodeterminant gives (1).

If equality held in (1), every step in that chain would be equality.  The
nonzero pseudodeterminant would have absolute value one, no negative
eigenvalue could occur, and every nonzero eigenvalue would equal one.
Their sum would force exactly eight such eigenvalues.  That is precisely the
idempotent case excluded in Sections 2--4.  Hence

```text
det(B)<6561.                                 (15)
```

The determinant expansion for `B=I+2C` gives

```text
det(B) congruent 1+2tr(C) congruent 1 (mod 4). (16)
```

The largest integer satisfying (15)--(16) is `6557`.  The next section uses
the stronger factor data.

## 7. Complete factor enumeration and the cap `6525`

The finite enumeration imposes all of

```text
det(B)=h det(Q)<6561,
h=3^a 7^b,
h=1 mod 4,
h!=1,
det(Q)=1 mod 4,
det(Q)>=5.
```

It finds exactly 323 `(h,det(Q))` pairs:

| `h` | `(a,b)` | `(rank_F3(M),rank_F7(M))` | exact `det(Q)` progression | count | largest `det(B)` |
|---:|---:|---:|---:|---:|---:|
| 9 | `(2,0)` | `(42,44)` | `5,9,...,725` | 181 | 6525 |
| 21 | `(1,1)` | `(43,43)` | `5,9,...,309` | 77 | 6489 |
| 49 | `(0,2)` | `(44,42)` | `5,9,...,133` | 33 | 6517 |
| 81 | `(4,0)` | `(40,44)` | `5,9,...,77` | 19 | 6237 |
| 189 | `(3,1)` | `(41,43)` | `5,9,...,33` | 8 | 6237 |
| 441 | `(2,2)` | `(42,42)` | `5,9,13` | 3 | 5733 |
| 729 | `(6,0)` | `(38,44)` | `5` | 1 | 3645 |
| 1029 | `(1,3)` | `(43,41)` | `5` | 1 | 5145 |

Every displayed progression has common difference four.  The JSON artifact
lists every value explicitly, and the tests compare the program output with
a separately written brute-force set comprehension.  The largest product is

```text
h=9,
det(Q)=725,
det(B)=6525.                                 (17)
```

Thus the best bound from this exact package is (17).  It does not remove any
of the eight values of `h`.

## 8. Hostile controls

The 21-test suite includes the following premise attacks.

### 8.1 False global inverse

The full frozen Wave 24 matrices satisfy

```text
SQ=B!=I.
```

They reject `S=Q^-1` globally.  The inverse relation used in the proof is
only the kernel restriction (9).

### 8.2 Omitted evenness

The explicit diagonal package

```text
G=21I,
S=I,
Q=B=diag(3^8,1^36)
```

satisfies all three product identities and has `det(B)=6561`, but its forms
are odd.  This hostile relaxation verifies that evenness cannot be omitted.

### 8.3 Nonintegral idempotent

Eight rational rank-one projectors

```text
(1/2)[[1,1],[1,1]]
```

plus 28 zeros give a symmetric idempotent with both traces equal to eight.
Its integral image and kernel sum with index `2^8=256`, not one.  This
rejects an integral-splitting claim without integral `C`.

### 8.4 Rank divisible by eight

Mutating the ambient rank to 40 leaves a rank-32 equality kernel.  The
checker reconstructs the even positive-definite unimodular witness `E8^4`,
so no signature contradiction occurs.  The actual rank 36 is active.

### 8.5 Congruence and strict-cap omissions

The exact maxima under weakened premises are:

```text
valid conditions:                         6525
omit det(Q)=1 mod 4, retain oddness:      6543
omit all det(Q) parity/congruence:        6552
omit h=1 mod 4:                           6559
wrongly permit det(B)=6561:               6561
```

The last mutation restores exactly

```text
(h,det(Q))=(9,729),(81,81),(729,9).
```

These controls catch a non-strict cap or a dropped congruence.

## 9. The Wave 24 survivor still blocks endpoint promotion

The frozen, independently verified abstract package has

```text
h=9,
det(Q)=9,
det(B)=81,
tr(B)=60,
tr(C)=8,
tr(C^2)=32.
```

It satisfies (12), (13), (15), and (17).  The matrix certificate also
supplies the hostile global product `SQ=B!=I`.

Its boundary is unchanged.  It is not shown to be:

- a primitive sublattice of `Z^231`;
- generated by the required 231 projector columns;
- induced by the Schur square `W=M o M`; or
- realized by an `srg(99,14,1,2)`.

Therefore this wave proves a strict conditional refinement only.

## 10. Exact replay and next obstruction

The standard-library-only replay passed:

```text
Ran 21 tests
OK
```

It checks all seven frozen input hashes, all 44 possible nonzero ranks, the
integral equality split, the rank-36 signature gate, trace-square parity,
all 323 factor pairs, all hostile mutations, the complete frozen Wave 24
survivor matrices needed for the global-product control, and deterministic
LF-only JSON.

The next obstruction remains structural:

> Use the primitive 231-column projector origin, exact row data, or
> `Q=X^T(M o M)X` to reject all surviving arithmetic/lattice packages, or
> construct a complete target certificate.

Until such a bridge is derived and independently verified, `n3=708` and
Conway-99 remain open in this repository.
