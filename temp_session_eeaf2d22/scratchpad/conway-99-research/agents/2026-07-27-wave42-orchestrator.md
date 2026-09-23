# Wave 42 orchestrator freeze

Date: 2026-07-27 UTC

Base commit: `ef49b60aafd67f9007f6c218c39fd50392453a1b`

Target:

```text
Does an srg(99,14,1,2) exist?
```

The target remains `UNKNOWN`. The strongest verified starting theorem is

```text
rank_F7(M)>=26.
```

The rigorous induced-prism interval remains

```text
708<=n3<=4158.
```

## Disjoint discovery lanes

1. **Rank-26 equality.** Classify the exact equality cases in every
   39-point edge block. Seek either a universal rank-27 theorem or complete
   rank-26 normal forms suitable for global coupling.
2. **Joint endpoint incidence.** Under the explicitly scoped assumptions
   `n3=4158`, `r3=12`, and all edge types `222`, enforce the simultaneous
   outside incidence matrix and outside graph through `BB^T`, `BH`,
   `B^TB+H^2`, common-neighbor equations, and `K^2=0`.
3. **Proof-producing endpoint search.** Strengthen one frozen refined
   endpoint case, preferably branch 15, while retaining exact input hashes,
   atomic journals, cut catalogues, and proof-chain requirements.

## Promotion boundary

- Discovery cannot verify itself.
- Rank 26 has the exact local decomposition

  ```text
  rank(K39)=rank(S)+2 rank(F)+rank(residual).
  ```

  A rank-26 classification must cover every minimum-rank border permutation
  and every labelled third-fibre perfect matching; samples and representatives
  are insufficient.
- The scoped all-`222`, `r3=12` lane cannot be promoted to an endpoint theorem
  unless those hypotheses are separately proved or every other branch is
  excluded.
- Added clauses must be derived from checked graph identities and replayed
  against the frozen source. A stronger formula without a checked terminal
  proof is a reduction, not an endpoint exclusion.
- A solver status, timeout, model confidence, propagation fixed point, or
  unverified assignment is not a certificate.
- A graph candidate requires independent checks of all 99 degrees, every
  adjacent/nonadjacent common-neighbor count, simplicity, and the claimed
  prism statistic.
- `UNSAT` requires a retained proof accepted by the frozen independent
  checker chain.

## Workspace note

The pre-existing untracked file
`attempts/wave41-endpoint-evenpart/type-6-results.json` is outside Wave 42's
frozen evidence. It is an unverified orphaned discovery artifact and will not
be promoted or overwritten.
