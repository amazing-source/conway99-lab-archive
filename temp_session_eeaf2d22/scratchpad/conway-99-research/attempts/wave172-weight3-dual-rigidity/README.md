# Wave 172: weight-three dual rigidity

Status: `VERIFIED_WITH_SCOPE` by an independent clean derivation.

This checkpoint continues the non-search coding-theory lane from Wave 171.
Assume the prism-free endpoint and write

```text
D=C+J over F_3,
W=row(D).
```

For any weight-three word in `W^perp=ker(D)`, the three nonzero coefficients
must be equal.  A mixed sign pattern such as `(1,1,-1)` contradicts the exact
integer reflection identity `C^2=441I`.

Moreover, the support blocks are three pairwise disjoint triangles with no
cross edges, hence induce `3K3`.  After scaling the dual word to coefficients
`(1,1,1)`, the three corresponding rows of `D` have the exact joint coordinate
distribution

```text
000:                       15
111:                      144
222:                       18
permutations of 012:       54
```

where the last line is an aggregate over the six permutations.

Equivalently, the complete dual weight enumerator has no weight-three terms
of symbol composition `(2,1)` or `(1,2)`.  This is information discarded by
the ordinary Wave 54 enumerator.

The result does not prove that a weight-three dual word exists or does not
exist, and it does not exclude the endpoint.  Conway-99 remains `UNKNOWN`.
