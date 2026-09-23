# Derivation: an integral orthogonal model

Claim label: `DERIVED` (discovery; independent verification required).

## 1. Exact equivalence

Let

```text
S = 2A - J + I.
```

The imported verified identities are

```text
S^2 = 49(I+J),   S1=-70 1.
```

Set

```text
T = 9S+7J = 18A-2J+9I.                     (1)
```

Because `SJ=JS=-70J` and `J^2=99J`,

```text
T^2
 = 81S^2 + 63(SJ+JS) + 49J^2
 = 3969I + (3969-8820+4851)J
 = 3969I.                                   (2)
```

Also `T1=63 1`.  The entries in (1) are 7 on the diagonal, 16 on an
edge, and -2 on a nonedge.

Conversely, suppose a symmetric order-99 integer matrix has diagonal 7,
off-diagonal alphabet `{16,-2}`, row sum 63, and square `3969I`.  Define

```text
A = (T+2J-9I)/18.                           (3)
```

The entry alphabet makes `A` a symmetric zero-diagonal binary matrix, and
the row sum is 14.  Equivalently define `S=(T-7J)/9`; its entries and (2)
give

```text
S^2=49(I+J),   S1=-70 1.
```

Substituting `S=2A-J+I` recovers

```text
A^2=12I-A+2J.
```

Thus (1)--(3) are an exact equivalence, not a relaxation.

The imported Seidel spectrum gives

```text
spec(T)={+63^55,-63^44},   det(T)=63^99.     (4)
```

## 2. The 3-primary Smith factors

Write the 3-adic Smith exponents in increasing order as
`e_1,...,e_99`.

Since `T^2=3969I` and the 3-adic valuation of 3969 is four, Smith
reciprocity gives

```text
e_i + e_(100-i) = 4.                         (5)
```

Moreover,

```text
T = 9S+7J = 7J (mod 9).
```

Therefore `rank_F3(T)=1`, so exactly one exponent is zero.  Every 2-by-2
minor is divisible by 9; with `e_1=0`, this gives `e_2>=2`.  Applying (5)
at the opposite end gives `e_98<=2`.  Monotonicity forces

```text
3-primary exponents: 0^1,2^97,4^1.           (6)
```

## 3. The 7-primary Smith factors

Over the 7-adic integers, 10 is a unit and

```text
T = S(9I-J/10).                              (7)
```

The second factor acts by 9 on `1-perp` and by `-9/10` on the all-one
line.  Its determinant is therefore a 7-adic unit.  Hence `T` and `S`
have the same 7-primary Smith factors.

For `r=rank_F7(S)`, the imported verified Wave 51 form gives

```text
7-primary exponents: 0^r,1^(99-2r),2^r.      (8)
```

There are no other prime factors by (4).  Aligning the increasing
3-primary and 7-primary factors in (6) and (8) yields

```text
SNF(T) =
diag(1, 9^(r-1), 63^(99-2r), 441^(r-1), 3969).   (9)
```

Every factor divides the next and their product is `63^99`.

## 4. Boundary

Wave 66 leaves eight possible values

```text
r in {28,30,32,34,36,38,40,42}.
```

All eight profiles in (9) pass the divisibility, reciprocity, factor-count,
and determinant checks.  No rank row is deleted.

The new object is a certificate-friendly exact search space: a symmetric
three-valued integral orthogonal matrix with a completely prescribed Smith
profile conditional on `r`.  It is not a construction, nonexistence proof,
or novelty claim.  Conway-99 remains `UNKNOWN`.

