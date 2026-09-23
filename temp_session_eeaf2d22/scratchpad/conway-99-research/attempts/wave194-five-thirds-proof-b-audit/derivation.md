# Compact audit derivation

Use

```text
a1+a2+a3=n1,
b1+b3=2p2,
c1+c2=p3,
r1=a1+b1+c1.
```

If a type-two raw in a `6+2` parent is exact three, subtract it after
scaling to cancel its unique leaf block.  The residual is nonzero, stays
inside the proper parent, and omits both the raw leaf and the conic
coordinate used by the companion.  It is therefore distinct from the raw,
companion, and selected conic, and exact-two uniqueness makes it exact one
or three.

The two endpoint residuals for the same private label are distinct.  If
exact three they have opposite centers.  If exact one, a common support
would lie in the two-coordinate intersection of the `6+2` and `2+6`
parents, contradicting dual distance four.

Thus

```text
RA=3h+y+3g-(a2+a3+2b3+c2)>=0.
```

For the union `U` of labels on selected type-three circuits, let `k` count
selected type-two incidences in `U`.  Selected type one has no `U` label,
and only `c1` among exact-one raws can cross `U`.  The same `k` is removed
from the outside-`U` cover capacity and added to the low-target collision
capacity:

```text
C-U<=n1+2n2-k,
U<=k+c1+2r2+y+2W,
SL=n1+2n2+c1+2r2+y+2W-C>=0.
```

With the standard slacks and disjoint-pool objective

```text
Q0=n1+n2+2n3+r1+r2+2h+y+2g+W,
```

the exact positive identity is

```text
Q0-5C/3
=2SI/3+S2+2RA/3+SL/3
 +a1/3+b1/6+b3/2+r2/3+W/3.
```

Hence `Q>=6930` for `C=4158`.
