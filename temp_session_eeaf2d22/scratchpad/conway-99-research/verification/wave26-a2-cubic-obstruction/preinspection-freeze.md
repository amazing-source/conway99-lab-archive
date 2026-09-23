# Wave 26 A2 cubic obstruction: preinspection freeze

```yaml
role: verifier
date_utc: 2026-07-23T22:53:12Z
git_commit: NOT_USED_PER_TASK_INSTRUCTION
claim_label: CANDIDATE
scope: >-
  Blind independent verification plan for the conditional claim that a
  231-row projector/Schur realization with scaled-dual form containing an
  orthogonal A2 summand must satisfy tr(A2 Q_AA) >= 18, and that the frozen
  Wave 24 E8^5 orthogonal-sum A2^2 survivor, whose corresponding block is
  Q_AA=A2, violates that necessary condition because tr(A2^2)=10.
inputs:
  verification/2026-07-23-wave20-global-schur-audit.md: 6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3
  verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md: 45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268
  verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md: 958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8
  verification/wave24-n3-708-index/survivor-certificate.json: a217ec7211128f51e684030a7fe8d3c60ac80935f356ba5193dc34d36d4077a2
  verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md: 642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de
method: >-
  Derive the row/tensor factorization from the frozen projector identities,
  enumerate the A2 row projections exactly, derive the signed root-line
  imbalance constraints, and prove the compression trace floor before
  inspecting the submitted Wave 26 candidate.
command: NOT_YET_RUN
outputs:
  verification/wave26-a2-cubic-obstruction/preinspection-freeze.md: SELF_HASH_RECORDED_IN_FINAL_MANIFEST
limitations:
  - No actual 231-by-231 projector matrix exists in the repository.
  - The verification is conditional on the frozen full projector/Schur premises.
  - The exact Wave 26 discovery report and attempt directory were not inspected.
  - This scope cannot exclude every h=9 form or the endpoint n3=708.
```

## Inspection wall

As of the timestamp above, neither of these candidate paths had been opened,
searched, hashed, imported, or executed:

```text
agents/2026-07-23-wave26-a2-cubic-obstruction.md
attempts/wave26-a2-cubic-obstruction/
```

The older public Wave 26 `A2` frame obstruction was visible as prior context
but is not a mathematical input to this cubic verification. The derivation
below is to use only the five hash-frozen audited inputs listed above.

## Independently frozen derivation plan

1. Let `X` be a `231 x 44` integral basis matrix for the primitive projector
   lattice, with row coordinate vectors `x_i`, Gram matrix `G=X^T X`, and
   scaled-dual form `S=21G^-1`. Derive, rather than assume,
   `M=X S X^T`, `G=21S^-1`, and `Q=X^T(M o M)X`.
2. Work first in the full ordered tensor square. For the row-square map
   `R_i=x_i tensor x_i`, prove
   `(M o M)_ij=<R_i,R_j>_(S tensor S)` and hence
   `Q=C^T(S tensor S)C`, where the `a`th column of `C` is
   `sum_i x_ia R_i`. Track every factor of two; do not switch silently to a
   normalized symmetric tensor square.
3. If `S=A2 direct_sum R`, show that
   `tr(A2 Q_AA)` is the squared norm of
   `sum_i a_i tensor x_i tensor x_i` in
   `A2 tensor S tensor S`, where `a_i` is the selected two-coordinate row
   projection. Orthogonal projection to `A2 tensor A2 tensor A2` must give a
   lower bound; explicitly verify that mixed and complement tensor blocks are
   orthogonal, so cross-block terms cannot lower it.
4. Enumerate the integral vectors of `A2=[[2,-1],[-1,2]]` having norm at most
   four. Use row norm four and complement positivity to prove every `a_i` is
   zero or one of the six norm-two roots and that no norm-four `A2` vector
   occurs. Use `sum_i x_i x_i^T=G=21S^-1` to prove exactly 21 nonzero
   `A2` projections.
5. Group the six roots into the three unoriented lines represented by
   `e1`, `e2`, and `e1+e2`. Define signed imbalances `d1,d2,d3`.
   Derive `X^T 1=0` from `M1=0` using full column rank and invertibility,
   then obtain `d1=d2=-d3=t`. Since the total root incidence is 21,
   prove `t` is odd and therefore nonzero.
6. Compute the exact tensor Gram matrix
   `(<r_i,r_j>_A2^3)` and verify that the compressed cubic tensor has norm
   `18t^2`, yielding `tr(A2 Q_AA)>=18`.
7. Attack conventions with explicit controls: transpose the row/column
   presentation; change an integral basis; use both oriented-root choices;
   compare ordered versus normalized symmetric tensors; retain arbitrary
   mixed `A2`/complement components; and drop `M1=0` to see whether the
   claimed floor survives. A dropped-premise counterexample is required if
   `M1=0` is essential.
8. Parse the full frozen Wave 24 certificate independently. Verify its block
   placement, `S_AA=A2`, `Q_AA=A2`, zero cross-block entries, and
   `tr(A2 Q_AA)=10`.
9. Only after the independent checker, tests, and baseline result are fixed,
   inspect the candidate report and attempt directory. Record exact agreement
   and discrepancies without silently repairing the candidate.
