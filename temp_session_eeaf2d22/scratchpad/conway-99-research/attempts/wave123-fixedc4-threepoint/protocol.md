# Wave 123 protocol

Date frozen: 2026-07-28.

Role: proof A / construction discovery.

## Frozen inputs

- Wave120 discovery manifest:
  `e2e35519158556a1810affdee4bc148a333ee95a63557ea1a1e687dfcd883017`.
- Verified Wave96 manifest:
  `8b3f9f90de931dc152ccf1b9e0705409492a6c5eb5246643ddce55aad8afe6e9`.
- Verified Wave112 manifest:
  `56845bcdf221c16ec46d40c630a8cdb3d63beed1314dd2683e17bf5c929ff024`.
- Wave120 witness:
  `3569eaa48ec3e99ab988f943492c103f67889c8fadf9a2a15edeac9586220183`.

Assume a hypothetical `srg(99,14,1,2)` only when deriving necessary
eigenspace/projector conditions.  Fix a labelled induced C4 and the
orientation `(1,-1,1,-1)`.  Assume no graph automorphism.

## Questions

1. Does the forty-record Wave120 support realization fit in one `-4`
   eigenspace?
2. Can a 26-record subset pass the coordinate leverage condition?
3. Does such a subset pass exact rooted three-point support-code PSD
   constraints?
4. Can its span projector be completed even at every graph-valued
   two-by-two principal minor?

## Gates

- The Wave120 records are formal supports, not eigenvectors.
- Refuting one coordinate realization does not refute its abstract Gram.
- A code-only three-point witness is not a graph-valued projector
  completion.
- A nonexhaustive subset search cannot prove a cap.
- Solver or floating search output is not a certificate; promoted finite
  rows must be replayed with exact rational arithmetic.
- Discovery cannot verify itself.
