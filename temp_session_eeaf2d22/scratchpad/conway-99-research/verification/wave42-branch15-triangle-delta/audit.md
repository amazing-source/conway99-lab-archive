# Wave 42 branch-15 triangle-delta audit

## Verdict

`VERIFIED_SCOPED_REDUCTION`.

Before reading discovery implementation or clause catalogues, the verifier
froze an independent implementation and result. It independently reproduced
the generalized-unit closure of the 574,615-row source OPB, the direct
derivation `x2=1`, the full rooted triangle `[1,15,17]`, and every
prism-blocking clause based at that triangle.

After the freeze, a separate comparison parser checked both complete discovery
OPB catalogues. Their normalized clause sets equal the clean-room clause sets
exactly:

```text
raw:    64,932 clauses, SHA-256 e82aaa6b6f9cad3d27dbfb36069446a62aafbb2629fabc2a8492d243c1320635
active: 33,778 clauses, SHA-256 fc8925756861e850b28bfb9e18844dd75c525b75f4061f70089df696843ad903
```

## What this verifies

- The frozen branch-15 OPB forces the residual edge `x2=1`.
- This edge completes the rooted triangle with full zero-based vertices
  `[1,15,17]`.
- At the prism-free endpoint, the triangle soundly adds 64,932 exact negative
  prism clauses.
- Independent generalized-unit simplification leaves exactly 33,778 active
  clauses with no unit and no empty clause.

## What this does not verify

- It does not independently replay the discovery package's 64 failed-literal
  probes.
- It does not prove branch 15 satisfiable or unsatisfiable.
- It does not close any of the 33 endpoint cases.
- It does not improve the general upper bound or decide Conway-99.

The discovery reports its additional combined propagation and probe results as
null. Those null results remain useful diagnostics, not promoted verifier
claims.
