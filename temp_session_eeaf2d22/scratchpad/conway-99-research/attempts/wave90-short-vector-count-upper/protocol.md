# Wave 90 protocol: a prism-free norm-14 count

Claim label: `DERIVED`.

## Frozen scope

The theorem in this package is conditional on:

1. a hypothetical `srg(99,14,1,2)`;
2. the **prism-free endpoint** `P=0`, equivalently `n3=4158` under the
   previously verified identity `n3+3P=4158`; and
3. the verified Wave 71 description of every norm-14 integer `-4`
   eigenvector as seven `+1` and seven `-1` coordinates whose signed support
   is the complementary-Fano `2-(7,4,2)` incidence graph.

The count `N14` includes both `t` and `-t`.

The bound itself does not assume `r=28` or `q=16`. Those hypotheses are
needed only if a later orchestrator combines the bound with the provisional
Wave 86 scalar theorem.

## Target

Prove, without a graph automorphism assumption,

```text
N14 <= 5544.
```

The checker must reproduce the rooted `560`, `84`, `8`, `672`, `4`, `392`,
and global `5544` counts exactly. It must also verify the complementary-Fano
root reconstruction used for injectivity.

## Nonpromotion rules

- This discovery package does not verify itself.
- The theorem is not valid for a general target graph with prisms.
- It is not an upper bound on `N14+N16+N18`.
- It is not, by itself, a contradiction or a Conway-99 resolution.

