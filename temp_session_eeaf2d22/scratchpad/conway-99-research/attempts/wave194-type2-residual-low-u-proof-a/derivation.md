# Type-two residual and joint low-target derivation

Use

```text
a1+a2+a3=n1,
b1+b3=2p2,
c1+c2=p3,
r1=a1+b1+c1,
a2+c2<=2r2,
a3+b3<=3h.
```

For an exact-three type-two raw `D_x` inside its `6+2` translated
relation, cancel the unique leaf-side coordinate of `D_x`. The residual is
nonzero on proper subsets of both endpoint stars, crosses the source
label, omits both the raw-pair leaf coordinate and a selected-conic
coordinate, and hence has exact multiplicity one or three. It cannot equal
an exact-one opposite raw: their common support would have weight at most
three. If the opposite raw is exact-three, its center is opposite, so it is
neither equal nor companion. If both raws are exact-three, their two
residuals are distinct: equality in the exact-one case would give support
of size at most two, while exact-three equality or companionship would
again require the opposite unique centers to coincide. Different-label
exact-one collisions are impossible because an exact-one circuit realizes
only one label.

Thus the old raw assignments plus forced residuals demand

```text
a2+a3+2b3+c2
```

label slots. If the genuinely new closed residual pool contains `y`
exact-one circuits and `g` exact-three pairs, then

```text
SR=3h+y+3g-(a2+a3+2b3+c2)>=0.
```

Let `U` be the selected-type-three label union and let `k` be the selected
type-two incidences in `U`. Then

```text
C-|U|<=n1+2n2-k,
|U|<=k+c1+2r2+y+2W.
```

Adding cancels `k` and gives

```text
SL=n1+2n2+c1+2r2+y+2W-C>=0.
```

For

```text
I=2n1+2n2+3n3+p2+p3,
Q0=n1+n2+2n3+r1+r2+2h+y+2g+W,
```

the exact certificate is

```text
Q0-5C/3

 =(2/3)(I-2C)
  +(p2-n2)
  +(2/3)SR
  +(1/3)SL
  +a1/3+b1/6+b3/2+r2/3+W/3.
```

Hence `3Q>=5C`, so `Q>=6930` for `C=4158`.

The complete arithmetic equality face is

```text
h=t,
n3=C/3-t,
n1=a3=3t,
p3=c1=r1=C-3t,
0<=t<=C/3,
all other variables zero.
```

It is a null control, not a construction.
