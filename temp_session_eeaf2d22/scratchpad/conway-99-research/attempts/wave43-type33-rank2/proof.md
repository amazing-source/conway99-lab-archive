# Completeness proof for the type-`3+3` pivot/mate CSP

## 1. Frozen local reduction

For type `3+3`, every one of the 144 border signatures in the frozen Wave 41
coordinate system is zero. Therefore `F=0` for every border permutation and
the Schur residual is

```text
D(U,R) = W_R - T(U),
```

where `U` is a labelled permutation and `R` is a labelled perfect matching
on twelve coordinates. At the prism-free endpoint, `U` is a derangement.

## 2. Principal-pivot lemma

Let `D` be a symmetric rank-two matrix over `F_7`. It has a nonsingular
principal submatrix of order two.

Indeed, a rank factorization by congruence gives

```text
D = X^T H X,
```

where `X` has two rows and rank two and `H` is a nonsingular symmetric
`2 x 2` matrix. Two columns `x_p,x_q` of `X` are linearly independent.
The corresponding principal minor is

```text
det([x_p x_q]^T H [x_p x_q])
  = det([x_p x_q])^2 det(H) != 0.
```

The checker enumerates all such pairs, so every rank-two residual enters at
least one branch.

## 3. Complete matching cases at the pivot

For a pivot pair `(p,q)`, a perfect matching `R` has exactly two possibilities:

- `p` and `q` are mates; or
- they have two distinct mates in the remaining ten coordinates.

The checker enumerates the first case and all `10*9` ordered mate choices in
the second. Thus the pivot rows of `W_R`, and consequently of `D`, are fixed
in each branch.

## 4. Schur-complement equations

For every remaining coordinate `i`, the diagonal equation

```text
D_ii = D_iP (D_PP)^(-1) D_Pi
```

is necessary and gives an exact unary domain for `U_i`. For every pair
`i,j`, the off-diagonal equation gives the only allowed value of `W_R(i,j)`.
The matching matrix alphabet is exactly:

```text
W_R(i,j)=6  if i,j are mates,
W_R(i,j)=1  otherwise.
```

Any other required value rejects the assignment. A value six adds a forced
mate edge; degree constraints require exactly one mate per coordinate,
including the already fixed pivot mates.

At a complete leaf these equations say that the Schur complement of the
invertible pivot is zero. Therefore `rank(D)=2`. Conversely every rank-two
residual satisfies every equation and follows a branch of the search.

## 5. Exact outcome

The exhaustive deterministic search visits 666,666 branches and no complete
leaf. It therefore excludes rank two in this exact local endpoint model. The
claim remains `DERIVED` until an independent verifier reconstructs the
coordinates, pivot lemma, branch universe, and zero-leaf result.
