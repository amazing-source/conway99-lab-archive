# Derivation

## 1. Scalar-pair coordinates

Let `W` be the conditional centered ternary `[231,11]` code.  Since
`1` belongs to `W^perp` and every word of the self-orthogonal code has weight
divisible by three, both nonzero symbol counts of every word are divisible
by three.

Pair every nonzero word `c` with `-c`.  If `c` has `a` symbols equal to one
and `b` symbols equal to two, put

```text
w=a+b,
d=a-b,
x=231-3*w/2.
```

The scalar mate exchanges `a` and `b`, so only `d^2` occurs in a paired
complete MacWilliams coefficient.

## 2. Degree-two and degree-three coefficients

Let `omega` be a primitive cube root of unity and

```text
S=(231-w)+a*omega+b*omega^2.
```

Then

```text
Re(S)=x,
Im(S)^2=3*d^2/4.
```

Newton's identities for elementary symmetric functions give the paired
coefficient with two dual symbols equal to one:

```text
K20
 =e2(S coordinates)+conjugate
 =x^2-x-(3/4)*d^2.                                (1)
```

Similarly the paired coefficient with three dual symbols equal to one is

```text
K30
 =e3(S coordinates)+conjugate
 =x^3/3-x^2+154-(3/4)*(x+1)*d^2.                 (2)
```

The accompanying exact checker independently reconstructs these coefficients
by direct degree-at-most-three expansion in the Eisenstein integer ring for
every allowed composition used below.

## 3. The degree-two forced moment

Wave 54's nonzero ordinary multiplicities, divided by two into scalar pairs,
are

| weight | scalar pairs |
|---:|---:|
| 18 | 1 |
| 144 | 26,658 |
| 153 | 9,899 |
| 159 | 49,248 |
| 162 | 2,536 |
| 198 | 231 |

The zero codeword contributes `binomial(231,2)` to the complete dual
coefficient `B20`.  Projectivity gives `B20=0`.  Substitution in (1) yields

```text
Q=sum d^2=13,640,319.                              (3)
```

All 462 weight-198 words in Wave 54 are exhausted by the 231 distinguished
row words and their negatives.  Their symbol composition is `(162,36)` up
to sign, so `d^2=126^2`.  Hence

```text
Q_fixed=231*126^2=3,667,356,
Q_remaining=9,972,963.                            (4)
```

## 4. The degree-three forced moment

Wave 54 has ordinary dual coefficient `B3=120`.  Wave 172 proves that the
mixed complete coefficients `B21` and `B12` vanish.  Scalar symmetry gives

```text
B30=B03=60.
```

The zero codeword contributes `binomial(231,3)` to `B30`.  Substitution in
(2) gives

```text
T=sum (x+1)*d^2=-7,617,321/2.                     (5)
```

At weight 198, `x+1=-65`, so the fixed rows contribute

```text
T_fixed=-65*3,667,356=-238,378,140,
T_remaining=469,138,959/2.                        (6)
```

## 5. Exact extremal contradiction

For the remaining weights, the coefficient `x+1` is

| weight | `x+1` |
|---:|---:|
| 18 | 205 |
| 144 | 16 |
| 153 | `5/2` |
| 159 | `-13/2` |
| 162 | `-11` |

There is only one weight-18 scalar pair, and `d^2<=18^2=324`.  Every other
coefficient is at most 16.  Since every contribution to `Q` is nonnegative,

```text
T_remaining
 <=205*324+16*(Q_remaining-324)
 =159,628,644.                                    (7)
```

Equations (6)--(7) are incompatible:

```text
469,138,959/2-159,628,644
 =149,881,671/2
 >0.
```

No integrality assumption was used in the last optimization; the
contradiction excludes even a nonnegative rational composition refinement of
the Wave 54 distribution.

## Boundary

This proves that one previously surviving ordinary formal enumerator cannot
be the ordinary shadow of the endpoint code.  It does not prove that Wave
54's ordinary distribution is unique, and therefore does not exclude every
possible complete enumerator or the endpoint itself.
