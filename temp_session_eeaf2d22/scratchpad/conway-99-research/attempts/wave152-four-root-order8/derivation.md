# Derivation

## 1. Four pointwise-labeled roots

Let `tau` be one of the nine locally admissible graph types on labels
`0,1,2,3`. The labels are fixed pointwise: no root automorphism is used to
identify flags.

A `tau`-flag adds two free vertices `4,5`. Only the transposition of the two
free vertices is quotiented. Filtering by the common-neighbor caps

```text
adjacent pair:    at most 1 common neighbor,
nonadjacent pair: at most 2 common neighbors
```

gives the following exact flag dimensions:

```text
root mask:   0   1   3   7  11  12  13  15  30
dimension: 224 201 155  99  69 178 125  60  70
```

No automorphism of a hypothetical 99-vertex graph is assumed.

## 2. Raw moments close at order eight

For an ordered root embedding `theta` of type `tau`, let `c(theta)` be the
vector counting all unordered free pairs by flag type. There are

```text
binom(95,2) = 4465
```

free pairs, so every `c(theta)` has coordinate sum 4465.

Define

```text
R_tau = number of ordered root embeddings of type tau,
s_tau = sum_theta c(theta),
M_tau = sum_theta c(theta)c(theta)^T.
```

Two free pairs can be equal, meet in one vertex, or be disjoint. Their unions
with the four roots therefore have orders 6, 7, or 8 respectively. Every
entry of `M_tau` is consequently a linear combination of the order-6,
order-7, and order-8 induced counts.

The first moment `s_tau` comes from the order-six diagonal contribution.

## 3. Centered covariance

For every real vector `v`,

```text
v^T (R_tau M_tau - s_tau s_tau^T) v
  = sum_theta (R_tau*v^T c(theta) - v^T s_tau)^2 / R_tau
  >= 0.
```

Equivalently,

```text
R_tau M_tau - s_tau s_tau^T
```

must be positive semidefinite. Wave150 order-eight counts have denominators
dividing four, so

```text
B_tau = 4 * (R_tau M_tau - s_tau s_tau^T)
```

is an integer symmetric matrix.

The total checks are

```text
sum_i s_tau[i]       = R_tau * 4465,
sum_{i,j} M_tau[i,j] = R_tau * 4465^2.
```

## 4. Exact separating directions

The discovery evaluator found numerical negative eigenvectors, rounded them
to integer vectors, and then computed the quadratic values using Python
integers. Zeroing coordinates greedily retained strict negativity.

The stored certificates specify the exact flag masks, indices, integer vector
entries, and exact value of `v^T B_tau v`. Strictly negative integer values
are solver-free non-PSD certificates.

The clean-room verifier reconstructed the matrices from frozen induced counts
and independently replayed both values.

## 5. Linear cutting planes

For a fixed integer direction `v`, write `q_H(v)` for the coefficient of an
induced class `H` in `v^T M_tau v`. At the endpoint the order-six counts and
therefore `v^T s_tau` are fixed. Thus

```text
R_tau * sum_H q_H(v) x_H - (v^T s_tau)^2 >= 0
```

is a valid linear inequality in the order-seven and order-eight counts. The
cut builder divides all coefficients by their gcd and stores a primitive
integer row.

The first feedback solve demonstrates why one separating direction is not a
global proof: the relaxation moves to a different exact rational point, with
one cut active.

## 6. Cube-versus-Wagner inequality

On the eight-cut replacement, the mask-12 covariance block has an exact
two-by-two principal submatrix on flag masks 21812 and 22708:

```text
[ a b ]
[ b a ],  with b>a.
```

Thus the direction `(1,-1)` is exact and has negative quadratic value
`2(a-b)`. Rebuilding its class coefficients and taking their primitive gcd
gives

```text
18711 + 6*x8[2022000] - 2*x8[5683824] >= 0.       (1)
```

Canonical isomorphism against explicit controls shows:

```text
2022000 = Q3, the 3-dimensional cube;
5683824 = the Wagner graph, C8 plus opposite chords.
```

If `N_Q3` and `N_W` denote their induced counts, (1) becomes

```text
2*N_W <= 18711 + 6*N_Q3.
```

The left side and the variable term on the right are even, so integrality
sharpens this to

```text
N_W <= 3*N_Q3 + 9355.
```

Only one order-six class occurs in this direction: canonical mask `1884`,
with quadratic coefficient 8 and zero first moment. In the independently
transcribed six-class formulas its count is

```text
x6[1884] = 41580 - n3.
```

The root-embedding factor is `1014552`; the primitive divisor is
`16232832 = 16*1014552`. Thus before substituting the endpoint, the primitive
inequality is

```text
(41580-n3)/2 + 6*N_Q3 - 2*N_W >= 0,
```

or, after multiplying by two,

```text
4*N_W <= 41580 - n3 + 12*N_Q3.                 (2)
```

At `n3=4158`, equation (2) specializes to (1) and integrality gives the
displayed `+9355` endpoint corollary. Equation (2) is a candidate general
necessary inequality for `srg(99,14,1,2)` pending the separate Wave157
proof/verifier gate. It supplies no standalone strict upper bound because no
independent inequality currently forces `N_W-3*N_Q3` to be large enough.
