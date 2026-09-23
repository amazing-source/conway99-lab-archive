# Verification protocol

## Independence and chain of custody

1. Wait for the discovery agent to declare the Wave 124 package sealed.
2. Hash every discovery file without reading its contents.
3. Freeze those hashes in `discovery-inventory-preinspection.tsv`.
4. Independently reconstruct the scalar marking, coefficient semantics,
   Fricke transform, residue DFT, tight frame, and finite moment null before
   source inspection.
5. Freeze that first reconstruction in `precomparison.sha256`.
6. Only then inspect the discovery package.
7. Reconstruct the full-level Jacobi basis with a separate q^3
   implementation and compare exact rational coordinates.
8. Replay both discovery and verifier tests and confirm that the original
   12-file inventory is unchanged.

No discovery module is imported by either independent implementation.

## Frozen inputs

- Wave 124 discovery manifest:
  `fbdaa5071229c921fdf652a91eaa895f57ce1d31f726cb4f465f0356a6dfec55`
- Wave 71 verifier manifest:
  `0eede2ebc625534360dda3f8e62456e582f5184fd18d3820dd44748de95a5237`
- Wave 86 verifier manifest:
  `cbfafc03db11ad7f103e532e0f5e0b2e85ff6b568ad327b947a2d394a1d1dfa2`
- Wave 96 verifier manifest:
  `8b3f9f90de931dc152ccf1b9e0705409492a6c5eb5246643ddce55aad8afe6e9`
- Wave 101 verifier manifest:
  `79fd0331a936761f2394d58f835df80e41ad855cdf88660a2ccfd5841c5d7aba`
- Wave 112 verifier manifest:
  `56845bcdf221c16ec46d40c630a8cdb3d63beed1314dd2683e17bf5c929ff024`
- Wave 116 verifier manifest:
  `e44afa352f51c192d6c5ac8584ccd6334dd69a3d11856f4ac0254283829bbfb8`

## Claim rules

- `VERIFIED` applies only to the conditional identities reproduced here.
- The standard weak-Jacobi-ring structure theorem is used, not reproved.
- Full-level Jacobi forms are not claimed to span the whole
  `Gamma_0(7)` space.
- Signed null directions are not positive theta series.
- The support-clean degree-eight threshold first observed in this
  verification is retained as `CANDIDATE`.
- Rank 28, rank 30, Conway-99, and novelty remain `UNKNOWN`.
