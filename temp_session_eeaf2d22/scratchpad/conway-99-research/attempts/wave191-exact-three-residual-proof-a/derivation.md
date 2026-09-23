# Exact-three exclusion and joint residual amplification

## Frozen inputs

Assume the independently verified conditional prism-free rank-11 endpoint
results through Wave190. In particular:

1. every proper subset of a point-star is independent;
2. an exact-three circuit is one member of a canonical weight-four /
   weight-five companion pair with a common center and the same three
   labels;
3. an exact-two circuit for a given label, when it exists, is the unique
   canonical checkerboard conic;
4. the orbit-closed private-label extraction pool has
   `A=n1+2*p2+p3`, `delta=2*r+3*h-A>=0`, and `r1<=delta`; and
5. the selected, selected-companion, closed-raw, and genuinely new residual
   pools are disjoint.

## Local lemma

For a selected type-three flag `(x,T={y,u,v})` and private label `e=xy`,
normalize the leaf relation as

```text
w_e = 2*(three x-star blocks)+2*(six y-star blocks other than T).
```

Let a raw circuit `D` inside this support have exact multiplicity three.
Its label star contains `xy`, so its center is `x` or `y`.

If centered at `x`, its leaf block is on the `y` side. A weight-five member
needs four `x`-star blocks and cannot fit. A weight-four member uses all
three available `x`-star blocks. Subtracting it from `w_e` gives a nonzero
relation on six proper `y`-star blocks, impossible. Thus `D` is centered at
`y`.

The three source blocks pair the leaf-incidence types `yu,yv,uv`. The
target leaf must be the unique `uv` block `S={x,a,b}`, anticomplete to `y`.
In the target flag `(y,S)`, the owner block `T` has exactly two cross
incidences, so `T in A_y`. The only contained companion member is therefore
`c5=S+B_y`.

The difference `w_e-2*c5` has coefficient two on exactly the canonical four
blocks through the two common neighbors of `xy`. Wave181 proves that this
support has checkerboard kernel `(1,2|2,1)`, not the all-equal word
`(2,2|2,2)`. This contradiction excludes center `y` too. Hence every
type-three raw is exact-one or exact-two; every exact-two case forces the
verified Wave190 checkerboard residual.

## Capacity

Let `t` be the number of type-three raws on exact-one circuits and set
`u=r1-t`. If `Z` is the new residual-assignment incidence, combined old-pool
capacity gives

```text
p3+u <= delta+Z.
```

Close the new residual pool under exact-three companionship and let `Y`
count its circuits. Low circuits have assignment capacity at most two per
circuit, while an exact-three pair has capacity three for two circuits, so
`Z<=2Y`. Therefore

```text
delta+2Y>=p3.                                    (1)
```

The selected type-two owner is already the unique exact-two circuit through
each private label. Both distinct outside raw translates are consequently
non-exact-two. Since type-three raws occupy `t` exact-one slots,

```text
2p2<=u+3h.
```

Eliminating `u` gives

```text
delta+3h+2Y>=2p2+p3.                             (2)
```

The disjoint pools satisfy

```text
Q >= B+r+2*h+Y
  = B+A/2+delta/2+h/2+Y,
B=n1+n2+2*n3.
```

Moreover,

```text
delta/2+h/2+Y
 =(delta+2Y)/3+(delta+3h+2Y)/6
 >=p2/3+p3/2.
```

Thus

```text
Q >= B+A/2+p2/3+p3/2.
```

The coefficient identity is

```text
12*Q
 >= 18*n1+12*n2+24*n3+16*p2+12*p3

  = 9*I+6*(p2-n2)+p2+3*(p3-n3)
 >= 18*C.
```

At `C=4158`, `Q>=3*C/2=6237`.

## Exact null control

The scalar system is arithmetically compatible with

```text
n3=p3=2079, n1=n2=p2=h=0,
r=1040, r1=1, delta=1, Y=1039, Q=6237.
```

No cover, code, graph, or circuit family realizing this row is claimed.
