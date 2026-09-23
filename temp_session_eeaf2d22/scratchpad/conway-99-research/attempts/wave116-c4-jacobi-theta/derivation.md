# C4 coordinate evaluation and the corrected Jacobi route

Claim label: `DERIVED` (scoped discovery; independent verification required).

Everything is conditional on a hypothetical `srg(99,14,1,2)` and the
verified Wave 66/71 lattice transfer.

## 1. Restricted `-4` projector

The primitive idempotent is

```text
E_-4=(-A+3I+J/9)/7.
```

For an induced four-cycle in cyclic order, let `H` be its `C4` adjacency
matrix.  The principal coordinate Gram is therefore

```text
E=E_-4[C]=(3I-H+J/9)/7.
```

The four standard cycle modes give the exact spectrum

```text
constant:     13/63,
alternating:   5/7,
two zero-H:    3/7, 3/7.
```

Thus `E` is positive definite and

```text
det(E)=65/2401.
```

This part of the proposed route is correct.

## 2. The naive Jacobi index is not lattice-compatible

Write `C=7E_-4` for the Gram matrix of the Wave 66 vectors `u_i`, and put

```text
p_i=u_i/sqrt(7).
```

Then the `p_i` have Gram `E_-4`, and for `x=sqrt(7)y in K`,

```text
<x,p_i>=<y,u_i>=t_i.
```

However, Wave 71 proves only `3u_i in L`, not `u_i in L`.  Since
`K*=(1/sqrt(7))L`, it follows that

```text
a_i=3p_i=3u_i/sqrt(7) is in K*,
7a_i=3sqrt(7)u_i is in K.
```

There is no proof that `p_i` lies in `K*`.  Consequently the attractive
small matrix `E/2` is **not** a justified ordinary Jacobi index.

The intermediate vectors `a_i` have Gram `9E`.  Their classes in `K*/K`
have order seven.  On a cycle, seven times their Gram is

```text
G_L=63E=
[ 28 -8  1 -8 ]
[ -8 28 -8  1 ]
[  1 -8 28 -8 ]
[ -8  1 -8 28 ].
```

Its determinant is `426465`, congruent to `4 mod 7`.  The four classes are
therefore independent and span a nondegenerate `(Z/7)^4` subgroup of the
discriminant form.  This gives a legitimate 2,401-sector
characteristic/Heisenberg description, but modular transformations still
retain the orthogonal discriminant complement.  The small sector alone is
not a closed scalar Jacobi form.

## 3. A conventional common-index Jacobi sum

Use instead the actual lattice vectors

```text
g_i=7a_i=3sqrt(7)u_i in K.
```

Their cycle Gram is

```text
G_K=441E=7G_L,
```

with entries `196` on the diagonal, `-56` on cycle edges, and `7` on
opposite pairs.  Its spectrum and determinant are

```text
91,315,189,189;
det(G_K)=1023942465.
```

Choose any cyclic labeling for every induced four-cycle `C`, and define

```text
Phi_K(tau,z)
 = sum_C sum_{x in K}
   q^((x,x)/2) exp(2*pi*i*sum_j z_j<x,g_Cj>).
```

Each summand is a weight-22, level-7 lattice Jacobi theta series with the
same matrix index `G_K/2`.  A finite sum stays in that space.  No graph
automorphism is needed: the common principal Gram follows solely from every
chosen subgraph being an induced `C4`.  Dihedral changes of cyclic labeling
preserve the index.

The normalization checks are

```text
[q^0 z^0] Phi_K = 2079,
Phi_K(tau,0)=2079 Theta_K(tau).
```

The price of making the object conventional is a very large raw index:
the associated index-lattice discriminant has
`det(G_K)=1,023,942,465` classes.

## 4. Fricke is a `K/L` pair, not one fixed index

Put `v_i=3u_i in L`.  Their cycle Gram is `G_L`, and
`g_i/sqrt(7)=v_i`.  Direct Poisson summation gives

```text
Phi_K(-1/(7tau),z/(7tau))
 = -7^(q/2) tau^22 exp(pi*i*z^T G_L z/tau) Phi_L(tau,z).
```

Equivalently, with the normalized weight-22 Jacobi-Fricke slash,

```text
Phi_K || W_7 = -7^(q/2-11) Phi_L.
```

At `z=0` this is exactly the scalar Wave 101 normalization

```text
Theta_L=-7^(11-q/2)(Theta_K|W_7).
```

The elliptic index changes from `G_K/2` to `G_L/2`.  Treating Fricke as an
involution inside a single fixed-index positive cone would be incorrect.

## 5. The exact incidence coefficient

For all `K` vectors of norm at most 18, Wave 71 gives integral coordinate
values `t_i`.  Let

```text
epsilon=(1,-1,1,-1).
```

Because `<x,g_i>=21t_i`, the coefficients

```text
c(n)=[q^n z^(21 epsilon)] Phi_K, n=7,8,9,
```

select norm-14, norm-16, and norm-18 vectors alternating on the chosen
cycle.  For each cycle-support incidence, exactly one vector of the
antipodal pair has the chosen sign `epsilon`; the other has `-epsilon`.
Therefore

```text
c(7)+c(8)+c(9) = antipodal C4 incidence,
2(c(7)+c(8)+c(9)) = oriented C4 incidence.
```

Wave 112 yields

```text
c(7)+c(8)+c(9) >= 52812.
```

An upper certificate at most `2079*25=51975` would contradict this, with
gap `837`.  The alternating Fourier pattern has projection norm

```text
(21 epsilon)^T G_K^(-1)(21 epsilon)=28/5,
```

so ordinary Jacobi support/discriminant positivity permits all three
coefficients; it gives no exclusion by itself.

## 6. Finite-dimensional optimization and its present boundary

In principle one can:

1. construct an exact basis through a proved Jacobi Sturm bound;
2. impose both constant terms `2079`, the `K/L` Fricke relation, and scalar
   specializations;
3. impose nonnegative integral Fourier coefficients of both theta sums;
4. maximize `c(7)+c(8)+c(9)`; and
5. accept an upper bound only through an exact dual identity.

It is not yet known whether this cone is bounded in the target direction.
No basis, truncation proof, or dual certificate is present, so Wave 116
derives **no new upper bound**.

A smaller alternative avoids the billion-class matrix index.  On norms at
most 18, every integral `t_i` lies in `{-4,-3,...,4}`.  The indicator of
`t_C=epsilon` can therefore be interpolated by degree eight in each
coordinate, total degree 32.  Harmonic decomposition turns its shell sums
into finitely many weighted theta series.  This retains the exact incidence
but loses coefficientwise positivity, so it must be coupled to exact moment
or positive-semidefinite constraints.

Rank 28, Conway-99, and literature novelty remain `UNKNOWN`.
