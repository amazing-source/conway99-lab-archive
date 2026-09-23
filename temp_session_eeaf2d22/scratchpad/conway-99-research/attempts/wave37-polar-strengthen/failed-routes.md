# Wave 37 polar-strengthening limits and refuted routes

This lane starts from the conditional prism-free endpoint `n3=4158`.  It
does not construct the endpoint matrix or graph.

## Refuted: every balanced signed triangle is collinear

The signed support matrix satisfies

```text
S^2=13S+68I.
```

Consequently, for every support edge, the number of balanced signed common
neighbors minus the number of unbalanced signed common neighbors is 13.
Globally,

```text
balanced triangles - unbalanced triangles = tr(S^3)/6 = 34034.
```

It is **false** that all 34,034 of these balanced triangles give
weight-three words in the dual ternary code.  Their ternary `3 x 3` Gram
matrix has rank one, but a singular Gram matrix inside a nondegenerate
ambient space does not force the vectors to be linearly dependent.  Three
independent vectors can span a degenerate three-space with a
two-dimensional radical.

There are at most

```text
7854/3 = 2618
```

collinear selected triples: each nonorthogonal pair lies on a unique
projective line and therefore belongs to at most one such triple.  The
correct consequence is instead that at least 31,416 balanced triples are
linearly independent, forcing at least 437 distinct rank-one degenerate
three-spaces.  This is a restriction, not a contradiction.

## Ternary code and MacWilliams relaxation survive

The endpoint would supply a projective self-orthogonal ternary
`[231,r3]` code with `1` in its dual, both nonzero symbol counts divisible
by three in every word, and

```text
A_69 >= 462.
```

At `r3=12`, the checker gives an exact nonnegative real
MacWilliams/Delsarte relaxation satisfying `B1=B2=0` and `B_j>=A_j`.
Most transformed coefficients are nonintegral, so this is not a formal
weight enumerator and not a code.  It is only a hostile control showing that
the basic real linear-programming inequalities do not reject the boundary.
No complete integer weight-enumerator or code-realizability classification
was performed.

## Ternary divisibility sharpens Evans but leaves large slack

For every ambient ternary point, the two nonzero inner-product counts are
separately divisible by three.  In particular, every outside orthogonality
degree is divisible by three.  Replacing the ordinary consecutive-integer
polynomial with the consecutive-allowed-values polynomial gives

```text
sum_z (b_z-75)(b_z-78) = 5843880 > 0.
```

This is stronger than the ordinary Evans value `6020322`, but it does not
exclude the square determinant class in dimension twelve.

## Full oriented ternary association scheme survives

The oriented norm-two scheme distinguishes equality, antipodality,
orthogonality, and the two signed nonorthogonal relations.  The exact
endpoint inner distribution

```text
(1,0,162,36,32)
```

has nonnegative transform in all five primitive eigenspaces.  Thus retaining
the signed `36/32` split gives no rank-twelve contradiction at this level.

## Characteristic seven gives no new rank floor

The Wave 36 cube identity makes the 231 characteristic-seven factor rows
projectively distinct norm-one points.  At rank eleven, the orthogonality
graph on their ambient point type is not strongly regular: nonorthogonal
pairs split into three orbits with different common-neighbor counts.
Therefore Evans's strongly-regular-graph polynomial is not applicable.

The exact five-class association scheme gives largest nonprincipal
orthogonality eigenvalue

```text
square class:     2401(1+sqrt(2)),
nonsquare class:  4802.
```

Both values already exceed the target induced degree 162, so spectral
mixing has no exclusion power.  Both rank-eleven determinant classes
survive this test.

## Status

No rank floor is raised, no determinant class beyond the Wave 36 ternary
rank-twelve nonsquare class is excluded, and the general bound remains

```text
n3 <= 4158.
```

The endpoint and Conway-99 remain `UNKNOWN`.
