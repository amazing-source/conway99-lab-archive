# Rooted Wagner strategy and exact reductions

Claim label: `DERIVED` for the identities and reductions;
`UNKNOWN` for the four-failure lemma.

## 1. Endpoint arithmetic

At `n3=4158`, Wave 158 gives

```text
37422 + 12*C8 - 4*W8 >= 0.                      (1)
```

Wave 165 gives `C8<=3118`, so the positive part of (1) is at most

```text
37422 + 12*3118 = 74838.
```

If `W8>=18710`, then `4*W8>=74840`, contradicting (1). Thus the exact new
sufficient target is

```text
W8 >= 18710.                                    (2)
```

## 2. The fixed-C4 shell identity

Fix an induced cycle `v0 v1 v2 v3 v0`. Let `U_i` be the ten outside
vertices adjacent only to `v_i` among the anchors, and let `a_i` be the
edge apex adjacent to `v_i,v_(i+1)`.

For `x in U_i`, put

```text
d_plus(x)  = deg(x,U_(i+1)),
d_minus(x) = deg(x,U_(i-1)).
```

The exact boundary matching calculation gives

```text
d_plus(x)  = 1 - indicator[x~a_(i+1)],
d_minus(x) = 1 - indicator[x~a_(i+2)].
```

The nonedge `x,v_(i+2)` has exactly two common neighbors. The only
candidates are `a_(i+1),a_(i+2)` and `U_(i+2)`. Hence

```text
deg(x,U_(i+2))
  + indicator[x~a_(i+1)]
  + indicator[x~a_(i+2)] = 2,
```

and therefore

```text
deg(x,U_(i+2)) = d_plus(x)+d_minus(x).           (3)
```

At `P=0`, every consecutive matching has nine edges. Summing (3) over
`U_i` shows that each opposite-class graph has exactly 18 edges and maximum
degree two on both sides.

## 3. Cube and Wagner patterns over a square

In a cubic triangle-free eight-vertex extension, the remaining vertices are
uniquely `b_i in U_i` and induce a four-cycle. There are three four-cycles
on the labelled set:

```text
01,12,23,30                    cube;
02,21,13,30                    Wagner;
01,13,32,20                    Wagner.
```

The two Wagner patterns require both opposite-class edges and one opposite
pair of consecutive-class matching edges.

The degree equations do not force either crossed pattern. Take the nine
active vertices of each `U_i` as `Z/9` and one inactive vertex. Use identity
matchings between all consecutive classes. Between `U_0,U_2`, use shifts

```text
A={0,1};
```

between `U_1,U_3`, use

```text
B={2,3}.
```

All active vertices have two opposite neighbors and both consecutive
neighbors; inactive vertices have none. Thus (3), the edge totals, and the
degree caps all hold. But

```text
A intersect B = empty,
A intersect (-B) = empty,
```

so neither crossed Wagner pattern occurs. This is a shell countermodel, not
an SRG completion.

## 4. Five-cycle incidence target

The verified point--triangle incidence geometry has 33,264 simple
ten-cycles. These are in bijection with induced `C5`s in the target: each
graph edge lies in its unique triangle, and a chord would repeat a triangle
line in the incidence lift.

Writing the Wagner graph as an eight-cycle with four antipodal chords,
every induced `C5` uses exactly one chord and one of the two four-edge rim
paths between its endpoints. Hence every Wagner contains

```text
4*2 = 8
```

induced `C5`s. Therefore

```text
sum_F e_W(F) = 8*W8.                             (4)
```

By (2), the exact sufficient aggregate target is

```text
sum_F e_W(F) >= 8*18710 = 149680.                (5)
```

## 5. Exactly forty marked C5s per nonedge

Fix a nonedge `uv` with common neighbors `p,q`. They are nonadjacent, or the
edge `pq` would have both `u,v` as common neighbors.

Choose `p` as the middle of the marked two-edge path `u-p-v`. Let `a` be
the unique triangle apex on `up`, and `b` the unique triangle apex on `vp`.
Define

```text
X = {x in N(u): x is nonadjacent to v and p},
Y = {y in N(v): y is nonadjacent to u and p}.
```

The only exclusions inside `N(u)` are `p,q,a`, so `|X|=11`; similarly
`|Y|=11`.

