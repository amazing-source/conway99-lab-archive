# General degree-three rational control

The Wave 54 distribution is refuted, but this is not a universal
degree-three obstruction.  Let `t_(a,b)` denote the rational number of scalar
pairs whose two symbol compositions are `(a,b)` and `(b,a)`.  The following
six values are nonnegative:

```text
t_(0,3)     = 9303802338/154676717
t_(36,162)  = 231
t_(54,162)  = 3304353488/11898209
t_(63,93)   = 61600137243/11898209
t_(72,78)   = 585275248956/11898209
t_(78,81)   = 5202810114945/154676717
```

All other cells are zero.  Direct substitution into the complete
Krawtchouk formulas gives

```text
sum t = (3^11-1)/2,
B10=B01=0,
B20=B11=B02=0,
B21=B12=0,
t_(36,162)=231.
```

The remaining equal-sign degree-three coefficient is positive:

```text
B30=B03=2948614938535/963754929.
```

Thus projectivity and the Wave 172 marked zero remain rationally feasible
through degree three after the ordinary distribution is allowed to change.

This is only an aggregate rational control.  Its cell masses and `B30` are
not all integers, it is not a complete enumerator of a linear code, and it
does not encode the distinguished rows' joint Gram matrix or the 99
point-star dependencies.
