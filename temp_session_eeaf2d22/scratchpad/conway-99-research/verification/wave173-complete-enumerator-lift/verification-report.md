# Independent verification report

## Verdict

`VERIFIED_WITH_SCOPE`.

## Wave 54 lift obstruction

For a scalar pair of ternary words with weight `w`, symbol difference `d`,
and `x=231-3w/2`, an independent character-generating-function derivation
gives

```text
K20=x^2-x-(3/4)*d^2,
K30=x^3/3-x^2+154-(3/4)*(x+1)*d^2.
```

The zero word contributes `binomial(231,2)` and `binomial(231,3)` once.
Independent ordinary MacWilliams reconstruction confirms Wave 54's
`B2=0` and `B3=120`.

Projectivity therefore forces

```text
Q=sum d^2=13,640,319.
```

Wave 54 has exactly 231 weight-198 scalar pairs.  The Wave 39/171 endpoint
theorem gives their composition `(36,162)` up to sign, so

```text
Q_fixed=3,667,356,
Q_remaining=9,972,963.
```

Wave 172 gives `B21=B12=0`, hence `B30=B03=60`.  The degree-three moment is

```text
T=sum (x+1)*d^2=-7,617,321/2.
```

The fixed rows contribute `-238,378,140`, leaving
`T_remaining=469,138,959/2`.  The sole weight-18 pair has `d^2<=324` and
coefficient 205; every other remaining coefficient is at most 16.  Therefore

```text
T_remaining<=159,628,644,
```

contradicting the required value by `149,881,671/2`.

The contradiction is exact and excludes even a nonnegative rational
composition refinement of the Wave 54 distribution.

## General rational control

The verifier separately substituted the six cells recorded in
`general-rational-control.md` into independently derived paired coefficients
`K10,K20,K11,K21,K30`.  They satisfy exactly

```text
sum t=(3^11-1)/2,
B10=B01=B20=B11=B02=B21=B12=0,
t_(36,162)=231,
B30=B03=2948614938535/963754929>0.
```

This confirms rational feasibility of the unrestricted degree-three marked
moment system.  The cell masses and `B30` are not all integers, so the
control is not a complete enumerator or linear code.

## Scope boundary

- The obstruction uses Wave 54, Wave 39/171's distinguished weight-198
  compositions, and Wave 172 together.
- It applies only to the conditional dimension-eleven, hence `r3=12`,
  Wave 54 distribution.
- Other ordinary distributions remain unclassified.
- The general control verifies only a rational moment relaxation.
- No endpoint exclusion, strict `n3` improvement, graph, or Conway-99
  resolution follows.
