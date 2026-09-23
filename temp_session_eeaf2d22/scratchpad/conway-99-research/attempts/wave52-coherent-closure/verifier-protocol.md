# Independent verifier protocol

The verifier should not import `coherent_closure.py`.

1. Re-derive from `srg(99,14,1,2)` and prism-freeness that the eighteen
   root-neighbor triangles induce `3K6` and that each sector-pair `B` graph is
   a simple bipartite 2-factor.
2. Reconstruct the 19-node partial structure and the 163-node incidence
   template from the prose specification, not the discovery matrices.
3. Implement 2-WL independently, including ordered-pair direction, diagonal
   node types, and multiset multiplicities.
4. Check the claimed color trajectories `6` and `26 -> ... -> 47`, and
   reconstruct all stable intersection numbers.
5. Check diagonal class sizes `(1,18)` and `(1,18,36,108)`.
6. Reconstruct all four simple bipartite 2-factor cycle types and all 64
   canonical profile triples. Verify relation caps for every completion.
7. Confirm at least two completed closures have different invariant
   intersection fingerprints. Do not interpret the 64 examples as exhaustive
   joint labelled completion coverage.
8. Attack the implementation by deleting a `B` edge, duplicating an endpoint,
   changing a cap incidence, and weakening the memory guard.
9. Verify that no output claims a graph, endpoint exclusion, improved `n3`
   bound, global association scheme, or completed-graph automorphism.

