# Wave 27 retained failed and bounded routes

## 1. The proposed algebraic `E6` trace floor 18 is false

A first route tried to prove

```text
S=E6,
Q even positive-definite integral,
SQ congruent to I modulo 2
  ==>
tr(SQ) >= 18.
```

That statement is false.  In the standard `E6` basis, put `H=E6^-1`,

```text
v=(-1,0,1,0,0,-1),
P=v(v^T H)/(v^T H v),
B=I+8P,
Q=HB.
```

The exact checker confirms `v^T H v=4/3`, `P^2=P`, `B=SQ`, `B=I (mod 2)`,
and that `Q` is symmetric, integral, even, and positive definite.  Yet

```text
spec(B)={9,1,1,1,1,1},
tr(B)=14,
det(Q)=3.
```

This block is an exact hostile control against a purely algebraic trace
argument.  It is not a projector/Schur object: the cubic-parity theorem
excludes that stronger origin.

## 2. The first tensor norm was not classified

The exact enumeration proves only the closed balls needed for the theorem:

```text
E6 parity coset: no tensor of squared norm at most 18,
A6 parity coset: no tensor of squared norm at most 60.
```

The actual zero-sum projector origin makes every local cubic energy divisible
by six, giving the safe floors 24 and 66.  The checker does not claim these
floors are attained or classify the first vector of either affine tensor
coset.  Exploratory larger-cap searches are not used as evidence.

## 3. Nonorthogonal root subsystems are not summands

For an integral orthogonal summand `S=R orthogonal_sum C`, the frame block is
exactly

```text
sum_i z_i z_i^T=21 R^-1.
```

A nonorthogonal root subsystem need not inherit this identity.  Orthogonal
projection can land in a dual or glue coset rather than in the displayed root
lattice.  Applying the parity enumeration to such a subsystem would be
invalid, so no such claim is made.

## 4. Norm-four vectors break the direct `A2` incidence argument

The `A2` proof uses the fact that `A2` represents no vector of norm four.
Every irreducible `A_n` with `n>=3`, and the larger simply-laced root
lattices, has norm-four vectors.  Such a row can lie entirely in the
summand, changes the root-incidence energy count, and has no norm-two
complement.  The general safe capacity inequality therefore retains the
unknown norm-four code parameter `alpha4(R)`.

The tensor-parity proof does not classify rows by norm and remains valid in
the presence of norm-four vectors.

## 5. No `E8` or `A20` cubic minimum is claimed

An attempted direct `E8` symmetric-cubic enumeration was not completed and
is non-evidentiary.  No tensor minimum for `E8` or `A20` is imported.  The
only floors used for those components in the conditional full-ADE census are
the elementary AM-GM bounds 8 and 24.

Consequently

```text
S=A20 orthogonal_sum E8^3,
h=21
```

survives this conditional screen.  This is a lattice type, not a constructed
frame, Schur certificate, primitive embedding, or graph.

## 6. An empty necessary-condition ball is one-way evidence

The parity constraints are necessary for projected rows.  Therefore an empty
ball proves a lower bound.  If the affine tensor coset were nonempty, that
would not produce a row multiset: symmetry, second-moment equality beyond
parity, row norms, the projector entry alphabet, and all cross-component
conditions would still need to be realized.

## 7. Scope wall

The new unconditional-in-component conclusions are:

```text
orthogonal A6 summand at the endpoint: refuted,
orthogonal E6 summand at the endpoint: refuted.
```

The rank-44 index conclusion is conditional on the entire scaled-dual form
being an orthogonal ADE root lattice.  General even determinant-`h` forms
need not be root lattices and are not classified.  Thus all eight arithmetic
`h` rows, `n3=708`, Conway-99 existence, and novelty remain `UNKNOWN` in the
unrestricted problem.
