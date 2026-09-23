# Wave 120 adversarial verification report

Claim label: `VERIFIED_WITH_CLARIFICATION`.

## Frozen evidence

The Wave120 discovery manifest hashes to
`e2e35519158556a1810affdee4bc148a333ee95a63557ea1a1e687dfcd883017`,
and all ten entries match. The sealed Wave96 verifier package, hash
`8b3f9f90de931dc152ccf1b9e0705409492a6c5eb5246643ddce55aad8afe6e9`,
is used for the norm-20 classification. The sealed Wave112 verifier
package supplies the fixed-C4 outside partition.

No discovery code is imported.

## Projector and integer sharpening: PASS

Independent rational inversion of the C4 principal block gives

```text
s^T E[C,C]^-1 s = 28/5,
(2s)^T E[C,C]^-1 (2s) = 112/5.
```

The second number is an exact real affine minimum, not an integrality
claim.

For `z_C=r(1,-1,1,-1)`, each positive anchor needs outside signed sum
`-2r`. Its negative outside mass is therefore at least `2r`. The two
positive anchors have no common outside neighbour because their two
common neighbours are already the negative C4 anchors (`mu=2`). They
force total outside negative mass at least `4r`; the negative anchors
symmetrically force positive mass at least `4r`. Since integer energy
dominates L1 mass,

```text
||z||^2 >= 4r^2+8r.
```

At `r=2` this is `32`. Equality is exhibited only in the local anchor
relaxation; existence of a full norm-32 integer eigenvector is `UNKNOWN`.

## Six pairwise intervals: PASS

For distinct same-oriented integer eigenvectors of norms `a,b`, the sum
bound and the nonzero lattice minimum give

```text
a+b+2k >= 32,     a+b-2k >= 14.
```

Exact integer arithmetic produces:

```text
(16,16):  0..9
(16,18): -1..10
(16,20): -2..11
(18,18): -2..11
(18,20): -3..12
(20,20): -4..13
```

The imported norm-20 unit-profile statement is taken from the verified
Wave96 verifier package. Wave120's earlier "pending" wording is therefore
superseded, not a mathematical defect.

## Forty-record formal witness: PASS AS A RELAXATION

All forty records are distinct. Each has eight positive and eight negative
units. The six outside pools realize the verified `20,20,51` singleton
partition, while the four one-P-and-one-N vertices are explicitly unused.
The ambient binary length is therefore `4+91+4=99`.

Every record selects exactly two vertices from each listed pool. Direct
substitution checks the four anchor equations. Across all 780 record
pairs the outside overlap histogram is

```text
q:      0   1   2   3   4   5
pairs: 92 230 222 157  62  17
```

This reproduces difference norms `24,22,20,18,16,14`; all classified
rows are balanced signed-unit differences. The binary supports have
weight 16 and minimum distance 14.

Every outside coordinate has one globally fixed sign across the family.
For any subset of `r` records, if `m_v` is its multiplicity at an outside
coordinate, then

```text
sum_v m_v^2 >= sum_v m_v = 12r.
```

Together with the four anchors this proves the stronger formal-support
bound `4r^2+12r` for every positive subset, hence the required
`4r^2+8r` bound. The full forty-record sum has norm `9836`, versus the
required `6720`.

After subtracting the common interpolant, multiply the residual Gram by
five. It has diagonal `52` and off-diagonal `5q-8`. A clean-room
fraction-free Bareiss elimination finds all forty leading principal
determinants strictly positive. By Sylvester's criterion it is positive
definite and has exact rank 40.

## Evidence boundary

The signed records and the abstract residual Gram share the advertised
pair data, but this does not make the records integer `-4` eigenvectors.
The 95 outside eigen-equations are absent. The abstract residual
realization need not retain the signed unit coordinates, and the binary
supports are not shown to lie in a target graph kernel code. No single
common adjacency matrix is encoded.

Accordingly, the size-40 object is a valid null control against the
scoped pairwise Gram/spherical and binary constant-weight/minimum-distance
routes. It is not a graph construction.

Caps 25 and 24, ranks 28 and 30, Conway-99, and literature novelty remain
`UNKNOWN`.
