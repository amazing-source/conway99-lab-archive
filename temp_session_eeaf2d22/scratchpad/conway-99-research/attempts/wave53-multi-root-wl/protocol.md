# Wave 53 discovery protocol

1. Freeze the endpoint relation order `I,K,D,C,B`, the one-root `3K6`
   neighborhood, and the exact-two `B` cap for every petal and opposite
   sector.
2. Couple two roots separately in relations `K`, `B`, `C`, and `D`. Identify
   exactly their forced common `K`-neighbor triangles: respectively
   `5,2,1,0`.
3. For `B`, place the two cross edges at distinct endpoints of both roots.
   Their two common `K`-neighbor triangles share one candidate variable, and
   that variable is forced to `B`.
4. Merge candidate nodes only when they represent the same unordered pair of
   actual triangle nodes. Retain every unresolved `B/C` choice and all 72
   exact-two cap nodes.
5. Do not select a `B/C` completion before refinement. Root-sector coordinates
   are names, not automorphisms of a completed graph.
6. Run exact 2-WL to stability on each expanded forced CSP and reconstruct all
   nonzero integer intersection parameters.
7. Run exact folklore 3-WL to stability on the smallest typed two-root
   triangle core.
8. Only after both closures are fixed, emit a deterministic integral cap
   assignment as a positive local control. Do not treat it as a graph.
9. Reject malformed overlaps, missing forced truths, broken caps, unstable
   partitions, nonexact replays, and any endpoint status promotion.
10. Preserve the discovery label `DERIVED`; the prism-free endpoint and
    Conway-99 remain `UNKNOWN`.
