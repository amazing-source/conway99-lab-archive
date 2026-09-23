# Wave 109 independent-verification protocol

Role: verifier.

The sealed discovery input is
`attempts/wave109-c4boxk3-local-projector/package-manifest.sha256`, with
SHA-256
`6d54d48dbb6b1ffd3f7da845792fc12ee490471c02cc8137ebd1b03c21f5347e`.
All discovery files were hashed into `input-freeze.sha256` before their
claims or implementation were inspected.

The verifier must:

1. reconstruct `C4` Cartesian `K3` and the forced incidence multiset from
   the SRG degree and common-neighbor equations;
2. search independently for a unimodular full-rank minor of `Q=[one P]`,
   then construct a complete integral basis of `ker(Q^T)`;
3. compute both Gram determinants exactly and classify the resulting
   74-dimensional form over `F_7` with the correct even-dimensional sign
   convention;
4. express the conditional block equations as `DQ=QE`, verify invariance,
   and expand the global SRG polynomial to obtain `B^2=7B`;
5. use an independently computed Schur complement on
   `span(Q)` to verify the rational dimensions and every imported mod-seven
   rank row;
6. rederive the Smith, index, and determinant formulas from the inclusions
   `7U subset B Lambda subset U`;
7. test Witt capacity, residual orthogonal type, and formula consistency for
   an additional obstruction;
8. rerun discovery only after the independent computation passes.

The verifier may certify only this conditional algebra. Motif occurrence,
the existence or nonexistence of a full extension, Conway-99, and literature
novelty remain outside scope and must remain `UNKNOWN`.
