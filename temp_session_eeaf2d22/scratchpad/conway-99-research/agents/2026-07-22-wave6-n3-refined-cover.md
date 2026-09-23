# Wave 6 refined `N3` common-neighbor cover

```yaml
role: proof_a
date_utc: 2026-07-23T00:03:07Z
git_commit: a066170e452f31efe1e00610b8159a66b825b01f
claim_label: DERIVED
scope: complete 78-branch refinement conditional on the verified canonical N3 unit and 12-branch shared-fiber cover
inputs:
  code/root_model.py: 2a1f074f29f2e00e38437bf81418771d57ab41335605b9f3b9f2cae061a1624e
  code/matching_orbits.py: 1ba68393c385ef296458555b7c48533786ea592a50bec589be675f95fd550240
  code/sat_model.py: 45f0da74619b31a1a31cc407f702f8e86a0597ee73d29ec268528cd89980aef8
method: exact rooted profile, oriented-stabilizer enumeration, exhaustive state-orbit traversal, and deterministic SAT-literal reconstruction
command: |
  .venv/Scripts/python code/matching_orbits.py --n3-refined
  .venv/Scripts/python code/sat_model.py --pair-count 7 --cardinality native --n3 --n3-refined-branch 1
outputs:
  verification/n3-refined-cover/n3-refined-cover.json: fd9a14193365bf40d3d7bcbe53d56c6f1ffa8a93ca63d5b68506c3354f3b9f8a
  verification/n3-refined-cover/verify.py: cbf0b46a4656b54c0f5b6a65a7f0e549286a5cfb68ca7ee54813b43423d1cb9a
limitations: this is a symmetry-safe finite search reduction, not a solved branch or a result on target existence
```

## Forced second-stage choice

Write the canonical normalized residual edge as

```text
p = label(0,2)  ~  q = label(2,4).
```

The rooted coordinate-4 profile for `p` has target two. The normalized `N3`
already supplies neighbor `q`, so exactly one additional neighbor of `p` in
the coordinate-4 fiber must be present. It has label `(4,h)`, where

```text
h in {0,1,3,6,7,8,9,10,11,12,13}.
```

Endpoint `2` is the already-fixed neighbor, while `4` and its mate `5` do not
label vertices in that fiber. The eleven possible additional edge literals
are respectively

```text
2, 14, 34, 44, 45, 46, 47, 48, 49, 50, 51.
```

This is an exact-one consequence of the existing rooted formula. A refined
branch needs only one new positive unit; the other ten alternatives are forced
false by the coordinate equation and the normalized unit.

## Oriented stabilizer and orbit cover

The order-768 stabilizer of the unordered `N3` edge may exchange coordinates
`0` and `4`. Orienting the refinement at `p=(0,2)` removes that exchange. The
remaining group fixes coordinates `0` through `5` and acts as

```text
H0 = C2 wreath S4,   |H0| = 384
```

on the four unused coordinate pairs.

A refined state consists of:

1. one of the 945 perfect matchings on the shared fiber `S_2` that contains
   endpoint edge `(0,4)`; and
2. one of the eleven additional-neighbor endpoints `h`.

Thus there are `945 * 11 = 10,395` labeled states. Exact traversal under `H0`
gives 78 disjoint orbits. The fixed-point sum is

```text
29,952 = 78 * 384.
```

The orbit-size histogram is

```text
1:3, 8:6, 12:6, 32:3, 48:18, 64:6,
96:9, 192:12, 384:15.
```

Above the twelve parent matching branches, the numbers of refined orbits are

```text
4, 5, 5, 4, 4, 6, 7, 6, 8, 8, 10, 11.
```

They sum to 78. The public certificate records every canonical representative,
parent branch, candidate endpoint, orbit and stabilizer size, and positive SAT
literal list.

## Encoding interface

Select a case with `--n3-refined-branch 1..78`:

```powershell
.venv\Scripts\python code\sat_model.py --pair-count 7 `
  --cardinality native --n3 --n3-refined-branch 1 `
  --opb logs\local\conway99-n3-refined-001.opb
```

Relative to the unnormalized target encoding, one refined branch adds 67 unit
clauses: the `N3` unit, 65 nonduplicate decisions completing the shared-fiber
matching, and one additional-neighbor unit. The final unit profile has seven
positive and 60 negative edge decisions. It adds no variables or cardinality
constraints.

The CLI and direct API reject a missing `--n3`, a non-target scaffold, indices
outside `1..78`, legacy matching branches, a simultaneous 12-way branch, and
duplicate branch insertion. Applying `H0` is global relabeling of a putative
solution, not an assumed automorphism of its completed graph.

The independent audit promotes only this conditional finite cover to
`VERIFIED`. Conway-99 and every refined branch remain `UNKNOWN`.