For `x in X`, the two common neighbors of the nonedge `xv` lie in `Y`
except possibly at `q` and `b`. Thus

```text
deg(x,Y) = 2 - indicator[x~q] - indicator[x~b].  (6)
```

The edge `uq` has exactly one apex in `X`. The nonedge `ub` has common
neighbor `p` and exactly one further common neighbor in `X`. All exclusions
follow from the saturated `lambda=1` and `mu=2` equations. Summing (6),

```text
|E(X,Y)| = 2*11 - 1 - 1 = 20.                   (7)
```

Every edge `xy` in (7) gives exactly the induced cycle

```text
u-p-v-y-x-u,
```

and every induced `C5` with marked diagonal `uv` and middle `p` arises this
way. Repeating with middle `q` gives exactly

```text
40
```

marked induced `C5`s at every nonedge. Globally,

```text
4158*40 = 166320 = 5*33264,                     (8)
```

which checks both sides of the marked-diagonal incidence count.

## 6. Canonical Wagner success

For a marked cycle `C=u-p-v-y-x-u`, let:

- `r` be the other common neighbor of `u,y` besides `x`;
- `s` be the other common neighbor of `v,x` besides `y`.

The marked cycle extends to a Wagner when:

```text
r and s are distinct and nonadjacent;
N(r) intersect C = {u,y};
N(s) intersect C = {v,x};
some z in N(r) intersect N(s) has N(z) intersect C = {p}.
```

Then `C union {r,z,s}` induces `W8`. Conversely, the complement of a `C5`
inside a Wagner is a three-vertex path. Its middle vertex has a unique
neighbor on the `C5`, which selects the marked diagonal. Thus every
`(C5,W8)` incidence supplies one marked success, and every nonfailed mark
supplies at least one incidence.

## 7. The four-failure lemma would close the endpoint

Let `f(uv)` count the 40 marked cycles at `uv` with no Wagner extension.
If

```text
P=0 => f(uv)<=4 for every nonedge uv,             (9)
```

then the number of successful marks is at least

```text
4158*(40-4) = 149688.
```

Equation (4) gives `8*W8>=149688`, hence `W8>=18711`. With
`C8<=3118`,

```text
W8 - 3*C8 >= 18711 - 3*3118 = 9357,
```

which contradicts the endpoint covariance bound.

Equation (9) is not proved. Pair equations allow up to four obvious
endpoint-support failures in each of the `p` and `q` lanes. Even pure
endpoints still need nonadjacency and a common neighbor with exact singleton
support. A cross-lane compatibility argument must reduce the possible total
from eight to four.

## 8. Exact conic target and order boundary

Let `A` be the verified endpoint cube/Wagner covariance slack and `B` the
Wave 165 cube-prism slack:

```text
A = 37422+12*C8-4*W8,
B = 37422-12*C8.
```

A rational conic certificate for `W8>=18710` may combine:

- the 87-dimensional nonedge-root covariance block;
- the complete root-3 and root-12 four-root blocks;
- exact deletion, marked, and endpoint affine rows;
- nonnegative count slacks; and
- nonnegative multiples of `A` and `B`.

The target identity is

```text
8*W8-149680
  = PSD block pairings + affine equalities + nonnegative slacks.
```

An exact rational Gram factorization and coefficient replay would be a
proof-producing certificate.

The verified Wave 150 pair-root pseudowitness has

```text
C8 = 11781/4,
W8 = 35343/2,
A  = 2079,
B  = 2079.
```

It satisfies the pair-root centered blocks with equality. Therefore the
pair-root order-eight block and the new scalar inequalities alone cannot
prove the target. A successful order-eight dual must use the whole
root-3/root-12 blocks that refute this witness.

Alternatively, let `t_m` be the number of Wagner completions of a marked
`C5`. Order eight controls `sum t_m=8W8`, but failure is the nonlinear event
`t_m=0`. Without a uniqueness or uniform-overlap lemma, the second moment
`sum t_m^2` uses a marked five-cycle plus two three-vertex completions and
naturally has union order eleven. Cauchy--Schwarz then gives

```text
number of successful marks >= (sum t_m)^2 / sum t_m^2.
```

This supplies the clean next hierarchy if the coupled order-eight conic dual
still has a rational pseudowitness.
