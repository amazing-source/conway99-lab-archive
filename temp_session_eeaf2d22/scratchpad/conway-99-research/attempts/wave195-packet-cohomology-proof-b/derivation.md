# Compact fixed-center derivation

For a canonical exact-three flag `(x,T)`, Wave180 gives

```text
z_T+2*sum_(S in A_x(T)) z_S=0,
|A_x(T)|=3,
```

on the seven blocks through `x`.  At fixed `x`, the map `T -> A_x(T)` is
injective: equal `A`-sets give a forbidden weight-two relation.  Its image
is intersecting: disjoint `A,A'` plus the leftover star block `L` give

```text
z_T+z_T'+z_L=0,
```

a forbidden weight-three relation.

Let `j_x` be the number of distinct oriented center-leaf labels and `c_x`
the number of flags.  If the family is nontrivial, Hilton--Milner gives
`c_x<=13`, while `j_x<=3c_x`; hence

```text
j_x<=39.
```

If all members contain `S={x,p,q}`, Erdos--Ko--Rado gives `c_x<=15`, and
the common block makes one leaf per flag a `p`-neighbor among the 12
neighbors outside `{x,q}`, and a distinct leaf a `q`-neighbor among the
12 neighbors outside `{x,p}`.  They are distinct because a shared leaf,
together with `x`, would give the edge `pq` two common neighbors.  There
is at most one remaining leaf per flag.  Therefore

```text
j_x<=12+12+c_x<=39.
```

Thus, in both cases,

```text
j_x<=39.
```

Summing over 99 centers gives

```text
J<=3861.                                          (1)
```

The selected type-three label union has size at least
`C-n1-2n2`.  The `a3+b3` old exact-three assignments are distinct oriented
private labels outside that union.  Hence

```text
J>=C-n1-2n2+a3+b3.                               (2)
```

Equations (1)--(2) give

```text
SG=3861-C+n1+2n2-a3-b3>=0.                       (3)
```

With the verified Wave194 slacks,

```text
Q0-(11C-3861)/6
 =2SI/3+4S2/3+SE2/6+2RA/3+SL/3+SG/6
  +a1/6+b3/2+c2/6+W/3.
```

Every term is nonnegative.  At `C=4158`,

```text
(11C-3861)/6=13959/2,
```

so integrality gives `Q>=6980`.
