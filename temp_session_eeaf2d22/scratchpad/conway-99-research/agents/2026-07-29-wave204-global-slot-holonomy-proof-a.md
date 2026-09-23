# Wave 204 proof A: global slot-holonomy boundary

## Verdict

`DERIVED_WITH_EXACT_RELAXED_COUNTERCONTROLS_PENDING_INDEPENDENT_VERIFICATION`.

Two claims must be kept separate.

### A. Honest block-transition theorem

For an existing selected exact-three flag, the normalized relation gives

```text
z_T=z_S+z_Xa+z_Xb.
```

On the directed graph whose vertices are actual triangle blocks and whose
flag edge is `S->T`, define

```text
g(S->T)=z_T-z_S.
```

Then `g=dz`.  Every genuine closed block cycle has zero holonomy by
telescoping.  This is exact but tautological; it is not an endpoint
obstruction.

### B. Refuted center-gluing implication

Wave 203 supplies only an edgewise partial injection into a five-slot set.
For consecutive center labels `x->y->z`, composition requires the actual
triangle-block equality

```text
T_xy=S_yz.
```

No frozen theorem gives this equality, a total star-to-star map, or
surjectivity.  Thus center-cycle holonomy is undefined.

The exact package supplies three relaxed controls in the nonsquare
11-dimensional ternary orthogonal space.  For center-cycle lengths 3, 4,
and 5:

- every displayed column is singular and all are projectively distinct;
- every displayed center-star has Gram `J_7-I_7` and sums to zero;
- every displayed flag obeys `T=S+X_a+X_b`;
- isolated singular fillers make the displayed span rank 11;
- only one cyclic orientation per displayed label is used, so `b=0`;
- the incoming block differs from the outgoing block at every center; and
- the projected gain defect is nonzero.

The package also freezes identical one-point partial injections with two
full `S_5` extensions having identity versus transposition monodromy.
Therefore neither additive center holonomy nor full five-slot permutation
holonomy is determined by the Wave 203 interface.

```yaml
role: proof_a
date_utc: 2026-07-29T19:00:33Z
git_commit: e6ac24b5728ae8f2dc13b5a6ee0f50e965843b71
claim_label: REFUTED
scope: >-
  Conditional prism-free n3=4158 and rank-11 endpoint, with the surviving
  b=0 selected-orientation interface: exact block-coboundary theorem and
  refutation of center-cycle/slot-permutation holonomy from the current
  local premises.
inputs:
  attempts/wave204-global-slot-holonomy-proof-a/input-freeze.sha256: 7b2707d208e45fc288a0d2e3b94aa2c9999c2ec5887b1f4700b0d1ca4ddf18e0
method: >-
  Exact ternary coboundary algebra, type-correct incidence audit, canonical
  C4 Gram arithmetic, explicit nonsquare rank-11 A6/flag controls, and
  paired extensions of the same partial five-slot interface.
command: >-
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave204-global-slot-holonomy-proof-a\test_exact_check.py;
  .\.venv\Scripts\python.exe -B
  attempts\wave204-global-slot-holonomy-proof-a\exact_check.py --verify
  attempts\wave204-global-slot-holonomy-proof-a\exact-results.json
outputs:
  attempts/wave204-global-slot-holonomy-proof-a/package-manifest.sha256: e060f0f39c2b66b6b64a20694a2a6505f229cd85c7784374976e39cdba61dd84
limitations:
  - The exact controls do not realize 99 stars or 231 global columns.
  - They do not realize the global frame identity, point-triangle incidence,
    SRG axioms, Wave201 cover totals, an endpoint code, or a graph.
  - They refute only the claimed implication from the listed local premises.
  - This proof agent cannot self-promote to VERIFIED.
  - Rank 11, endpoint existence, Q>=7060, strict n3 improvement, external
    novelty, and Conway-99 remain UNKNOWN.
```

## Exact low-cycle table

| object | triangle | quadrilateral | pentagon |
|---|---:|---:|---:|
| genuine closed block-transition cycle | holonomy `0` | holonomy `0` | holonomy `0` |
| projected center cycle under Wave 203 | undefined | undefined | undefined |
| exact relaxed projected defect | nonzero | nonzero | nonzero |

The canonical graph quadrilateral is not a forced 2-cell on this branch:
its Gram kernel locates a possible checkerboard relation but does not assert
that the four columns are dependent.

## Premise wall

The countercontrols satisfy the correct field, nonsquare rank-11 ambient
form, local projective singular `A6` geometry, normalized flag equations,
cycle lengths, and displayed `b=0` orientation pattern.

They intentionally omit global endpoint incidence.  They are logical
countermodels to a proposed gluing lemma, not endpoint candidates.

## Boundary

The smallest honest incidence complex is a one-dimensional gain graph on
triangle blocks.  Its gains are exact coboundaries.  Any nontrivial global
continuation must first force intermediate block matching, total slot
transport, or genuine higher cells.

No rank-11 or endpoint exclusion, `Q>=7060`, strict `n3` improvement, graph,
code, or Conway-99 resolution follows.
