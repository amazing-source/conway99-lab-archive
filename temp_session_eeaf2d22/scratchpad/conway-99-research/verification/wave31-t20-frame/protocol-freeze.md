# Wave 31 T20 frame verifier protocol freeze

## Role and frozen submission

This package is a fresh verifier lane.  It did not author the construction
and does not import or execute the construction checker as part of its
independent result.

The submitted package is frozen at:

```text
commit: 67a0e4585c9c378dcd658784a3876564557b70e3
tree:   47ef723b915045c0ef83f15b49235b278dbfb6aa
parent: 31bc516a581decb6394bf5e780f07fb05d567274
```

The exact SHA-256 inventory is in `input-freeze.sha256`.  The verifier reads
the committed candidate bytes, checks that the worktree copies agree, and
validates both the submitted eight-entry artifact manifest and its four-entry
upstream input freeze.

The construction report and run report were generated before the construction
commit and therefore contain the parent hash
`31bc516a581decb6394bf5e780f07fb05d567274`.  This verifier resolves that
provenance detail by freezing the final submitted bytes at commit
`67a0e4585c9c378dcd658784a3876564557b70e3`; it does not reinterpret the
embedded parent hash as the submission commit.

## Claim under review

The only eligible positive verdict is:

```text
PASS_SCOPED_FINITE_EVIDENCE
```

It means all of the following and nothing stronger:

1. The displayed rank-20 Gram matrix has exactly 5,076 nonzero integral
   vectors of norm at most four, all of norm four, hence 2,538 antipodal
   lines.
2. The submitted canonical line list, line hash, residue counts, pair
   inner-product counts, and absolute-two degree distribution are exact.
3. The 105-line second-moment formulation and its stated GF(2) rank and
   consistency are exact.
4. Every submitted rational weight is in `[0,1]`, the weights sum to 105,
   and all 210 upper-triangular moments equal `21*T20^-1`.
5. The named 105-line near-frame is not a frame, and no exact second-moment
   support occurs within one or two exchanges of that named support.
6. The maximum-coordinate-one domain is excluded by the stated diagonal
   bound.
7. Under the frozen endpoint premises, `B_U=I` forces `A4_U=M_U`, and all 84
   diagonal excess units lie on the 105-row T20 block.
8. No solver timeout or bounded nonhit is promoted beyond its exact domain.

The following remain `UNKNOWN` regardless of a pass:

```text
unrestricted Boolean 105-line second-moment frame
oriented zero-sum alphabet frame
Q_A / B_A / A4_A package
coupled T20 plus U24 endpoint
rooted or integrally indecomposable endpoint forms
n3=708
Conway-99
novelty
```

## Independent methods fixed before verdict

### T20 and complete short shell

The verifier parses the Gram matrix as data from the frozen Wave 30 source.
It independently checks symmetry, even integrality, determinant 729, exact
positive definiteness, a fresh rational inverse, integrality of
`21*T20^-1`, and

```text
T20 * (21*T20^-1) = 21 I_20.
```

It then performs complete reverse recursion on the exact identity

```text
x^T T20 x = sum_i d_i (x_i + center_i)^2
```

from a rational `LDL^T` factorization.  At each level, an integer-square-root
bound lists every integer in the exact closed interval permitted by the
remaining norm budget.  Every summand is nonnegative, so this recursion
cannot prune a vector of norm at most four.

The entire enumeration is repeated after the nontrivial coordinate
permutation

```text
(7,1,14,0,19,3,11,6,17,8,2,15,5,13,9,18,4,12,16,10).
```

The changed-basis vectors are mapped back and must equal the original shell
exactly.  The verifier then canonicalizes antipodal lines by the first
nonzero coordinate and compares the complete ordered list, not merely its
cardinality, with the submission.  No automorphism quotient is used.

### Pair geometry

For every one of the `2,538 choose 2 = 3,219,453` unordered line pairs, the
verifier computes `v^T T20 w` with Python integers.  It accumulates the signed
counts and the degree of every vertex in the absolute-two graph.  It also
checks the handshake identity.  Modulo-two and modulo-three uniqueness is
recomputed directly from all canonical lines.

