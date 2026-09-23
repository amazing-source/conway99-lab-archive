# Wave197 clean-room protocol

This protocol was frozen before opening either sealed Wave197 source.

1. Use only the sealed Wave180, Wave194, Wave195, and Wave196 verifier
   results and `srg(99,14,1,2)`.
2. Let `H` be the undirected label union of the selected exact-three flags.
   Prove that a fixed orientation `x->y` lies in at most five selected
   flags: its two-block type fixes two members of `A_x(T)`, leaving only
   five choices for the third block, and fixed-center `A`-injectivity gives
   at most one flag for each choice.
3. Deduce degree at most ten for each undirected label in the selected flag
   hypergraph.
4. Audit simplicity carefully.  Wave180 leaves exactly two companion
   circuits for one flag; inclusion-minimality of the selected cover
   forbids selecting both, so selected exact-three circuits give distinct
   flags.
5. Prove that every one of the `p3` private labels has degree exactly one
   in the selected flag hypergraph.  Sum degrees to derive
   `S10=10H-9p3-3n3>=0`.
6. Reuse the verified oriented-label injection and Wave196 local cap to
   derive `SH=6C/7-H-a3-b3>=0`.
7. Reuse the Wave196 flag cap to derive
   `SF=13C/42-n3-h-g>=0`.
8. Retain the independently verified raw capacity
   `R3=3h-a3-b3>=0` and all Wave194 bookkeeping slacks.
9. Reconstruct the exact coefficient certificate at target
   `2131C/1260=70323/10`, verify integer rounding to `Q>=7033`, and check
   projective/scalar totals after adding the 693 edge-isolated circuits.
10. Build an independent integer arithmetic control and label it as
    accounting only.
11. Quarantine unrelated candidate rows and preserve the endpoint and
    Conway `UNKNOWN` boundary.
12. Freeze the independent mathematical result before opening Wave197
    proof A or hostile proof B.

No graph, code, cover, SAT, LP, configuration, construction, family,
enumeration, isomorphism, or brute-force search is permitted in the sealed
derivation.  Exact coefficient and arithmetic-row evaluation are allowed.
