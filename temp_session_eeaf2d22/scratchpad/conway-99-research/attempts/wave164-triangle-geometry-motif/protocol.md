# Wave164 protocol

## Scope

Compare the induced cube and Wagner counts through the point--triangle
incidence geometry of a hypothetical `srg(99,14,1,2)`.

## Required checks

1. Construct the cube and Wagner graphs independently from named definitions.
2. Verify that each is triangle-free, cubic, and has eight vertices and
   twelve edges.
3. Derive `M_H=12I-H+2J-H^2` directly from the frozen SRG identity.
4. Construct a complete binary `8 by 91` factor `B` and check `B B^T=M_H`.
5. Check that each column support induces maximum degree at most one in `H`.
6. Reconstruct the common `12,32,187` triangle-incidence profile.
7. Enumerate induced 5-cycles in the cube and Wagner graph.
8. Verify the fixed-`C5` matrix `11I+J` and its explicit binary factor.

## Evidence separation

- A successful run proves only the displayed finite identities and explicit
  factors.
- Feasibility of a local factor is not feasibility of its 91-vertex outside
  graph.
- No association-scheme closure, automorphism of the target, or uniform
  outside adjacency is assumed.
- The checker is not a verifier of itself.
- Until the checker is run and independently replayed, this package remains
  `DRAFT_UNEXECUTED`.
- Conway-99, the endpoint `n3=4158`, and a strict upper bound remain
  `UNKNOWN`.

