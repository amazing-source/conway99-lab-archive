# Complete Wave191 equality face and its exclusion

Assume the independently verified conditional Wave191 theorem and suppose
`Q=6237`.

## Equality face

Equality in

```text
12Q>=9I+6(p2-n2)+p2+3(p3-n3)>=18C
```

gives

```text
n2=p2=0,
p3=n3=m,
n1=C-2m.
```

An exact-two type-three raw has a Wave190 residual through the same label.
Wave181 uniqueness prevents this residual from being exact-two. Closing
new exact-three residuals shows `2Z<=3Y`, not merely `Z<=2Y`. Equality in
the Wave191 penalty then forces `Y=0`, and old-pool collision exclusion
forces every type-three raw to be exact-one.

The complete equality family is

```text
n1=C-2m, n3=p3=m,
r=2079, r1=t=delta=m,
n2=p2=h=u=Y=Z=0,
0<=m<=2079.
```

All type-one raw assignments saturate `2079-m` canonical exact-two conics,
two labels per conic. Hence the type-one label set is invariant under the
canonical nonedge involution.

## Endpoint `m=0`

The majority translation of a selected type-one circuit must equal its
canonical conic raw circuit; otherwise relation subtraction forces a third
circuit through its private label. The other nonzero translation along the
same endpoint is a distinct `6+2` weight-eight relation containing neither
known circuit. It therefore forces a new circuit. Contradiction.

## Branch `m>0`

Every selected type-three circuit has exactly one private label and two
nonprivate labels. A leaf relation for a nonprivate label contains a
circuit of multiplicity at most two by the privacy-free Wave191 local
exclusion. It cannot be any equality-face exact-one circuit because those
have private labels, and it cannot be an equality-face exact-two conic
because those label pairs lie entirely in the type-one set. It is new.
Contradiction.

Therefore equality is impossible and, integrally,

```text
Q>=6238.
```
