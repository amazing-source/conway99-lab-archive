# Wave 178: edge-to-circuit injection

Status: `DERIVED_PENDING_VERIFICATION`.

This wave closes the multiplicity caveat left by Wave 177.  In the
conditional rank-11 endpoint model, every one of the 693 graph edges forces
a different projective circuit of the centered triangle-block code:

```text
693 distinct projective circuits of size 4, 6, or 8,
B_4+B_6+B_8 >= 1386.
```

The injection is incidence-theoretic.  A nonzero relation supported in the
two outer stars of an edge cannot be supported in the outer stars of any
second edge: shared-edge-endpoint and disjoint-edge cases both contradict
the strongly regular parameter `lambda=1`.

A tiny four-matrix calculation then uses the four possible cycle types of
an adjacent star pair.  Every short outer Gram-kernel word has even weight,
uses equally many columns from the two stars, and has equally many
coefficients `1` and `-1`.  This calculation enumerates at most `3^5=243`
vectors in a locally derived kernel; it searches no graph, code,
configuration, SAT instance, or isomorphism class.

This is a genuine global strengthening, but not an endpoint exclusion.
Standard Hamming, circuit-elimination, critical-exponent, subspace-EKR, and
sunflower bounds do not turn the new circuit count into a contradiction.
The Conway-99 endpoint and the rank-11 branch remain `UNKNOWN`.
