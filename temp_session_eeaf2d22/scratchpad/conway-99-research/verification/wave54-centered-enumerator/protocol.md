# Wave54 centered-enumerator independent verification protocol

Frozen before inspecting any file under
`attempts/wave54-centered-enumerator/` or
`agents/2026-07-27-wave54-centered-enumerator.md`.

## Role and evidence boundary

- Role: verifier.
- Baseline commit: `a4a61658356253fb95cf68252c972a4f79df38fe`.
- The discovery implementation is not an input to the independent derivation.
- Upstream mathematical inputs are limited to the independently integrated
  Wave39 artifacts listed below. Their meaning, provenance, and scope will be
  audited before use.
- A candidate ordinary weight enumerator is only a feasible formal enumerator.
  It is not a generator matrix, a ternary code, a complete weight enumerator,
  an endpoint object, or an `srg(99,14,1,2)`.

## Frozen target

Independently test the following conditional feasibility problem over exact
integers:

- alphabet size `q = 3`;
- length `n = 231`;
- putative code size `M = 3^11`;
- coefficients `A_0,...,A_231` with `A_0 = 1`;
- `sum_i A_i = M`;
- `A_i = 0` unless `i` is divisible by 3;
- every nonzero `A_i` is an even nonnegative integer;
- `A_198 >= 462`;
- for every `0 <= j <= n`,
  `B_j = (sum_i A_i K_j(i))/M`;
- projectivity constraints `B_1 = B_2 = 0`;
- every `B_j` is a nonnegative integer;
- formal self-orthogonality dominance `B_j >= A_j`;
- dual lower bounds
  `B_7 >= 198`, `B_12 >= 1386`, `B_13 >= 1386`,
  and `B_14 >= 16632`.

The independent Krawtchouk implementation must use the direct formula

`K_j(i) = sum_t (-1)^t 2^(j-t) binom(i,t) binom(n-i,j-t)`,

with impossible binomial terms interpreted as zero. It must not use a
Krawtchouk recurrence copied from or shared with discovery.

## Frozen candidate

The only nonzero proposed ordinary-enumerator coefficients are

```text
A_0   = 1
A_18  = 2
A_144 = 53316
A_153 = 19798
A_159 = 98496
A_162 = 5072
A_198 = 462
```

All other `A_i` are zero.

## Independently selected upstream inputs

```text
4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3  AGENTS.md
9d22f5ae2ed1f1ec756975508030f2b6b440580d1215604d4f353256bae1483b  verification/2026-07-27-wave39-integration-audit.md
094db8281faf23f402f5093a617c43ebe428dae6f8ce1eceae8621472fc37111  verification/2026-07-27-wave39-orchestrator.md
85b8d36d6ce5ebd638e957e1731864eff75f38405935f5e51ad5b629edea5966  verification/wave39-edge-local-rank/independent-results.json
3afc665de9d8d0e5a5a4dab6b600db1e5b726ef1dfba685eeba92c80da1df5e4  verification/wave39-proof-solver/exact-results.json
c11b09f9da2300261bf8b0bc665fc5cc4b5654c6a460a9b7b43d5a53ee3ad970  verification/wave39-edge-local-rank/package-manifest.sha256
62af7bb7e0ff6dedb64fe8173394e04ca16c082d9eedc43ea30bfb05dcc0e98e  verification/wave39-proof-solver/package-manifest.sha256
```

## Checks fixed in advance

1. Rehash and audit the selected Wave39 artifacts.
2. Recompute all 232 `B_j` exactly from the direct combinatorial sum.
3. Check `B_0 = 1`, integrality, nonnegativity, projectivity, dominance,
   the four named dual lower bounds, and
   `sum_j B_j = 3^220`.
4. Check the complete sparse support and every frozen condition on `A`.
5. Compare the full recomputed `B` vector byte-for-value with discovery only
   after the independent result exists.
6. Recompute and compare every discovery result and manifest hash.
7. Run hostile mutations, including violations of total size, support
   divisibility, evenness, the `A_198` floor, projectivity, transform
   integrality/nonnegativity, formal dominance, and each dual lower bound.
8. Audit the claimed implication boundary and identify any condition whose
   provenance is absent, overstated, or not necessary for the stated formal
   feasibility scope.

## Resource condition

The checker will abort before substantive computation if free physical memory
is below 15 percent. At freeze time it was 51.37 percent.
