# Wave54 centered-enumerator independent audit

Date: 2026-07-27 UTC

Baseline commit: `a4a61658356253fb95cf68252c972a4f79df38fe`

Verdict: **VERIFIED for the exact frozen formal ordinary-enumerator
feasibility claim.  No code, complete enumerator, endpoint object, graph, or
upper-bound improvement is verified.**

## Independent reconstruction

The protocol was written before any Wave54 discovery implementation or report
was opened.  The independent checker uses the defining combinatorial formula

```text
K_j(i)=sum_t (-1)^t 2^(j-t) C(i,t) C(231-i,j-t)
```

and Python arbitrary-precision integers.  Discovery instead uses a three-term
Krawtchouk recurrence.  A separate unit-test oracle extracts coefficients
from

```text
(1+2z)^(n-i) (1-z)^i
```

for every `q in {2,3,4,5}`, `0<=n<=9`, and every admissible `i,j`.

The independently recomputed nonzero primal coefficients are exactly

```text
A_0   = 1
A_18  = 2
A_144 = 53316
A_153 = 19798
A_159 = 98496
A_162 = 5072
A_198 = 462
```

They sum to `177147=3^11`.  Every occupied nonzero weight is divisible by
three and has even multiplicity.

All 232 dual coefficients were recomputed.  The only zeros are `B_1` and
`B_2`; every coefficient is an integer and is nonnegative.  Selected exact
values are

```text
B_0  = 1
B_1  = 0
B_2  = 0
B_7  = 8143116060
B_12 = 1185646137004494672
B_13 = 38435816835634909096
B_14 = 1155653940391429336216
```

The full vector satisfies `B_i>=A_i` and

```text
sum_i B_i =
3^220 =
926138713099787670959935798024513966701772293499227988263405269197039529170894882252068039219702299428401.
```

The full independent `A` and `B` vectors equal discovery's vectors at every
one of the 232 indices.

## Provenance of the frozen conditions

From the integrated Wave39 centered-boundary record:

- `W=col(Z)` has length 231 and dimension 11, so `|W|=3^11`;
- `Z^T Z=0` gives `W subseteq W^perp`;
- the 231 generator columns are nonzero and pairwise nonproportional, so
  projectivity gives `B_1=B_2=0`;
- self-orthogonality gives `wt(c)=c dot c=0 mod 3`;
- nonzero ternary words occur in distinct scalar pairs `{c,-c}`;
- `W subseteq W^perp` gives the necessary coefficientwise count
  `B_i>=A_i`;
- 231 distinguished weight-198 words and their negatives give
  `A_198>=462`;
- the recorded star-word constructions give
  `B_7>=198`, `B_12>=1386`, `B_13>=1386`, and `B_14>=16632`;
- `dim(W^perp)=231-11=220`, so the dual size is `3^220`.

The Wave39 integration audit classifies the simultaneous-B/H lane as
`DERIVED_INCONCLUSIVE`, not as an independently promoted graph-to-code
theorem.  This Wave54 verification treats those conditional code consequences
as frozen inputs and independently verifies their enumerator feasibility; it
does not re-promote the underlying endpoint derivation.

## Corrections and hostile audit

The first preinspection protocol list omitted the Wave39 simultaneous-B/H
source package.  That provenance omission was recorded before opening the
package in `protocol-corrections.md`; no mathematical target or test was
changed.

Two elementary necessary ordinary-code conditions were absent from the
Wave54 frozen list:

1. every nonzero dual multiplicity `B_i` is even by ternary scalar pairing
   (and therefore every `B_i-A_i` is even for `i>0`);
2. Wave39 records the all-one vector in `W^perp`, so ordinary feasibility also
   requires `B_231>=2`.

The candidate passes both: every nonzero `B_i` and every nonzero
`B_i-A_i` is even, and

```text
B_231 =
19480428691810750580106083708137499612422891810373801997825474560.
```

These omissions do not change the candidate's feasibility.  They do mean the
discovery disposition should be read as

```text
no obstruction from the exact listed ordinary constraints
```

rather than a proof that no other ordinary one-variable code constraint can
exist.  In particular, the statement in `failed-routes.md` that the smallest
meaningful continuation must be complete or joint enumerators is a research
recommendation, not a verified exhaustion theorem.

The independent suite contains 22 tests.  It mutates `A_0`, primal size,
support divisibility, parity, the `A_198` floor, dual integrality,
nonnegativity, projectivity, dominance, each of the four dual bounds, dual
size, MacWilliams equality/integrality, discovery `A` and `B`, and manifest
expectations.  All 22 passed.  Discovery's six tests also passed on replay.

## Exact discovery hashes

```text
d7f8da8862c74da08e5d122e028f95125051d4e3032287f8e2e7f5490ded3cd8  attempts/wave54-centered-enumerator/exact-results.json
6d3983f7e67211eff34b08960cd11ef1d0d07514fc23a1dfea2e47f666d61932  attempts/wave54-centered-enumerator/input-freeze.sha256
4e6fa530dee3c30be6423d9b08f87e6389a59f20d972a5df999ca97541a2db23  attempts/wave54-centered-enumerator/package-manifest.sha256
531bed27e505a9db18b97ab6062ce1e002a0cf3bc488b01086b89be1ad566e76  agents/2026-07-27-wave54-centered-enumerator.md
```

Every entry in both discovery manifests rehashed successfully.  The
discovery candidate's internal sparse-enumerator hash is
`df68b6aefb292f22852672b155304b15b4010e76e277647cc4db3c1598f0777a`.

## Status wall

```text
listed formal ordinary enumerator: VERIFIED FEASIBLE
realized ternary [231,11] code:     NOT CONSTRUCTED
complete or joint enumerator:       NOT CONSTRUCTED
centered endpoint object:           UNKNOWN
srg(99,14,1,2):                     UNKNOWN
upper bound below n3<=4158:         NOT PROVED
novelty and priority:               UNKNOWN
```
