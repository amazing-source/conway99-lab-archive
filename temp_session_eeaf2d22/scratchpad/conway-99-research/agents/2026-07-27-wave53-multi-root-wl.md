# Wave 53 multi-root coherent-lift discovery

```yaml
role: proof_b
date_utc: 2026-07-27T19:58:38Z
git_commit: a4a61658356253fb95cf68252c972a4f79df38fe
claim_label: DERIVED
scope: two-root completion-free CSP and tuple-WL lifts for root relations K, B, C, D
inputs:
  attempts/wave53-multi-root-wl/input-freeze.sha256: frozen source hashes
method: exact 2-WL on merged cap-incidence CSPs plus exact 3-WL on typed triangle cores
command: python -B attempts/wave53-multi-root-wl/multi_root_wl.py --verify attempts/wave53-multi-root-wl/exact-result.json --envelope-only
outputs:
  attempts/wave53-multi-root-wl/exact-result.json: d99d89ef56cbd1f603cc8668b340bd7ad20993570899eaf556ee4c9a7f400717
limitations: discovery-only local relaxation; independent recreation required; endpoint UNKNOWN
```

## Result

This lift is genuinely stronger than Wave 52: it retains two rooted `3K6`
systems simultaneously, identifies their `5,2,1,0` common `K`-neighbor
triangles in root relations `K,B,C,D`, merges identical candidate variables,
and keeps all 72 exact-two cap nodes.

The `B` case contains the only shared candidate variable. It is forced true:
the two common triangles already have the two root edges between them, while a
third cross edge would be a forbidden triangular prism.

Exact expanded-CSP 2-WL stabilizes at:

```text
K: order 319, 285 colors
B: order 323, 584 colors
C: order 325, 321 colors
D: order 326,  63 colors
```

Exact 3-WL on the triangle cores stabilizes at `107,321,240,61` colors.
Every 2-WL intersection number is a nonnegative integer. Deterministic local
controls satisfy every cap in all four relation types, including the shared
forced truth in `B`.

## Disposition

```text
new multi-root coupling:                 yes
new forced Boolean value:                yes, one in the B-root template
root relation excluded:                  no
positive local-cap controls:             K, B, C, D
prism-free endpoint:                     UNKNOWN
Conway-99:                               UNKNOWN
```

The next coherent route must add compatibility among at least three
overlapping rooted systems or bring point-level SRG constraints into the cap
variables. Two-root WL closure alone does not close the endpoint.
