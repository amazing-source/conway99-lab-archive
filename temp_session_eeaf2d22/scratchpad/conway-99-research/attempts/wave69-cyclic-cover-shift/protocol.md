# Wave 69 protocol: cyclic-cover shift

## Frozen scope

This is a restricted construction/obstruction lane for an
`srg(99,14,1,2)`.

The primary hypothesis is:

> A hypothetical target graph admits a specified semiregular automorphism of
> order 11, hence a `C_11` action with nine vertex orbits of size 11.

This hypothesis is not asserted for an arbitrary target graph. No absence or
presence of automorphisms is inferred outside this restricted lane.

An additional exact lemma tests whether a nonidentity order-11 automorphism
could have fixed vertices. If the lemma succeeds, it upgrades the
semiregular-`C_11` obstruction to all order-11 automorphisms without assuming
semiregularity.

The secondary hypothesis is stronger and separate:

> A hypothetical target graph is a Cayley graph on a group of order 99.

## Role and labels

- Role: `construction` / discovery.
- Allowed promotion labels in this package: `DERIVED`, `CANDIDATE`, `UNKNOWN`.
- This package cannot label its own claims `VERIFIED`.
- Novelty relative to the literature: `UNKNOWN`.
- Status of the unrestricted Conway-99 target: `UNKNOWN`.

## Claims under test

### W69-Q1 — quotient conditions (`DERIVED`)

Under the semiregular-`C_11` hypothesis, the equitable quotient `Q` is a
symmetric nonnegative integer `9 x 9` matrix satisfying

```text
Q 1 = 14 1,
Q^2 + Q = 12 I + 22 J,
diag(Q) is even,
spec(Q) = {14, 3^4, (-4)^4}.
```

The spectrum multiplicities use the rational representation of `C_11` on the
full graph eigenspaces, not merely the quotient polynomial.

### W69-Q2 — quotient nonexistence (`DERIVED`, verification pending)

The exhaustive standard-library search in `exact_search.py` tests all row
choices for all trace-compatible sorted diagonal cases. The proof-grade
`unpruned` mode uses no within-diagonal canonical pruning. The `canonical`
mode is a faster independent cross-check of the same result.

If both searches report zero solutions, the restricted conclusion is:

> No `srg(99,14,1,2)` admits a semiregular automorphism of order 11.

### W69-F1 — fixed points of order-11 automorphisms (`DERIVED`)

For an arbitrary nonidentity automorphism of order 11, the number `f` of fixed
vertices is a multiple of 11. Exact local common-neighbor counts and a
neighbor-degree double count eliminate `f=11`, `f=22`, and every
`33 <= f < 99`. Thus `f=0`: every nonidentity order-11 automorphism is
semiregular.

Combining W69-F1 with W69-Q2 excludes every order-11 automorphism.

### W69-V1 — vertex-transitive consequence (`DERIVED`)

If a target were vertex-transitive, orbit-stabilizer would make its
automorphism-group order divisible by 99. Cauchy's theorem would then supply
an element of order 11, contradicting W69-F1 plus W69-Q2. Therefore the
restricted derivation excludes vertex-transitive targets.

This is not a nonexistence result for a target without order-11 symmetry.

### W69-L1 — cyclic lift search (`DERIVED`)

For a quotient candidate, every block would be encoded by subsets
`D_ij` of `Z_11`, with `D_ji=-D_ij`; diagonal subsets exclude zero and are
closed under negation. The frequency-zero character matrix is `Q`, while every
nonzero frequency matrix must satisfy `M_t^2+M_t=12I`.

If W69-Q2 has zero quotient candidates, the lift candidate set is empty before
any voltage SAT encoding. This is a logical consequence, not a solver nonhit.

### W69-C1 — abelian Cayley obstruction (`DERIVED`)

Every group of order 99 is abelian. Fourier inversion for a putative Cayley
connection set makes a certain sum of roots of unity equal to `-18/7` or
`81/7`. A rational algebraic integer must be an integer, so either value is
impossible.

This independently reproves the no-Cayley consequence and does not replace the
stronger order-11/vertex-transitive argument.

## Separation and reproducibility

1. Discovery does not certify itself.
2. The `unpruned` quotient search is the primary exhaustive computation.
3. The symmetry-canonical search is recorded only as a cross-check.
4. Every row shape and diagonal case is generated from the frozen equations.
5. Search order, branch counts, and transcript SHA-256 digests are
   deterministic.
6. No solver exit code is treated as a certificate.
7. Failed routes and limitations are retained.
8. Memory use must leave at least 15 percent of host RAM free.
