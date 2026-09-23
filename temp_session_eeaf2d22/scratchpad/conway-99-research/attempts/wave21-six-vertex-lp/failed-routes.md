# Exact routes that do not improve the incumbent obstruction

## Six-vertex nonnegativity

All 62 affine formulas were specialized to `n=99,k=14`.  Their complete
nonnegative-integral feasible set is

```text
n3 = 0,3,6,...,4158.
```

The upper endpoint comes from

```text
n1 = 1386 - n3/3 >= 0.
```

Every other upper bound is weaker; the next is `n3<=20790` from `n5`.
Consequently the published six-vertex table is compatible with all 1,152
multiples of three from 705 through 4158.

## Hamiltonian seven-vertex nonnegativity and congruence

The 19 published counts use a second free variable `h11`.  Integrality of the
whole table is exactly

```text
h11 = 0 (mod 4).
```

For every six-vertex-feasible `n3`, simultaneous nonnegativity is exactly

```text
ceil_to_multiple_of_4(2*n3) <= h11 <= 4*n3.
```

The two facets are `h16=h11-2*n3>=0` and
`h18=n3-h11/4>=0`.  The universal choice `h11=4*n3` proves that these
published seven-vertex counts remove no feasible `n3`.  At `n3=705`, there
are 353 feasible `h11` values from 1412 through 2820.

## Raw five-to-six deck equation

The printed `m7(n-5)` identity fails by exactly `n23`; the `N23` column has
only five deletion cards.  This is not an obstruction on a putative target
graph because independent deck reconstruction shows the printed equation
omitted `+n23`.  With that explicit correction, all 21 deck equations and all
62 formula columns agree exactly.  The raw failure is preserved rather than
used as a contradiction.

## Local graph census

The independent `9,21,62,19` class census checks the source's finite indexing
and exposes the `N23` omission.  It does not establish that any locally
admissible graph embeds in a global `srg(99,14,1,2)`, nor does it turn a
formula-feasible parameter pair into a construction.

## Strongest scoped conclusion

The encoded primary-source count identities are rigorously exhausted but do
not improve or contradict the independently audited conditional
`n3>=705`.  Conway-99 and novelty remain `UNKNOWN`.

