# Waves 43--44 integration audit

Date: 2026-07-27 UTC

Base commit: `e28f90464d00b98d37672b0b2b23dba15399a6f2`

Verdict: **PASS for one conditional endpoint rank theorem, three scoped
endpoint reductions, and two exact relaxation-feasibility controls.
Conway-99, `n3=4158`, a strict general upper bound below 4158, and
novelty/priority remain `UNKNOWN` or `NOT PROVED`.**

## Separation and replay

Discovery, verification, and orchestration remained separate. Each promoted
Wave 43 claim has an independent implementation, hostile or positive controls,
and a frozen comparison boundary.

The rank verifier independently reconstructs the local matrices and exhausts
both rank-27 mechanisms for endpoint types `222`, `24`, `33`, and `6`. It
agrees with discovery on 36/36 compared fields and includes planted type-`6`
rank-zero and type-`33` rank-two leaves.

The all-rank33 verifier regenerates all 4,050 normalized quotients, all
`2^18` masks, all 37,378 triangle-free masks, the exact 264-mask rank-33
stream, and every per-mask forced-Gram and six-set record. The branch-15
verifier independently replays the frozen OPB closure and complete named
two-triangle clause family. The order-seven verifier independently enumerates
all 156 and 1,044 unlabeled graphs on six and seven vertices, checks labelled
orbit sums `2^15` and `2^21`, filters 62 and 208 locally admissible classes,
and reconstructs every equation.

Wave 44 was checked after a pre-discovery protocol freeze. The verifier
independently derives the vertex-, ordered-edge-, and ordered-nonedge-root
equations, reconstructs all 170 coefficient rows and right sides, and
substitutes the 91-support witness using exact integers. It also reproduces
the free HiGHS status-2 result, then refutes it as mathematical evidence:
the exact and binary64 witness residuals are zero, and the same model with
variables fixed to the witness returns optimal.

## Conditional endpoint rank 28

The Wave 42 identity is

```text
rank_F7(K39) = (25-2e) + 2 rank(F) + rank(D),  rank(F)>=e.
```

At `n3=4158`, local rank 27 can arise only from

```text
rank(F)=e,   rank(D)=2,
```

or

```text
rank(F)=e+1, rank(D)=0.
```

Complete exact searches exclude both mechanisms for all four endpoint types.
Principal-block monotonicity and the previously verified rank transport give

```text
n3=4158  ==>  rank_F7(M)>=28.                 VERIFIED
```

Equivalently, `rank_F7(M)=27` forces an induced triangular prism. With
`n3+3P=4158`, this gives the conditional branch bound `n3<=4155`.
It is not a strict general upper bound because ranks 28 through 44 remain
compatible with the endpoint. Exact endpoint arithmetic leaves 281
`(r3,r7)` pairs.

## Scoped endpoint reductions

All 264 canonical rank-33 lifts in the conditional all-`222`, `r3=12` lane
have `12+24` components, fibre balance `4+8`, and exactly the three expected
rational Gram-kernel directions. Five numerical candidate-census rows occur
with multiplicities `48/48/24/48/96`; every lift survives.

The branch-15 two-triangle family contains 40,800 exact width-four clauses.
After the frozen closure, 34,340 remain active, all with slack three. All 64
bounded polarity probes remain nonterminal. Endpoint proof coverage is still
`0/33`.

For canonical mask `51739`, exact compact CNF and sparse MILP formulations
of the 45,032-candidate three-way matching are retained. CaDiCaL stopped after
five million conflicts and HiGHS stopped without an incumbent; both results
are `UNKNOWN` and neither is promoted.

## Alternative-space boundary

The unrooted order-seven relaxation has an exact nonnegative 99-support
solution at `n3=4158`, `h11=16632`. It satisfies all 62 deletion and 19
Hamiltonian equations, totals `binom(99,7)=14,887,031,544`, and assigns zero
to all three prism-containing seven-types.

The aggregate rooted extension adds seven vertex-root, 36 ordered-edge-root,
and 46 ordered-nonedge-root rows. Its coefficient rank rises from 81 to 93,
and the first witness fails every new family. A second exact 91-support
integer witness nevertheless satisfies all 170 rows. Thus both linear count
spaces are rigorously shown too coarse. Feasibility of either relaxation is
not a graph or evidence of endpoint existence.

## Status wall

```text
n3=4158 => rank_F7(M)>=28:             VERIFIED
conditional endpoint rank pairs:        281
all 264 rank-33 lift reductions:         VERIFIED SCOPED
branch-15 two-triangle cuts:             VERIFIED SCOPED
unrooted order-seven relaxation:         EXACT FEASIBLE
aggregate rooted order-seven relaxation: EXACT FEASIBLE
endpoint proof coverage:                 0/33
upper bound below 4158 in general:        NOT PROVED
rigorous interval:                        708 <= n3 <= 4158
n3=4158 / Conway-99:                      UNKNOWN
novelty and priority:                     UNKNOWN
```
