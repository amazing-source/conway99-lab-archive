# Wave 30 retained construction failures and scope limits

These routes are preserved to prevent a later run from treating a cutoff or
restricted nonhit as a theorem.  None is used to claim nonexistence.

## 1. The neighbor route is a construction, not a classification

The successful path searches binary representatives in a succession of
two-neighbor classes and greedily prefers a lower exact root count.  It found
the displayed chain

```text
240 -> 112 -> 48 -> 20 -> 6 -> 0 roots.
```

The five accepted supports are replayed exhaustively once frozen, but the
discovery search did not enumerate the full two-neighbor graph, quotient by
isometry, or prove that the final class is unique.  No target automorphism was
assumed.  Failed random supports are not retained as nonexistence evidence.

An early seven-round prototype did not reduce the basis after each neighbor.
Its exact ellipsoid enumeration became slow and the process was stopped after
roughly four minutes.  That timeout says nothing about any lattice class.  The
successful replay instead applies a checked unimodular exact-LLL basis change
after every neighbor.

## 2. Shell size is not a marked frame

The final `T20` has exactly `5076` norm-four vectors, or `2538` antipodal
lines.  This exceeds the elementary availability requirement for the `105`
rows forced on a rank-20 block.  It does not select those rows or prove

```text
X_A^T X_A = 21 T20^(-1).
```

It also does not enforce the off-diagonal alphabet, row histograms, cubic
moments, or Schur-square origin.

As an explicitly restricted discovery scout, one Boolean variable was assigned
to each of the `2538` antipodal lines and the `210` upper-triangular
second-moment equations were sent to Z3 `5.0.0.0`.  Model construction took
about 21 seconds; the solver returned `unknown` at its 30-second timeout.
The result is neither a witness nor evidence against a frame.  Z3 was used
from a disposable temporary installation and is not a replay dependency.

Orienting any hypothetical selected lines to make every distinct inner product
belong to `{0,1,-1,-2}` is a separate unsolved constraint.

## 3. No determinant-five `Q` or endpoint `B`

The scalar spectrum

```text
spec(B_A) = 5^1, 3^6, 1^13
```

has the necessary rank-20 determinant and trace, but no integral lattice
endomorphism with that spectrum was constructed.  In particular, this lane
does not produce an even determinant-five `Q_A`, `B_A=T20 Q_A`, or
`B_A=I mod 2`.  The rank-44 output is therefore a bare `S/G` candidate only.

## 4. The Leech norm-four coefficient was not re-enumerated

The embedded `LAMBDA24` matrix is checked exactly for symmetry, evenness,
positive definiteness, determinant one, even integral inverse, and absence of
norm-two vectors.  A generic exact enumeration through norm four was stopped
after four minutes.  The catalogue's kissing number and the standard modular
theta derivation are not used in the candidate certificate.

Rootlessness of the rank-44 direct sum needs only the two completed norm-two
enumerations, not the uncompleted Leech norm-four enumeration.

## 5. No isometry classification

The output gives a new explicit route and the literal decomposition

```text
T20 orthogonal_sum LAMBDA24
```

rather than the frozen `K12 orthogonal_sum LAMBDA(F)` construction.  This lane
does not classify rootless determinant-729 forms or prove an isometry
classification distinguishing every possible presentation.

## 6. Global status is unchanged

No primitive `Z^231` embedding, complete projector frame, `M`, `W`, `Q`,
`B`, graph, or Conway configuration was constructed.  The failure to bridge
any one of these layers is not an exclusion of `h=729` or `n3=708`.
