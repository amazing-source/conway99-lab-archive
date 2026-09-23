# Compact derivation

Let `C=4158`.  Equality in the Wave191 coefficient certificate

```text
12Q>=9I+6(p2-n2)+p2+3(p3-n3)>=18C
```

at `Q=6237` forces

```text
p2=n2=0, p3=n3, n1+2n3=C.
```

Equality in its two pool-capacity rows forces

```text
h=0, delta+2Y=p3, u=0, Z=2Y.
```

A residual from a type-three raw conic is not exact two: the raw conic is
the unique exact-two circuit through that label, and the residual omits
one of its coordinates.  If the orbit-closed new residual pool has `y`
exact-one circuits and `g` exact-three companion pairs, then

```text
Y=y+2g, Z<=y+3g.
```

Since `Z=2Y`, one gets `Y=Z=0`.  Wave190's collision audit then gives

```text
delta=r1=n3, r=2079, r-r1=n1/2.
```

Thus every type-three private raw is exact one, and the type-one private
labels pair two at a time on canonical checkerboard conics.

For a type-one label `e`, equality forces its selected owner to be an
exact axis translate

```text
c_e=q_e-a*sigma_x.
```

The conjugate relation `q_e+a*sigma_x` also has weight eight and profile
`6+2`, but omits the opposite square coordinate.  Minimal circuit
extraction gives a new circuit for the private label `e`, so `n1=0`.

Hence `n3=p3=2079`.  Equality forces every private `3+6` leaf word to be
an exact-one circuit; otherwise circuit elimination inside the leaf word
gives a further circuit for the same private label.

The selected triples have 6237 label incidences.  Their 2079 private
labels occur once, so each of the other 2079 labels occurs exactly twice.
For any such shared label, the corresponding `3+6` leaf relation contains
a short circuit of exact multiplicity at most two by the Wave191 local
lemma.  It is neither a selected exact-three companion nor a private
singleton leaf circuit, and there is no type-one conic pool.  It is an
additional circuit.

Therefore `Q=6237` is impossible and, integrally,

```text
Q>=6238.
```

No topological square-span theorem, graph search, code search, SAT, LP, or
configuration enumeration is used.

