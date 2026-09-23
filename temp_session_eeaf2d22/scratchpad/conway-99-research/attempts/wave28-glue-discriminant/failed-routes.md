# Wave 28 glue/discriminant failed routes and boundaries

## Discriminant order alone

The determinant and the containment `21S^-1` integral determine the abstract
group

```text
A_S = (Z/3Z)^u direct_sum (Z/7Z)^v,
```

but not its quadratic form.  The normalized Gauss-sign calculation reduces
the possibilities to twelve; it does not delete any of the eight determinant
rows.  Treating the group order as a complete genus invariant would therefore
be invalid.

### Corrected class-count error

The first live integration snapshot incorrectly said there were eleven
discriminant-form types.  The deterministic census caught the arithmetic
mistake before publication:

```text
four pure-prime determinant rows * one type = 4
four mixed-prime determinant rows * two types = 8
total                                      = 12.
```

The erroneous count is retained here and in the JSON correction record.  A
hostile regression test requires the current count to be twelve and explicitly
rejects eleven.

## Reusing the Wave 27 orthogonal-summand compression

An embedded root subsystem need not be an orthogonal integral summand of `S`.
Its real orthogonal projection need not define integral principal blocks of
`S` and `Q`, so the complementary positive-integral-determinant trace floor
from Wave 27 cannot be imported.  The single-root calculation instead keeps
the unavoidable index-two glue explicit.

## Calling a root primitive and then splitting it

Odd determinant does force every norm-two root to have divisibility one.  This
has the opposite consequence from an orthogonal split:

```text
[S : (Zr direct_sum r_perp)] = 2.
```

Thus a root is never an orthogonal `A1` summand here.  Silently replacing the
index-two overlattice by a direct sum loses exactly the glue that Wave 28 is
meant to study.

## One-dimensional projector moments

For a root `r`, the vector `t=XSr` has entries in
`{0,+/-1,+/-2}`, sum zero, and squared norm 42.  The pure cubic projection
removes 14 of the 46 second-moment count patterns, but 32 patterns remain.
In particular,

```text
21 entries +1, 21 entries -1, 189 entries 0
```

passes every scalar moment used here.  These count identities are a necessary
condition, not an exclusion or a row realization.

## Theta-series shortcut

The exact level of `S` is `rad(det(S))`, namely 3, 7, or 21.  This does not
make the lattice strongly modular and does not supply an Atkin--Lehner
isometry.  No scalar or vector-valued modular-form classification is imported
in this lane.

## Finite ADE determinant census

Enumerating ADE determinants with square index would address only the case in
which roots span the rational space.  Even there, an even overlattice is
controlled by isotropic glue and may retain the same root system.  A
determinant-only census would not certify glue existence, absence of new
roots, or the endpoint projector/Schur origin, so it is not used as negative
evidence.
