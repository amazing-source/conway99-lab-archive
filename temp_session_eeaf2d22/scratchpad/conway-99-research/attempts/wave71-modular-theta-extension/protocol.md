# Wave 71 protocol: level-7 neighbor and modular reduction

Date frozen: 2026-07-27

Role: discovery

Claim label: `DERIVED`

## Imported hypothesis

This package is conditional on, and does **not** validate, the Wave 66
candidate lattice package.  Assume that a hypothetical
`srg(99,14,1,2)` supplies:

- an even positive-definite rank-44 lattice \(M\);
- \(M^*/M\cong\mathbf Z/9\oplus(\mathbf Z/7)^q\), with
  \(q\in\{2,4,\ldots,16\}\);
- \(63M^*\subseteq M\) and \(\min(M^*)\ge2\);
- vectors \(u_0,\ldots,u_{98}\in M^*\), all in one discriminant coset,
  with
  \[
  \sum_i u_i=0,\quad \sum_i u_iu_i^{\mathsf T}=7I,\quad
  \langle u_i,u_i\rangle=28/9,
  \]
  and pair inner products \(-8/9\) on graph edges and \(1/9\) otherwise.

No automorphism or transitivity assumption is made.

## Imported theorem

The modular reduction uses the main theorem of Skoruppa (2008), frozen in
`literature-freeze.md`: the theta series of an even lattice of prime-power
level \(\ell^n\) is congruent modulo \(\ell\) to a level-one modular form of
weight \(e(L)/2\), where \(e(L)\) is the sum of its Gram-matrix elementary
divisors.

The theorem is cited, not reproved.  All finite-field linear algebra after
that import is reproduced exactly in `exact_check.py`.

## Questions

1. Can the marked order-nine coset remove the 3-primary discriminant part by
   an exact even-neighbor construction?
2. What minimum and theta constraints does the resulting level-7 lattice
   satisfy?
3. Do exact mod-7 level-one theta constraints delete any of the eight rows?
4. If not, what finite short-vector alternatives are forced?

## Separation rules

- Wave 71 is discovery and cannot promote itself to `VERIFIED`.
- Group/discriminant-form existence, lattice-genus existence, and existence
  of the marked 99-vector frame are separate questions.
- A modular-form congruence is only a necessary condition.
- A bounded nonhit is not a nonexistence or novelty result.
- Conway-99 and novelty remain `UNKNOWN` absent a complete proof.
