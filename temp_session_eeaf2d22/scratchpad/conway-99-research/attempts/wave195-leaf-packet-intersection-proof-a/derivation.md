# Compact Wave195 derivation

Every selected or raw exact-three companion pair is a canonical flag
`(x,T)`. Its weight-four relation is

```text
z_T+2*sum_(S in A_x(T)) z_S=0,
```

where `A_x(T)` is a three-subset of the seven graph triangles through `x`.
Equal `A`-sets subtract to a forbidden weight-two relation. Disjoint
`A`-sets, together with the full star relation, give a forbidden
weight-three relation. Thus the local `A`-family is simple and
intersecting.

Let `c_x` be its size and `j_x` the number of distinct oriented leaf
labels. If the family is nontrivial, Hilton--Milner gives `c_x<=13`, so

```text
j_x<=3*c_x<=39.
```

If it has a common star block `{x,p,q}`, then `c_x<=15`. The `lambda=1`
geometry gives at most 12 distinct `p`-neighbors and 12 distinct
`q`-neighbors across all leaf triangles; those two vertices are distinct
in each triangle. There is one remaining vertex per flag, so

```text
j_x<=12+12+c_x<=39.
```

Summing over 99 centers, with `J=sum_x j_x`,

```text
J<=3861.
```

The selected-type-three label union has size at least `C-n1-2*n2`.
Raw exact-three assignments are keyed by private labels outside that
union. A type-one source contributes one orientation. The two raw
translates of a type-two source use opposite orientations of its one
undirected private label, while private labels of different selected
sources are distinct. They therefore add `a3+b3` distinct oriented labels.
Hence

```text
J>=C-n1-2*n2+a3+b3,
SG=3861-C+n1+2*n2-a3-b3>=0.
```

With the Wave194 slacks `SI,S2,SE2,RA,SL`,

```text
Q0-(11*C-3861)/6

 =(2/3)*SI+(4/3)*S2+(1/6)*SE2
  +(2/3)*RA+(1/3)*SL+(1/6)*SG
  +a1/6+b3/2+c2/6+W/3.
```

All terms on the right are nonnegative. At `C=4158`,

```text
Q>=Q0>=13959/2=6979.5,
```

so the integral count satisfies `Q>=6980`.
