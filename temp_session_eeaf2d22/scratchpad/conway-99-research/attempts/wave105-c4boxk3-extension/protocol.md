# Wave 105 protocol: `C4 box K3` extension

## Frozen scope

Conditional on a hypothetical `srg(99,14,1,2)` containing the induced
12-vertex parity-cancellation motif `C4 box K3`, derive and test the complete
87-vertex outside extension equations.

No automorphism of the target graph is assumed. Permuting outside vertices
with identical motif neighborhoods is an encoding symmetry only.

## Gates

1. Derive the outside-to-motif incidence multiset from exact pair codegrees.
2. Reconstruct every linear block equation and aggregate second moment.
3. Check all six induced/bipartite type degree sequences exactly.
4. Encode the full outside common-neighbor equations.
5. Accept a SAT result only after direct replay of
   `A^2=12I-A+2J`.
6. Treat a timeout or an uncertified solver UNSAT result as `UNKNOWN`.

The process refuses to build the full SAT instance below 20% free physical
memory.
