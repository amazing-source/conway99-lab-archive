# Wave 124 literature freeze

Access date: 2026-07-28 UTC.

## Cited structure theorem

Martin Eichler and Don Zagier, *The Theory of Jacobi Forms*, Progress in
Mathematics 55, Birkhauser, 1985.

Imported statement: the bigraded ring of weak Jacobi forms of even weight
and integral index for the full modular group is generated over
`C[E4,E6]` by `phi_-2,1` and `phi_0,1`.

Wave 124 does not import a dimension table.  It constructs the 34
weight/index-compatible monomials, expands the standard generators
exactly, and performs its own rational polar elimination.

## Definition and support convention

The standard holomorphic support condition used is

```text
c(n,r) nonzero implies r^2 <= 4mn.
```

The cusp condition replaces `<=` by strict inequality.  The elliptic
translation law reduces `r` modulo `2m`, which is used only to prove that
the finite polar audit is complete.

## Search boundary

A bounded primary-source search did not produce a ready-made exact basis
for `J_22,10(Gamma0(7))` with the required Fricke pairing and positivity
cone.  This nonhit is not evidence that no such basis or method exists.
The package therefore constructs only the rigorously controlled
full-level subspace and leaves the full level-seven basis `UNKNOWN`.
