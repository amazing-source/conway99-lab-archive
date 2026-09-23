# Wave 43 all-rank-33-lifts verifier

Role: verifier  
Claim label: `VERIFIED_SCOPED`  
Frozen commit: `e28f90464d00b98d37672b0b2b23dba15399a6f2`

The clean-room implementation imports no discovery helper. It independently
enumerated all 4,050 normalized quotient forms, recovered canonical form
`1446`, checked all `2^18` endpoint masks, and used dense batched elimination
over `F7`. It reproduced 37,378 triangle-free masks and exactly 264 masks of
`K39` rank 33, including the complete ordered mask stream.

For all 264 masks it independently reconstructed the forced Gram matrix,
component and fibre facts, Cauchy equalities, three-dimensional rational
kernel certificate, four-cycle count, and every one of the 216,000 six-set
pair triples. Every full per-mask record matches the discovery export.

Publication recommendation: publish as `VERIFIED_SCOPED`, conditional on
`n3=4158`, `r3=12`, all edges having type `222`, and the canonical rank-33
lift lane. Every mask survives; the result supplies no simultaneous `B`,
compatible `H`, endpoint exclusion, strict upper bound, graph, or Conway-99
solution. The five census rows are numerical classes only, and no
completed-graph automorphism is assumed.

The discovery result's live SHA-256 is `31e2e5d7...`; its run report contains
a stale output hash. Integration should bind the live file and correct the
metadata without altering the mathematical result.
