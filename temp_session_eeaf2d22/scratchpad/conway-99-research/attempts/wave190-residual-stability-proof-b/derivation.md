# Compact residual-stability derivation

Use the frozen Wave 189 pools.  Let

```text
A=n_1+2p_2+p_3
```

be the raw extraction assignments.  Write the closed extraction pool as
`r` circuits of exact multiplicity at most two and `h` exact-three companion
pairs, and put

```text
delta=2r+3h-A>=0.
```

If `r_1` low circuits have exact multiplicity one, actual capacity gives
`r_1<=delta`.

Let `a_H` count all raw assignments to exact-three pairs and `q_H` the
type-three raw assignments among them.  At least

```text
k>=p_3-r_1-q_H
```

type-three assignments land on exact-two checkerboard conics.  Subtracting
the conic from its all-two `3+6` leaf relation forces a residual circuit for
each of these distinct private labels.

Within one exact-three orbit, raw and residual assignments share the same
three-label set and are mutually exclusive label by label.  Type-two's two
raw assignments cannot be companion mates.  Thus the pairs absorb residuals
for at most `3h-a_H` labels.

If `Y` counts genuinely new residual circuits, capacity three gives

```text
3Y>=k-(3h-a_H)
   >=p_3-delta-3h,

delta+3h+3Y>=p_3.
```

The disjoint pools give

```text
Q>=N+n_3+r+2h+Y
  =N+n_3+A/2+delta/2+h/2+Y
  >=N+n_3+A/2+p_3/6.
```

Therefore

```text
6Q>=9n_1+6n_2+12n_3+6p_2+4p_3

   =4(2n_1+2n_2+3n_3+p_2+p_3)
    +n_1+2(p_2-n_2)

   >=8C.
```

For `C=4158`,

```text
Q>=4C/3=5544.
```

The integer relaxation row

```text
n_3=1386, p_3=4158, h=1386,
n_1=n_2=p_2=r=delta=Y=0
```

is arithmetically sharp.  It is not asserted to be a cover.
