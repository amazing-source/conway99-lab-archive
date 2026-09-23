# Wave 150 derivation

## 1. Centering the finite Gram matrix

For one of the two ordered-root families, let `c(theta)` be the integer
vector of order-five flag counts around a root embedding `theta`.  Put

```text
M = sum_theta c(theta)c(theta)^T,
s = sum_theta c(theta),
R = number of ordered root embeddings.
```

The covariance identity is

```text
M - s*s^T/R
  = sum_theta (c(theta)-s/R)(c(theta)-s/R)^T
  >= 0.
```

This is exact finite arithmetic.  It is stronger than the uncentered
condition `M>=0`.  Here `R=99*14=1386` for ordered edges and
`R=99*84=8316` for ordered nonedges.

The first-moment vector `s` is fixed by the known order-five induced counts:
for an order-five class, both free triples in the Wave 147 product coincide,
so its coefficient matrix is diagonal and records the rooted flag counts.

## 2. Normalized reconnaissance

Let

```text
p7(H) = x_H / C(99,7),
p8(K) = x_K / C(99,8).
```

The ordinary deletion equations simplify exactly to

```text
p7(H) = (1/8) sum_K d(H,K)p8(K).
```

The marked Wave 148 equations become

```text
lhs(H,tau)*p7(H)
  = (23/2) sum_K e(H,tau,K)p8(K).
```

SCS and Clarabel place the common centered PSD margin within about `1e-9`
of zero.  A first HiGHS run incorrectly reported infeasibility when
nonnegativity was encoded as column bounds with presolve enabled.  Replacing
those bounds by explicit inequalities and disabling presolve produced a
feasible point with residuals around `1e-13`.  The false status is retained
as a failed numerical route and is not evidence.

## 3. Exact reconstruction

At the explicit-bound HiGHS point:

- all order-seven raw counts are within `0.01` of integers;
- rounding gives a nonnegative 204-support vector of total `C(99,7)`;
- the rounded vector satisfies all 170 Wave 44 equations exactly at
  `y=h11/4=2079`; and
- exactly 874 order-eight coordinates are stably positive.

Set the other 42 order-eight coordinates to zero.  The exact equations for
the remaining variables are:

1. total order-eight count;
2. all ordinary deletion rows;
3. every nontrivial marked vertex and ordered-pair row; and
4. every upper-triangular entry of

   ```text
   R*M - s*s^T = 0
   ```

   for both ordered-root families.

There are 10,310 nontrivial full-system equations; 10,259 remain after
restricting to the selected support. Sparse modular elimination has full
column rank 874 over `F_1000003`; the first full-rank subsystem occurs after
1,931 restricted rows. Solving it over `Q` gives a nonnegative solution with
denominator at most four. Direct rational replay satisfies all 10,310
full-system rows.

## 4. Meaning

The witness shows that all constraints represented in this finite
relaxation can coexist at `n3=4158`, even with zero covariance in both
pair-root blocks.  Thus no dual certificate excluding the endpoint exists
inside this exact model.

It does not realize the overlapping subsets as a 99-vertex graph. The
remaining obstruction necessarily lives in a stronger compatibility layer.