### Moment system and rational certificate

For each line `v`, the verifier constructs all 210 entries `v_i*v_j` with
`i<=j`.  It checks that tracing the target against T20 gives

```text
trace(T20 * 21*T20^-1) / 4 = 105.
```

Repeated antipodal lines cannot occur in an endpoint alphabet frame because
two copies have inner product `+4` or `-4`, outside
`{0,+1,-1,-2}`.  Therefore the Boolean line formulation is necessary.

The 210 moment equations and the odd-cardinality equation are independently
row-reduced as bitsets.  Coefficient and augmented ranks are computed
separately so that consistency is not inferred from a combined rank alone.

The rational witness is verified as a certificate, without reconstructing it
from the discovery solver.  All 2,538 weights are instantiated exactly as
`Fraction` values.  Bounds, support disjointness, the weight sum, every moment,
and the canonical certificate hash are checked.

### Named radius-two domain

The verifier recomputes the named support, its exact 210-entry residual, its
Frobenius score, support size, and residual hash.

The complete exchange scan uses an independent collision-free encoding

```text
code(a) = sum_e a_e * 257^e.
```

Every outer-product coordinate has absolute value at most 25 and the residual
has absolute value at most two.  In a radius-two comparison, every coordinate
of the difference between an addition sum and its required removal sum has
absolute value at most

```text
4*25 + 2 = 102 < 257.
```

If two codes agree, reduction modulo 257 forces the first difference
coordinate to vanish; division by 257 and induction force all 210 coordinates
to vanish.  Thus code equality is exact on this bounded domain.  All 105 by
2,433 one-exchange choices and all 2,958,528 unordered addition pairs against
all 5,460 unordered removal pairs are covered by the corresponding exact
lookup equations.

The submitted modulo-`2^64` fingerprint is audited separately.  Reduction
modulo `2^64` is linear, so exact equality necessarily gives equal
fingerprints.  The submitted code constructs every required removal key,
queries every addition choice, and checks all 210 entries for every matching
key.  A collision can add a candidate but cannot hide a repair.  The verifier
reconstructs the SplitMix64 coefficients and replays the complete scan.

### Restricted cap and A4 transfer

The verifier counts the 1,196 canonical lines whose maximum absolute
coordinate is at most one.  Each contributes at most one to any diagonal
moment, whereas zero-based coordinate one of `21*T20^-1` is 266.  A
105-line selection entirely inside this cap can contribute at most 105.
Only that restricted domain is excluded.

For the complement block, the verifier uses the frozen premises

```text
B_U = U Q_U = I,                 Q_U = X_U^T W_U X_U,
M_U = X_U U X_U^T,              A4_U = M_U W_U M_U.
```

It checks the exact substitution

```text
A4_U = X_U U Q_U U X_U^T = X_U U X_U^T = M_U.
```

All 126 complement rows therefore have A4 diagonal four.  From the frozen
global A4 trace 1,260 and 84 global excess units, the complement trace is 504
and the T20 trace is 756, equal to `4*(105+84)`.

The conditional T20 row table is also checked.  From
`trace(B_A)=36` and a per-row cubic contribution `60-6c_i`, the verifier
derives `sum_i c_i=1044` and recomputes the directed aggregate counts.

## Veto conditions

Any of the following forces `VETO`:

- a committed byte or manifest mismatch;
- a shell discrepancy in either exact basis;
- a missing or extra canonical line;
- any pair, residue, or degree-count discrepancy;
- GF(2) inconsistency or rank mismatch;
- a rational weight outside `[0,1]`, an incorrect sum, or any failed moment;
- an exact one- or two-exchange repair;
- a defect in the fingerprint coverage or full-vector collision check;
- failure of the cap-one or A4 transfer arithmetic;
- any promotion of solver telemetry or a restricted nonhit to a global claim.

No silent repair of the construction package is permitted.
