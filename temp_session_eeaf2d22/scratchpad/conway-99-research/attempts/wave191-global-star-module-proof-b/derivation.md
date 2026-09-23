# Compact global-star module derivation

Work over `F_3`.  Let `B` be point-triangle incidence, `A` point
adjacency, `J` the all-one matrix, and

```text
G=BB^T=A+I.
```

The strongly regular identities give

```text
G^2=G-J,
GJ=JG=J^2=0.
```

Thus `E=G-J` is a symmetric idempotent.  The verified `rank(G)=55`
implies

```text
rank(E)=54,
im(G)=im(E) direct_sum <1>.
```

Put `K=ker(E)`.  It is a nondegenerate 45-space containing the singular
all-one vector.

Let `U=im(B)`.  Since `im(G) subset U`,

```text
U=im(E) direct_sum U_0,
U_0=U intersect K.
```

If `d=dim(U_0)`, then `rank(B)=54+d`.  Every incidence column has sum
three, so `U_0 subset 1^perp`, while `1 in U_0`.

The centered endpoint matrix satisfies

```text
D=B^T A B,
rank(D)=11.
```

The adjacency operator kills `im(E)` and acts as `-I` on `U_0`.
Therefore the standard Gram form on `U_0` has rank 11 and radical
dimension `d-11`.  The marked vector `1` lies in that radical, so `d>=12`.
Nondegeneracy of the 45-space gives

```text
d-11<=45-d,
d<=28.
```

Consequently

```text
66<=rank(B)=54+d<=82.
```

The simultaneous star-dependency code is

```text
L=ker(B^T)=U^perp=U_0^perp inside K.
```

Writing `ell=dim(L)=45-d` gives

```text
17<=ell<=33.
```

Moreover

```text
rad(L)=U_0 intersect U_0^perp,
dim rad(L)=d-11=34-ell,
rank of the form on L=2ell-34.
```

Combinatorially, `L` consists of ternary point colorings whose colors sum
to zero on every graph triangle.  Every triangle has type

```text
000, 111, 222, or 012.
```

The checker constructs deterministic abstract orthogonal-space controls for
every `12<=d<=28`.  These prove that the modular rank/radical equations
alone do not exclude the endpoint.  The remaining graph-specific invariant
is the complete/joint weight enumerator of `L`, equivalently the
three/four-point projector trace tensor.
