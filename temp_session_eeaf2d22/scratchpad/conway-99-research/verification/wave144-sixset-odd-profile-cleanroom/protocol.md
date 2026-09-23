# Wave144 clean-room verification protocol

## Frozen target

The discovery manifest was copied byte-for-byte into
`discovery-manifest.frozen.sha256` before the discovery implementation or
results were read. Its SHA-256 digest is
`b5369353ac6959b0662e3f424cf80e48094ac6bcdb79572bf604632c45509436`.
The verifier checks both the frozen and live manifest bytes and every listed
artifact before checking any mathematical claim.

## Independent route

1. Regenerate every locally admissible unlabeled graph on four, five, and six
   vertices using fresh relabeling, canonicalization, and orbit code.
2. Align the resulting classes to the source numbering by independently
   constructing all vertex-deletion decks. The Wave21 module is loaded only
   as a frozen container for the transcribed deck-table constants; none of its
   algorithms is called.
3. For each of the 62 aligned six-vertex classes, exhaust every multiplicity
   assignment to cells of size at least three. Pair cells, singleton cells,
   and the empty cell are then forced by the exact equations. Retain and replay
   one independently produced witness for every attained weight.
4. Compare all support sets and graph metadata against the sealed discovery
   payload. Recheck the class-36 weight-68 gap with the high cells traversed in
   the opposite order.
5. Replay every published sparse local witness using direct 64-cell sums.
   Require its exact key set to equal the union of the aggregate cells and the
   four forced singleton-support cells.
6. Replay the endpoint aggregate with exact integers and rational arithmetic:
   all 62 class marginals, total six-set count, reciprocity moments for
   `t=0,1,2,3`, and the signed `S_6` identity.
7. Integrity-check the existing same-author verifier package, but do not use
   it to establish the clean-room verdict.

## Status discipline

`PASS_NULL_BOUNDARY` means only that the stated six-set marginal relaxation
has an exact integer feasible point at the already imported cap `n3=4158`.
It does not improve that cap and does not establish a graph.

The missing consistency condition is exact: the certificate chooses a valid
local `z_P` distribution for each six-vertex class/weight cell separately, but
does not assign those choices to all actual six-subsets of one common
99-vertex vertex set. Consequently it does not prove that witnesses belonging
to overlapping six-subsets identify the same outside vertices or agree on
their shared incidence and adjacency data.
