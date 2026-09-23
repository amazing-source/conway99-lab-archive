# Frozen pre-comparison verdict: Wave 13 `n3=45`

```yaml
role: verifier
date_utc: 2026-07-23T08:13:53Z
git_commit: c471801a7adf6852a208b5d5553bcc76a3372d6a
claim_label: VERIFIED
verdict: PASS
scope: conditional exclusion of n3=45 from the frozen Wave 6-12 active-triangle framework
target_result: UNKNOWN
novelty_status: UNKNOWN
```

This verdict was frozen before reading
`verification/2026-07-22-wave13-n3-45-audit.md` or any file under
`verification/n3-45-equality/`.

The proof in `agents/2026-07-22-wave13-n3-45-proof-a.md`, SHA-256
`e721614256f003d7266d0b3d1bb2f884febbdec33893f92ed18bf8961c6958e8`,
is semantically valid conditional on the audited Wave 6--12 premises.

Critical conclusions independently fixed:

1. Flower external parts are pairwise disjoint only by using both linearity
   and the common-point/Berge-triangle obstruction.
2. Every singleton- or empty-crossing-forced cross-pair is a `K`-edge by
   complementarity and lies outside `F` because any point owner would form a
   forbidden three-point motif with the root and petal.
3. In the mixed `r=14` profile, the size-three intersection graph is simple,
   cubic, and triangle-free. Incidence capacity leaves only `R=K3,3`; the
   exact forced equation
   `N_U(a_i)=N_{L(R)}(i)` and distinct open neighborhoods in the rook graph
   make `i -> a_i` inject nine edge labels into three eligible ordinary
   `t=0` labels, a contradiction.
4. For two meeting size-three points the external labeled crossing is
   `2`-by-`2` and is exactly empty or `K2,2`. A full crossing corresponds to
   an actual original graph edge and contributes exactly four to its
   `d_H`, by the audited support bijection.
5. The exact `r=15` local enumeration has only modes `111`, `122`, `222`,
   and `223` before the `t=3` parity step. The parity step removes `t=3`;
   the labeled degree-three contradiction removes `111`.
6. After those removals, all actual graph-edge crossings are exhausted:
   a size-two endpoint permits only zero or a four-edge `K2,2`; two disjoint
   size-three endpoints additionally permit a six-cycle, but modes `122`
   and `222` have residual fixed-point capacities four and zero, so degree
   six is impossible; an inactive endpoint gives zero by
   `d_H(uv)=e_L(S_u,S_v)`.
7. Hence every vertex of `H` has degree zero or four. The Wave 6 bijection is
   one unlabeled induced `N3` per edge of `H`, with no orientation factor, so
   `|E(H)|=n3=45` and the handshake sum is `90`, not divisible by four.

Independent finite companion:

```text
verification/n3-45-equality-b/audit_semantics.py
sha256 ce9ccd7fe6f33ef1a2007dea6f8cf27bda0dfdb93168996255d5bb2dd17c3b42
result PASS
```

Diagnostic weakened models fixed before comparison:

- A full labeled `1`-by-`2` crossing has row degree two but two column
  degrees one. It is a counterexample to checking the zero-or-two rule on
  only the singleton side.
- The linear point sets
  `P={0,1,2}`, `Q={0,3}`, and `R={1,3}` have pairwise singleton
  intersections at three different labels. Without the common-point rule,
  `Q` and a petal based at label `1` can reuse external endpoint `3`, and
  the would-be forced cross-edge `{1,3}` is owned by `R`, hence lies in
  `F`. This is a countermodel to both endpoint distinctness and
  “forced edge lies outside `F`” under a linearity-only formulation.
- A labeled `3`-by-`3` six-cycle satisfies the two-sided zero-or-two crossing
  rule and has six edges. It is a countermodel to the final `{0,4}` claim if
  the fixed-point capacities of modes `122` and `222` are omitted.

Limitations: this verifies only the conditional equality exclusion. It does
not verify the existence or nonexistence of `srg(99,14,1,2)`, and it makes no
literature-novelty claim.
