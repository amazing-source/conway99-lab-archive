# Wave 69 clean-room verification protocol

## Frozen claim boundary

This package verifies only the following claims for a hypothetical
`srg(99,14,1,2)`:

1. a fixed-point-free automorphism of order 11 gives a symmetric nonnegative
   integer `9 x 9` quotient satisfying the stated exact equations;
2. no such quotient exists;
3. consequently no semiregular order-11 action or cyclic `Z_11` lift exists;
4. independently, no Cayley realization on a group of order 99 exists;
5. after importing the separately `VERIFIED` Wave 72 fixed-point theorem, no
   order-11 automorphism and no vertex-transitive realization exists.

No automorphism is assumed for the unrestricted graph.  Conway-99 remains
`UNKNOWN`.

## Independence

- The complete 17-file discovery directory was SHA-256 inventoried before any
  discovery prose, code, or result was inspected.
- `independent_verify.py` imports no discovery module and executes no discovery
  program.
- The verifier reconstructs the rational representation step, row shapes,
  diagonal cases, and both search trees.
- Discovery JSON is read only after independent result generation, solely to
  compare exact mathematical fields, branch telemetry, and transcript hashes.
- The label-complete tree is the certificate.  Canonical augmentation is only
  a cross-check and cannot certify nonexistence by itself.

## Symmetry policy

The proof tree sorts the nine diagonal entries.  This is lossless because any
quotient can be conjugated by the same permutation on rows and columns.  No
ordering is imposed among equal-diagonal vertices in the label-complete tree.
All their labeled assignments are enumerated.

## Imported prerequisite

Only this theorem is imported from Wave 72:

> Every permutation automorphism of exact order 11 of a hypothetical
> `srg(99,14,1,2)` is fixed-point-free.

The imported result has label `VERIFIED`; its independent result and verifier
run report are checksum-pinned in this package's run report.  The Wave 69
discovery version of the fixed-point proof is not used as certification.

## Promotion policy

- `VERIFIED` applies to the restricted quotient obstruction, Cayley
  obstruction, and the combined order-11/vertex-transitive consequences.
- Literature novelty and priority remain `UNKNOWN`.
- Asymmetric targets and targets whose automorphism group has no element of
  order 11 remain possible.
- The unrestricted conjecture is not promoted.
