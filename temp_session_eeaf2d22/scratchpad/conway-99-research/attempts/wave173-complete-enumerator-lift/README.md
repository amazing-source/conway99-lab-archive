# Wave 173: complete-enumerator lift obstruction

Status: `VERIFIED_WITH_SCOPE` by two independent exact reconstructions.

Wave 54 exhibited one exact ordinary weight enumerator for the conditional
centered ternary `[231,11]` code.  Waves 39/171 fix the complete composition
of its 231 distinguished weight-198 scalar pairs, and Wave 172 supplies
information that the ordinary enumerator forgets: every weight-three dual
word has equal nonzero coefficients, so the two mixed symbol compositions
are absent.

Those combined facts are incompatible.  The contradiction uses only the
degree-two and degree-three complete MacWilliams moments.

For a nonzero scalar pair `{c,-c}`, let

```text
w = number of nonzero coordinates,
d = number of 1s minus number of 2s,
x = 231-3*w/2.
```

Its paired contributions to the relevant complete transform coefficients are

```text
K20 = x^2-x-(3/4)*d^2,
K30 = x^3/3-x^2+154-(3/4)*(x+1)*d^2.
```

Projectivity (`B20=0`) and the Wave 54 weight distribution force

```text
Q=sum d^2=13,640,319.
```

Wave 54 has exactly 231 scalar pairs of weight 198.  The 231 distinguished
rows exhaust them, with composition `(162,36)`, so they contribute

```text
Q_fixed=3,667,356.
```

The Wave 54 ordinary dual coefficient is `B3=120`.  Wave 172 eliminates the
mixed compositions, hence scalar symmetry forces `B30=B03=60`.  The
degree-three moment then requires

```text
T=sum (x+1)*d^2=-7,617,321/2.
```

After subtracting the fixed weight-198 rows,

```text
Q_remaining=9,972,963,
T_remaining=469,138,959/2.
```

The sole weight-18 scalar pair can contribute at most `d^2=324`, with
coefficient `x+1=205`.  Every other remaining Wave 54 weight has
`x+1<=16`.  Therefore

```text
T_remaining
 <=205*324+16*(9,972,963-324)
 =159,628,644,
```

but the required value is `469,138,959/2`, larger by
`149,881,671/2`.

Thus the Wave 54 ordinary formal enumerator has no complete-enumerator lift
compatible with Wave 172.  This refutes that hostile control, not the
endpoint: Wave 54 did not prove its ordinary enumerator was unique.
Conway-99 remains `UNKNOWN`.

A separate six-cell exact rational control shows that the unrestricted
degree-three marked moment system still survives when the ordinary weight
distribution is allowed to change, even with projectivity and all 231
distinguished `(162,36)` scalar pairs retained.  The obstruction is therefore
specific to Wave 54's distribution; degree three alone has not excluded the
endpoint.
