# Wave 41 even-part equality: clean-room protocol freeze

Date: 2026-07-27 UTC

Role: verifier

## Frozen premises

Only the following independently verified Wave 39/40 statements are admitted
before implementation freeze:

1. For an edge normal form indexed by a positive partition of six with `e`
   even parts, the 27-point transported block
   `S=(J-I-2A)[L,L]` over `F_7` has rank `25-2e`.
2. The twelve vertices in the third fibre are indexed by a permutation
   `pi:X->Y`; their border matrix is `U_pi`.
3. If `H` spans `ker(S)`, then
   `min_pi rank(H^T U_pi)=e`.
4. The third fibre induces a perfect matching on its twelve labelled
   vertices, hence has exactly `(11)!!=10,395` possibilities.
5. The global transported matrix has the same characteristic-seven rank as
   `M`.

The clean-room implementation will rederive the equality criterion for the
39-point block and independently enumerate:

- every minimum-projection permutation for each of the seven types containing
  an even part;
- every distinct right kernel of the projected border matrix;
- all 10,395 labelled third-fibre matchings for every distinct equality
  target.

No file under `attempts/wave41-evenpart-equality/` may be opened, imported, or
executed until the independent implementation, tests, and result artifact are
frozen by SHA-256.

## Equality criterion to be checked

For

```text
K_39 = [[S,U],[U^T,W]]
```

let `B=H^T U`, let the columns of `R` span the right kernel of `B`, and solve
`S X=U R`.  This solve exists because `ker(B)` is exactly the set of
coefficients whose border combination lies in `im(S)`.  Symmetric Schur
elimination gives

```text
rank(K_39)=rank(S)+rank([[0,B],[B^T,C]])
```

for a congruent residual block.  Its rank is the lower-bound value
`rank(S)+2 rank(B)=25` if and only if

```text
R^T (W R-U^T X) = 0.
```

This zero condition is unchanged by a different basis of `ker(B)` or by
different solutions of `S X=U R`.

## Status wall

Even a complete incompatibility result for these seven types does not by
itself prove the universal rank-26 theorem.  Promotion is permitted only
after a separately frozen clean-room package covers all four all-odd types
and the two results are composed.  Conway-99 existence, `n3`, endpoint
exclusion, general upper-bound improvement, novelty, and priority remain
`UNKNOWN` or `NOT PROVED`.
