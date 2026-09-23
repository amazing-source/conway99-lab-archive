# Independent audit of the triangle-side incidence bound

Verdict: `PASS` for the conditional strengthening `n3 >= 30` and
`induced_C6_count >= 209,316`. Conway-99 remains `UNKNOWN`.

> **Post-audit provenance note (2026-07-23):** the Wave 7 discovery report was
> later amended only to credit Lou--Murin 2014 for the fixed-triangle profile
> and `q!=1` gap. The input hash below identifies the exact mathematical text
> audited at commit `0728b260...`; the attribution correction and expanded
> source search are recorded in `agents/2026-07-22-wave8-status-search.md`.

```yaml
role: verifier
date_utc: 2026-07-23T00:43:19Z
git_commit: 0728b260e1282afdbaeaa9215659a4175cab25de
claim_label: VERIFIED
scope: triangle-partner identities, q-gap, support identity, and complete n3=24/27 finite incidence reduction
inputs:
  agents/2026-07-22-wave7-triangle-side-incidence.md: 2225d7f26f8719d24bceca0c4ef6d8b829332a80793762769d282f176e75b651
  agents/2026-07-22-wave6-opposite-edge-graph.md: 4197c40e1b43d72d5a2ad9a6203099ffed2e1dbf4f0b3c07186aaad54cae4fa2
  verification/2026-07-22-n3-count-bound-audit.md: 773321e8b9934d658f810c6c2eef0e00a339414d98be330ca273d3f9b8bd7753
  verification/n3-side-incidence/verify.py: ec51e5245a886f4f10520393ed06140fb4f9f07531f5461c9fc89f04c5654441
  verification/n3-side-incidence/audit_generic.py: cf37f75ad033cb2f9d839e7fa85d6bac2e6d113cfdfc07bc78a043e453482f98
  verification/test_n3_side_incidence.py: d63a97c139b3c405c398aaba14a1e0043c492f1220580c749b9bb0298838ef73
method: two independent adversarial reconstructions, two materially different exhaustive standard-library implementations, multiplicity audit, and clean-source replay
command: |
  python verification/n3-side-incidence/verify.py
  python verification/n3-side-incidence/audit_generic.py
  python -m unittest discover -s verification -p "test_*.py" -v
outputs:
  n3_24_support_maximum: 6
  n3_24_support_required_by_degree: 12
  n3_27_C3_plus_C6_support_maximum: 9
  n3_27_3C3_support_maximum: 8
  n3_27_Mantel_support_minimum: 11
  global_n3_lower_bound: 30
  global_induced_C6_lower_bound: 209316
  exact_checkers: PASS
limitations: conditional on the previously audited H/L structural premises and the target-specific forced N3 theorem; no existence or nonexistence certificate was found
```

## Structural reconstruction

The adversarial verifier independently reconstructed all three fixed-triangle
counts

```text
sum a_r=212, sum r a_r=216, sum binom(r,2) a_r=36
```

and their unique solution

```text
(a_0,a_1,a_2,a_3)=(20+q,180-3q,3q,12-q).
```

It also checked the matrix identity
`C=Gamma^2-5Gamma-18I`, including the bijection between common neighbors of
two disjoint vertices of the triangle-intersection graph and cross-edges of
the corresponding graph-triangles.

For fixed side triangle `T`, the verifier reconstructed the two local
matching choices at every potential cross-edge. Both choices are prisms or
both are `N3`s, so the nonisolated part `H_T` is a simple 2-regular subgraph of
triangle-free `H`. Since `|E(H_T)|=3q(T)`, the forbidden value `q(T)=1` would
make `H_T` a triangle. No orientation or factor-of-two issue was found.

For active triangle sets

```text
S_u={active graph-triangles containing u},
```

the audit checked, for every actual graph edge `uv`, the bijection

```text
d_H(uv)=e_L(S_u,S_v).
```

The right side counts each distinct crossing `L`-edge once, even when the
sets overlap. The statement is not asserted for arbitrary pairs of graph
vertices.

## Independent finite checks

The first checker explicitly enumerates the complement components forced by
the extremal `q` sequences. It verifies:

- `n3=24` forces eight active `q=2` triangles and `K=4K2`;
- `n3=27` forces nine active `q=2` triangles and
  `K` of type `C9`, `C4+C5`, `C3+C6`, or `3C3`;
- the 16 matching-point patterns have support maximum six;
- the 64 central `C3+C6` patterns have support maximum nine; and
- the central `3C3` patterns have support maximum eight.

The second implementation does not encode those point choices by hand. It
generates every clique of `K`, enumerates all edge-disjoint clique families,
enforces the graph-triangle incidence cap, permits unused `K`-edges, applies
the `K3` common-point rule, and adds distinct singleton fillers until every
active triangle has three graph vertices. Its exact family counts are

```text
K=4K2:       16
K=C9:        512
K=C4+C5:     512
K=C3+C6:     448 without a central, 64 with one
K=3C3:       343/147/21/1 with 0/1/2/3 centrals
```

It independently returns maxima `6`, `9`, and `8`. With no size-three point,
every positive candidate degree is four, contradicting degree sum 54 in the
27-edge cases. With a central point, the maxima nine and eight are below the
Mantel minimum eleven. The 24-edge case is even stronger than its Mantel
minimum ten: allowed degree four requires twelve support vertices, while at
most six can occur.

Both implementations count every point-pair with an allowed crossing number
as a possible support vertex whether or not that pair is actually a graph
edge. Their maxima are therefore safe upper bounds rather than optimistic
realizability counts.

## Adversarial wording and scope checks

The audit required the publication to make the following distinctions:

- vertices in the support of `H` are graph edges of `G`;
- `H_T` is a subgraph of `H`, not necessarily an induced subgraph;
- `S_u` uses active triangles only;
- `e_L(S_u,S_v)` counts crossing edges once for possibly overlapping sets;
- a `K`-edge need not represent a triangle intersection; unused edges are
  allowed; and
- no automorphism of a completed graph is assumed.

With those corrections, both independent verifiers returned `PASS`. Combining
the exclusions of 24 and 27 with the already verified conditional lower bound
24 and divisibility by three yields

```text
n3 >= 30,
induced_C6_count >= 209,316.
```

This is a stronger necessary condition only. The extremal `n3=30` case, the
existence question, and the nonexistence question all remain open in this
project.
