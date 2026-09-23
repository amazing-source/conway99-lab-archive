# Wave 180: conic companions for triple-serving circuits

Status: `DERIVED_PENDING_VERIFICATION`.

Work conditionally at the prism-free endpoint in the smallest surviving
centered rank:

```text
P=0,  n3=4158,  rank_F3(D)=11.
```

Wave 179 showed that a short circuit support can cross-realize at most three
vertex pairs.  This wave classifies the equality case when all three pairs
are nonedges.  Finite-polar star-projector geometry forces the circuit to be
one member of a canonical pair:

```text
a weight-4 plane-conic circuit,
a weight-5 complementary circuit.
```

Both supports cross-realize exactly the same three nonedges.  Applying this
pairing to an inclusion-minimal cover of all 4,158 nonedges improves the
conditional short-circuit bounds to

```text
at least 2,079 nonedge-realizing projective circuits of sizes 4..9,
at least 2,772 projective circuits of sizes 4..9 after the 693 edge circuits,
B_4+B_5+B_6+B_7+B_8+B_9 >= 5,544.
```

The simultaneous Wave 178 edge refinement remains

```text
B_4+B_6+B_8 >= 1,386.
```

The argument is incidence geometry, orthogonal projectors, and a covering
involution.  It performs no graph, code, SAT, configuration, or isomorphism
search.

This is a stronger necessary condition, not a contradiction.  Rank 11, the
endpoint, every strict improvement to `n3<=4158`, and Conway-99 remain
`UNKNOWN`.
