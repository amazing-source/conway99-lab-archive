# Wave 82 verification report

Claim label: `VERIFIED`.

## Verdict

The discovery derivation is correct as stated. The integral-orthogonal model
is bidirectionally equivalent to a Conway graph, conditional on all listed
entry, symmetry, row-sum, and square conditions. The complete conditional
Smith form is also correct. No correction is required.

This is an exact reformulation, not a solution: all eight imported rank rows
survive, no `T` is constructed, and Conway-99 remains `UNKNOWN`.

## Exact equivalence

Forward, the verified Seidel equations

```text
S^2=49(I+J),  S1=-70 1,  SJ=JS=-70J
```

give

```text
(9S+7J)^2
 = 81*49(I+J) + 63(SJ+JS) + 49*99J
 = 3969I.
```

The coefficient of `J` is exactly `3969-8820+4851=0`, and
`T1=(-630+693)1=63 1`. The entry values are independently recovered as
`7`, `16`, and `-2`.

Conversely, the entry map

```text
A=(T+2J-9I)/18
```

is exactly binary, hollow, and symmetric. The row sum is
`(63+198-9)/18=14`. Hence `AJ=JA=14J`, and direct expansion gives

```text
T^2-3969I = 324(A^2+A-12I-2J).
```

Thus `T^2=3969I` is exactly the SRG identity
`A^2=12I-A+2J`. There is no relaxation in either direction.

Because `T` is symmetric with `T^2=63^2 I`, its eigenvalues are `+63` and
`-63`. Its trace is `99*7=11*63`, forcing multiplicities 55 and 44.
Consequently `det(T)=63^99`.

## 3-primary audit

Let the nondecreasing 3-adic Smith exponents be
`e_1,...,e_99`.

For an invertible matrix satisfying `T^2=cI`, the Smith exponents of
`T^{-1}` are `-e_99,...,-e_1`, while `T=cT^{-1}`. Therefore

```text
e_i+e_(100-i)=v_3(c)=4.
```

Also `T=7J (mod 9)`. Since the nonzero all-ones matrix has rank one over
`F_3`, exactly one exponent is zero. Every 2-by-2 minor is zero modulo 9,
so `e_1+e_2>=2`; with `e_1=0`, this gives `e_2>=2`. Reciprocity gives
`e_98<=2`. Monotonicity then forces

```text
0^1, 2^97, 4^1.
```

The hostile profile `0^1,2^96,3^2` has the same factor count, determinant
valuation, mod-3 rank, and 2-minor floor, but fails reciprocal pairing. This
confirms that determinant and modular rank alone do not prove the result.

## 7-primary audit

The exact relation `SJ=-70J` gives, over `Z_7`,

```text
T=S(9I-J/10).
```

The right factor has eigenvalue `9` on the 98-dimensional all-one
orthogonal complement and `-9/10` on the all-one line. Its determinant is
`-9^99/10`, a 7-adic unit. It therefore lies in `GL_99(Z_7)`, so right
multiplication preserves every 7-primary Smith exponent. Thus `T` and `S`
have identical 7-primary data:

```text
0^r, 1^(99-2r), 2^r.
```

## Global invariant factors

No other prime occurs because `det(T)=63^99`. Aligning the nondecreasing
3-primary and 7-primary exponents gives

```text
1,
9^(r-1),
63^(99-2r),
441^(r-1),
3969.
```

For each of the eight surviving values of `r`, the independent checker
verifies:

- exactly 99 invariant factors;
- successive divisibility;
- product `63^99`;
- mod-3 rank 1 and mod-7 rank `r`;
- reciprocal products `d_i*d_(100-i)=3969`.

All eight profiles survive.

## Hostile controls

The verifier rejects:

1. the 14-regular circulant graph with offsets `+/-1,...,+/-7`, whose
   associated `T` has the exact alphabet, row sum, congruence
   `T=7J (mod 9)`, and mod-3 rank one but fails `T^2=3969I`;
2. `63I`, which is symmetric, has row sum 63, and squares to `3969I` but
   violates the required entry alphabet;
3. the all-nonedge alphabet matrix, which has diagonal 7 but the wrong row
   sum;
4. a row-sum-preserving asymmetric alphabet mutation;
5. the nonreciprocal 3-primary profile above;
6. a reversed alignment of the 3- and 7-primary parts, which retains the
   determinant but fails the invariant-factor divisibility chain.

## Boundary

- The imported Wave 51 7-primary profile is a prerequisite.
- An abstract Smith profile is necessary, not sufficient, for an integral
  matrix with the prescribed entries.
- No automorphism or endpoint assumption is introduced.
- No candidate matrix or graph is produced.
- Conway-99: `UNKNOWN`.
- Novelty: `UNKNOWN`.
