# Independent verifier request

Please treat every Wave 51 statement as discovery work. Do not reuse the
discovery code as the sole verification implementation.

## Required clean-room checks

1. Re-derive from a hypothetical `srg(99,14,1,2)` that the 231 graph
   triangles give an 18-regular intersection graph with local graph `3K6`
   and spectrum `18^1,7^54,0^44,(-3)^132`.
2. Re-prove that a disjoint triangle pair has `q` cross edges forming a
   matching, and that `q=3` is exactly an induced triangular prism.
3. At prism count zero, re-derive the row distribution `(32,144,36)` for
   `q=0,1,2`.
4. Reconstruct `S=K^2-17I-4K-J=B-D`, its valencies and spectrum, and
   `S^2+13S-68I=0`. Confirm independently that `4I-S=21E_0`.
5. Parse the displayed normalized tensor independently. Check nonnegativity,
   all five row and column margins, `K^2`, `KS`, `SK`, `S^2`, the `3K6`
   row, divisibility, and all 125 global balance equations.
6. Independently evaluate the association-algebra diagnostic, including the
   first failure `81 != 153`.
7. Confirm the logical boundary: an aggregate feasible tensor is neither a
   graph nor an association scheme and does not settle the endpoint.

## Requested labels

```text
exact tensor arithmetic: VERIFIED or REFUTED
interpretation as aggregate positive control: VERIFIED or REFUTED
endpoint: UNKNOWN
Conway-99: UNKNOWN
novelty: UNKNOWN
```

Please record exact input and output hashes and preserve any discrepancy.
