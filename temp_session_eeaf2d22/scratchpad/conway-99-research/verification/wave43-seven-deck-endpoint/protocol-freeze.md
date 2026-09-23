# Wave 43 seven-deck verifier protocol

Frozen before discovery inspection: 2026-07-27T16:16:24Z

The discovery package was treated as opaque while its filenames and SHA-256
hashes were recorded in `input-freeze.sha256`. No discovery source, result,
proof, test, or protocol content was opened before this file was written.

## Scoped claim supplied for verification

At the conditional endpoint values

```text
n3 = 4158
h11 = 16632,
```

the unrooted order-seven deck/count relaxation is claimed to have:

- 208 locally admissible unlabeled seven-vertex graph classes;
- 62 locally admissible six-vertex deletion rows;
- 19 endpoint Hamiltonian/count formula constraints; and
- an exact nonnegative integer solution supported on 99 seven-vertex classes.

The required verdict is only whether this finite unrooted order-seven
constraint system is feasible. Feasibility is not a graph, an endpoint
construction, or evidence for target existence.

## Independent method frozen before comparison

1. Obtain all unlabeled graphs on six and seven vertices from an independent
   catalogue path. Canonicalize every graph under all vertex permutations,
   verify unique canonical codes, compute automorphism groups, and confirm
   orbit-size sums `2^15` and `2^21`; this checks catalogue completeness
   against the full labelled graph universes.
2. Derive local SRG admissibility directly:
   every adjacent pair has at most one common neighbor and every nonadjacent
   pair has at most two common neighbors.
3. Filter the independent catalogues and record complete canonical mask
   streams. For every admissible seven-class, delete each of its seven
   vertices, canonicalize the resulting six-graph, and build the exact
   deletion multiplicity matrix from scratch.
4. Independently implement all graph invariants named by the frozen
   19-formula specification after that specification is opened. Evaluate
   every formula by exact integer arithmetic at `n3=4158`, `h11=16632`.
5. Reconstruct the proposed 99-support solution only from its public
   machine-readable coefficient list. Reject duplicate/noncanonical classes,
   negative or nonintegral coefficients, and any prism-containing class.
6. Verify every total, formula row, and six-to-seven deletion equation by
   recomputation from canonical graphs, not by trusting stored row values.
7. Add positive controls from small complete labelled graph universes and
   hostile mutations of a coefficient, deletion multiplicity, formula value,
   local-admissibility condition, and prism-zero condition.
8. Freeze the independent result before opening discovery implementation
   details. Compare exact counts, streams, row values, support, and residuals
   mechanically only afterward.

## Resource and status rules

- One foreground Python process; no background workers.
- Sample physical memory and abort before free memory falls below 15%.
- No discovery implementation import at any stage.
- Promote only exact feasibility of this specified unrooted relaxation.
- Do not infer a `99`-vertex graph, compatible lower decks, simultaneous
  rooted realizability, endpoint existence, a strict upper bound, Conway-99
  existence, novelty, or priority.

