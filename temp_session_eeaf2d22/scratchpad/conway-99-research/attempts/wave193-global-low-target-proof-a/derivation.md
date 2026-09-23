# Global low-target and residual-flow derivation

Split raw assignments as

```text
a1+a2+a3=n1,
b1+b3=2p2,
c1+c2=p3,
r1=a1+b1+c1,
a2+c2<=2r2,
a3+b3<=3h.
```

Wave181 uniqueness eliminates type-two exact-two raws. Wave191 eliminates
type-three exact-three raws.

Every exact-two type-one raw forces an exact-one/exact-three residual:
subtract the conic if it is proper in the majority-translated word; if the
word equals the conic, use the other `6+2` axis word. Wave190 supplies the
same residual for exact-two type-three raws.

Old exact-three raw pairs have unused residual-label capacity
`3h-a3-b3`. Closing the remaining residuals under companionship gives

```text
S_R=3h+(3/2)Y-(a2+a3+b3+c2)>=0.
```

Let `U` be the label union of selected type-three circuits. Then

```text
|U|>=C-(n1+2n2).
```

One privacy-free leaf target per label in `U` is exact-one or exact-two.
Counting selected low, old raw low, the exact-one portion of the new
residual pool, and additional low circuits `W` gives

```text
S_L=2n1+4n2+r1+2r2+Y+2W-C>=0.
```

For

```text
Q0=n1+n2+2n3+r1+r2+2h+Y+W,
```

the exact certificate is

```text
Q0-59C/39

 =(29/39)(I-2C)
  +(23/39)(p2-n2)
  +(3/13)(p3-n3)
  +(38/117)(2r2-a2-c2)
  +(2/117)(3h-a3-b3)
  +(76/117)S_R
  +(1/39)S_L
  +(17/39)(a1+a2)
  +(5/39)a3
  +(4/13)b1
  +(35/117)r2
  +(37/39)W.
```

Thus `117Q>=177C`; for `C=4158`, `Q>=6291`.
