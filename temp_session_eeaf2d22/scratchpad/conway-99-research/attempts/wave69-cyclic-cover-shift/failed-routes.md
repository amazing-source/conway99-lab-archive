# Failed and bounded routes

## Direct nonlinear SMT

A direct Z3 encoding used 45 symmetric integer variables, row sums, even
diagonal entries, and every entry of

```text
Q^2 + Q = 12 I + 22 J.
```

It did not return a status within 120 seconds. This run is `UNKNOWN`; it is not
evidence of unsatisfiability. The tailored row-exhaustion algorithm replaced
it.

## Quotient polynomial without rational representation theory

The quotient polynomial permits eigenvalues `14,3,-4`, but on its own it does
not force multiplicities `1,4,4`: a formal `1,6,2` split is not excluded by
trace parity and nonnegative diagonal entries alone. The full
semiregular-`C_11` action repairs this by forcing nonfixed rational
representation dimensions to be multiples of ten.

## Symmetry pruning as a sole certificate

The canonical search is fast, but a bug in a canonical-augmentation rule could
in principle remove a valid orbit. For that reason, the primary exhaustive
result also runs an `unpruned` enumeration that uses no within-diagonal
canonical pruning. Only the harmless convention of sorting the diagonal
remains.

## Voltage/difference-set SAT

No voltage SAT instance was run after the quotient search produced an empty
candidate set. This is not an inconclusive SAT nonhit: any block-circulant
`Z_11` lift would have a zero-frequency quotient, so quotient nonexistence
logically empties the lift lane.

## Cayley versus arbitrary graphs

The Fourier contradiction uses the Cayley hypothesis. It does not apply to a
general graph merely because the graph has 99 vertices. Likewise, all groups
of order 99 being abelian does not imply that every 99-vertex graph is Cayley.

The fixed-point lemma plus quotient search does exclude every order-11
automorphism and therefore every vertex-transitive target. It still does not
exclude an asymmetric target or a target whose automorphism group has order
not divisible by 11.

## Novelty and unrestricted status

No literature novelty claim is made. The unrestricted
`srg(99,14,1,2)`/Conway-99 target remains `UNKNOWN`.
