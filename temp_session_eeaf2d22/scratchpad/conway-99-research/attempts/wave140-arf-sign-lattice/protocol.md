# Wave 140 protocol: Arf sign from integral lattice data

Claim labels are `DERIVED` for exact implications, `REFUTED_BY_CONTROL` for
an invariant set admitting both signs, and `UNKNOWN` for the full target.

## Frozen premise

Assume a symmetric integral zero-one matrix satisfies

```text
diag(A)=0,
A*1=14*1,
A^2=12I-A+2J.
```

Let

```text
R=im_F2(A),
q(x)=wt(x)/2 mod 2 on the even-weight hyperplane.
```

The target is whether the sign

```text
sum_(x in R) (-1)^q(x)=epsilon*2^27
```

is forced.

No automorphism, graph construction, Type II theorem, lattice
self-duality, or unverified finite quadratic form may be assumed.

## Lanes

1. Reconstruct the full Smith form from the determinant, modular ranks,
   and the inverse denominator.
2. Split the integral operator over `Z_2` into the `3`, `14`, and `-4`
   spectral lattices.
3. Relate the target Arf sign to the determinant square class of the
   even unimodular `3`-eigenlattice.
4. Test whether spectrum, Smith factors, or discriminant-group structure
   determine that square class.
5. State separately what a full two-primary finite quadratic form would
   add.

## Acceptance boundary

A forced sign requires a derivation using every needed target premise.
An abstract local control can refute sufficiency of the invariants it
matches, but it cannot refute a stronger argument using the entrywise
zero-one and zero-diagonal conditions unless it also realizes them.

Solver status, numerical congruence, group order, and Smith factors alone
are not quadratic-form certificates.

