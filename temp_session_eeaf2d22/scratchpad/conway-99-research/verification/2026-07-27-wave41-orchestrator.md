# Wave 41 orchestrator decision

Date: 2026-07-27 UTC

## Decision

Publish Wave 41 as a verified universal characteristic-seven rank theorem and
a rigorous endpoint checkpoint:

```text
rank_F7(M)>=26.
```

Do not present it as a Conway graph, counterexample, prism-free endpoint
exclusion, upper bound below `n3=4158`, or novelty/priority result.

## Why promotion is justified

The four all-odd edge types and seven even-part edge types were handled by
separate finite arguments. Both were reconstructed without discovery
internals by clean-room verifiers.

The even-part verifier independently:

1. derived equality in the Wave 40 39-point rank bound;
2. enumerated every minimum-projection permutation;
3. canonicalized every right kernel and equality target;
4. evaluated all 10,395 labelled third-fibre matchings for every distinct
   kernel;
5. checked exact 39-block and cubic-core ranks;
6. supplied synthetic rank-25 positive controls for the equality criterion;
7. replayed the discovery only after freezing its implementation; and
8. composed with the separately verified all-odd result.

The discovery and primary verifier agree exactly on 164,928 permutations,
52 right kernels, 164,278 targets, 540,540 grouped matching evaluations, and
zero rank-25 survivors.

A second verifier independently covers all eleven types with a different
pivot-branch/vectorized matching audit. Its complete replay and hostile tests
also pass.

The primary verifier's initial positive-control and stale-journal defects were
verifier-side artifact issues. The final publication includes their repair,
updated freeze hashes, a byte-exact full replay, and regression gates. No
mathematical count or theorem statement changed.

## Promoted theorem

Every edge normal form is indexed by one of the eleven positive partitions
of six. Each fully specified 39-point block has rank at least 26 over
`F_7`. Since it is a principal block of the transported global matrix and

```text
rank_F7(N M N^T)=rank_F7(M),
```

every hypothetical `srg(99,14,1,2)` satisfies

```text
rank_F7(M)>=26.
```

The result is universal: it assumes neither `n3=4158` nor a nontrivial graph
automorphism.

## Scoped conditional theorem

Under `n3=4158`, `r3=12`, and all edges type `222`, every base-triangle
39-block has rank at least 33 and parity forces even `r7>=34`. This branch
theorem is independently verified but does not prove its hypotheses.

## Boundary and continuation

At the prism-free endpoint, universal rank 26 reduces the arithmetic rank
pairs from 330 to 314. The rank ceiling remains 44, so no contradiction
follows.

The most useful next mathematical target is no longer rank-25 equality. It
is one of:

1. classify rank-26 equality and couple it across adjacent triangles;
2. enforce the simultaneous 36-by-60 binary incidence matrix, compatible
   eight-regular outside graph, and full `K^2=0` identities;
3. complete proof-producing solve-cut-check coverage of all 33 endpoint
   cases; or
4. derive a global motif inequality forcing a prism, which would prove
   `n3<=4155`.

The universal three-dimensional compact kernel shows that raw local
border-rank packing cannot supply this step.

## Publication classification

```text
universal rank_F7(M)>=26:              VERIFIED
conditional all-222, r3=12 floor:      VERIFIED SCOPED; even r7>=34
conditional endpoint rank pairs:       314
endpoint proof coverage:                0/33
upper bound below n3<=4158:             NOT PROVED
target, novelty, and priority:          UNKNOWN
```
