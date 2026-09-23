# Wave 179: global exact-transversal circuit bound

Status: `DERIVED_PENDING_VERIFICATION`.

Wave 178 proved that the 693 edge-local relations have distinct circuit
supports.  This wave incorporates all 4,851 unordered pairs of original
vertices.

Regard a short cross-star circuit support as a family of graph triangles.
Any vertex pair that indexes it is an exact two-transversal: every support
triangle contains exactly one endpoint, and both endpoints occur.  A direct
`lambda=1` argument proves that one circuit support can serve at most three
vertex pairs.  Wave 178 balance further makes every chosen edge circuit
globally isolated: it cannot also serve a nonedge.  Consequently, in the
conditional rank-11 endpoint model,

```text
at least 2079 distinct projective dual circuits of size 4..9,
B_4+B_5+B_6+B_7+B_8+B_9 >= 4158.
```

The independently verified Wave 178 refinement remains simultaneous:

```text
at least 693 edge-unique projective circuits of size 4, 6, or 8,
B_4+B_6+B_8 >= 1386.
```

The proof is incidence/matroid theory, not a construction search.  It does
not exclude the endpoint: current code bounds do not consume the exact
triangle-transversal localization strongly enough.  The rank-11 branch,
strict `n3` improvement, and Conway-99 remain `UNKNOWN`.
