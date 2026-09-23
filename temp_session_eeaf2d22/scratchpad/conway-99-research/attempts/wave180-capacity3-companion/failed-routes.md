# Boundary and failed continuations

## Ordinary cap ceilings are too large

Each star space `E_x` is a nondegenerate minus-type six-space.  Its seven
star points form a simplex, and each of their 35 triples has one fourth
point completing a plane conic.  Even the elementary local ceiling

```text
7+binomial(7,3)=42
```

allows far more selected points in `E_x` than the compulsory seven.  The
sharp cap ceiling 56 in `PG(5,3)` is weaker for this mechanism.  Neither is
a lower bound on how many external selected points must lie in `E_x`.

## The first Pluecker wedge is identically zero

For the Pluecker point `omega_x` of a six-space in an 11-space,

```text
omega_x wedge omega_y in exterior_power^12(V)=0
```

for every pair, regardless of their intersection.  Point incidence
`z wedge omega_x=0` is valid, but the 99 star spaces are not known to form a
linear section of a Grassmannian.  Standard linear-section bounds therefore
do not apply.

## Exact local incidence still has slack

For a fixed triangle `T`, 36 vertices are adjacent to exactly one point of
`T` and 60 vertices are anticomplete to it.  Counting incidences with the
36 block partners having `j=2` gives:

```text
sum_(x anticomplete to T) t_(x,T)=36.
```

Every Wave 180 external-star incidence has `t_(x,T)=3`, so this permits as
many as 12 such centers for one `T`.  Dually, a fixed `x` has 140
anticomplete triangle blocks and total `t`-mass 84, permitting as many as
28 Wave 180 conic completions.  These are exact ceilings, not
contradictions.

## Raw circuit abundance cannot close the branch

A rank-11 ternary graphic matroid supplies a hostile scale control.  The
cycle matroid of `K_(6,6)` has length 36, girth four, and

```text
225   four-circuits,
2400  six-circuits,
16200 eight-circuits,
18825 total projective circuits of weights 4,6,8.
```

Orienting every edge from one bipartition class to the other makes these
cycles coefficient-balanced over `F_3`.  This is not a target model, but it
shows that rank, projectivity, girth, balance, and the raw lower bound 2,772
alone cannot force a contradiction.

## Remaining bridge

A continuation must exploit compatibility between the companion conics
across several overlapping star spaces, or turn the localized signed
circuits into a complete-weight upper bound below 5,544.  Neither bridge is
currently proved.
