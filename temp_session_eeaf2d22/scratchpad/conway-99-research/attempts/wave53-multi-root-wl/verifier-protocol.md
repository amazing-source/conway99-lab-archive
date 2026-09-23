# Independent verifier protocol

The verifier should recreate the four relation records without importing
discovery output as computational input.

1. Re-derive the common `K`-neighbor counts `5,2,1,0` for root relations
   `K,B,C,D`.
2. Check that disjoint-root cross edges form a matching and independently
   derive the shared forced-true candidate for `B`.
3. Rebuild both rooted `3K6` systems, merge only identical actual triangle
   pairs, and confirm the node counts `319,323,325,326`.
4. Reimplement or independently audit exact 2-WL refinement and the stable
   intersection records. Do not trust stored color identifiers.
5. Reimplement exact folklore 3-WL on the triangle cores and compare partition
   fingerprints only after independent construction.
6. Check every one of the 72 cap equations against each positive control,
   including the shared variable in `B`.
7. Mutate one common-neighbor overlap, remove the forced `B` truth, delete a
   selected control edge, and alter a stored partition hash. Each mutation
   must fail.
8. Confirm that no arbitrary `B/C` completion enters either WL input.
9. Confirm the endpoint and Conway-99 statuses remain `UNKNOWN`.

The discovery CLI supports component replay, but using that code alone is not
independent verification.
