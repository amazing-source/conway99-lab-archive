# Wave 86 literature freeze

Access date: 2026-07-28 UTC.

## Exact Eisenstein normalization

Jorge Florez, Cihan Karabulut, and An Hoa Vu,
*Eisenstein series whose Fourier coefficients are zeta functions of binary
Hermitian forms*, arXiv:2002.09819v1.

- Primary source: <https://arxiv.org/abs/2002.09819>
- Equations (2.5)--(2.8) give the normalized twisted Eisenstein
  q-expansions and the Fricke exchange.
- For the odd quadratic character `chi=(-7/.)`,
  `g(chi)=i*sqrt(7)`.  Converting the displayed unnormalized Fricke formula
  to the q-normalization used here gives

```text
A_k=E_k(chi,1) | W_7 = -i*7^((k-1)/2) B_k,
B_k=E_k(1,chi) | W_7 = -i*7^((1-k)/2) A_k.
```

The two imaginary factors cancel in every weight-22 product.  The exact
implementation also checks that the resulting rational Fricke matrix
squares to the identity.

## Standard inputs

The scalar theta transformation follows directly from Poisson summation.
For rank 44 and `det(L)=7^16`,

```text
Theta_L | W_7 = -7^3 Theta_K.
```

The minus sign is `i^(-22)=-1`.  The standard index-eight Sturm bound in
weight 22 and level seven is 14.

No genus classification or lattice-realization theorem is imported.
