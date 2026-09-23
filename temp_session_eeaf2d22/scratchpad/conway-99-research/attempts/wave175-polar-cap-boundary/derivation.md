# Finite-polar continuation after Wave 174

## 1. The correct polar object

At the endpoint, factor the centered ternary Gram matrix as

```text
D=V*H*V^T,
```

where `H` is nondegenerate and `k=rank_F3(D)=r3-1`.  The diagonal of `D`
is zero, so the 231 rows of `V` represent singular projective points.
Symmetry and `D^2=0` give

```text
V^T*V=0.
```

The zero entries in each row of `D` show that every selected point is
orthogonal to exactly 32 other selected points.  Wave 174 proves
`d(W^perp)>=4`, so no three selected projective points are collinear.

The smallest surviving dimension is `k=11`.  The ambient singular points
then form the parabolic quadric

```text
Q(10,3).
```

Its polar-collinearity graph has

```text
(v,k,lambda,mu)=(29524,9840,3278,3280)
```

and nonprincipal eigenvalues `80,-82`.

## 2. Exact spectral energies

Let `S` be the 231 selected points.  Its induced polar graph is regular of
degree 32, so it has 3,696 edges.  Decompose its characteristic vector as

```text
1_S=(231/29524)*1+x_80+x_-82.
```

Using its norm and adjacency quadratic form gives

```text
||x_80||^2  =37961/732,
||x_-82||^2=532/3.
```

Both are positive.  Thus the first polar Delsarte/interlacing test is
compatible with the configuration.

## 3. Divisibility-refined outside moments

For a singular point `z` outside `S`, let `b_z` count selected points
orthogonal to `z`.  The polar SRG intersection numbers and the selected
internal degree give

```text
number of outside singular points=29293,
sum b_z                        =2265648,
sum b_z^2                      =176288112.
```

The frame identity gives

```text
0=sum_i (z,g_i)^2 mod 3.
```

Every nonzero square in `F_3` is one.  Therefore the number of selected
points nonorthogonal to `z` is divisible by three, and, since `231=0 mod 3`,

```text
b_z=0 mod 3.
```

The consecutive allowed values around the mean are 75 and 78.  Exact
substitution yields

```text
sum_(z outside S) (b_z-75)(b_z-78)=1008018>0.
```

The strengthened degree-two moment test therefore survives with positive
slack.

## 4. Singular quadratic Veronese rank

Let `R` be the selected orthogonality graph.  Squaring Gram entries
coordinatewise gives

```text
D^(o2)=J-I-R.
```

This is the Gram matrix of the pure quadratic tensors `g_i^(o2)`.  The full
symmetric square of an 11-space has dimension

```text
binomial(12,2)=66.
```

All `g_i` are singular, so their pure squares lie in the hyperplane cut out
by the quadratic form.  Hence

```text
rank_F3(J-I-R)<=65.                                (1)
```

Since `I+R=J-(J-I-R)`,

```text
rank_F3(I+R)<=66.                                  (2)
```

These are necessary invariant-theory constraints new to this repository.  No
lower bound from the current regularity and projective-cap data contradicts
(1)--(2), and external novelty is `UNKNOWN`.

## 5. Terminology quarantine

Blokhuis and Moorhouse define a cap on a quadric to have no two points on a
line of the quadric.  Their cap is a partial ovoid: it forbids every
orthogonal selected pair.  The Wave 174 configuration instead has 3,696
orthogonal pairs and only forbids three points on an ambient projective
line.  Applying their numerical cap bound here would therefore be invalid.

## Boundary

The finite-polar reframing is exact and produces (1)--(2), but the
`k=11` parabolic branch survives the polar spectrum and all degree-two
divisibility-refined moments above.  No stronger rank floor, endpoint
exclusion, strict `n3` bound, graph, or Conway-99 resolution follows.
