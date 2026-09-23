# Wave 58 proof-B report: cross-incidence rank synthesis

```yaml
role: proof_b
date_utc: 2026-07-27T21:10:13Z
git_commit: 4bb1989e9e286b2ec753a855db58ad584e31f63a
claim_label: DERIVED
scope: conditional n3=4158 fixed-triangle X/Y cross-incidence synthesis
inputs:
  verification/wave36-block-compatibility/independent-results.json:
    b92ee5cde6a63ba3cce09bc2eae1518979aea09c4f5db39789b65f117b0768c4
  attempts/wave57-star-complement/exact-results.json:
    2b49b0bf3d52c0101cfcd59c3324279c1f153f4d48504c7ae67658e8786e6216
  verification/wave40-edge-type-coupling/independent-results.json:
    822f758e04bcf95576cf8c5adc5cff2131ffa13cd286a6924137149de0dc3a9e
method: prior-rank replay, exact row intersection, wedge bound,
  normalized component censuses, restricted lift replay
command: python -B attempts/wave58-cross-incidence-rank/exact_check.py
  --verify attempts/wave58-cross-incidence-rank/exact-results.json
outputs:
  attempts/wave58-cross-incidence-rank/exact-results.json:
    ec03c32fc72ec75222049a49b194b10bcae6bf1122ac82d9d9943e5b2f63181a
limitations: separate local/scalar controls only; no simultaneous B/A_Y;
  endpoint and Conway-99 UNKNOWN
```

## Result

Wave 36 already proves

```text
rank(B)=35-kappa,
mult_Y(3)=18,
mult_Y(-4)=7+kappa,
kappa in {1,2,3}.
```

Wave 58 does not claim these identities as new. Combining them with Wave 57
reduces its 18 multiplicity rows to

```text
(18,8,1), (18,9,2), (18,10,3).
```

Writing `q=C4(X)`, the cubic triangle-free wedge count and `mu=2` give the
new synthesis bound `q<=27`, improving Wave 57's 89. Exact normalized
component censuses sharpen the rows to

```text
kappa=1: 0<=q<=27
kappa=2: 0<=q<=24
kappa=3: q in {6,8,10,12,14,16,18}.
```

The `m=4` census checks 216 configurations and accepts 50; their component
cycle counts are 2, 4, or 6. The `m=6` census checks 162,000 and accepts
34,640, with cycle counts `0,1,2,3,4,5,6,7,9`. These normalizations use
coordinate relabeling only, not graph automorphisms.

## Failure of obstruction

All three component counts retain aligned but separate local/scalar controls:

- verified Wave 36 connected `q=0` core for `kappa=1`;
- two enumerated 18-vertex `q=0` components for `kappa=2`;
- three enumerated 12-vertex `q=4` components and an exact residual scalar
  control at total `q=12` for `kappa=3`.

The canonical Wave 40 rank-11 all-`222` replay checks all 262,144 endpoint
masks. Its 37,378 triangle-free lifts all have components `[12,24]` and
`4<=q<=14`, so the restricted `kappa=2` lane positively survives.

No simultaneous 60-column `B`, compatible `A_Y`, endpoint graph, or
contradiction is produced. Status is `DERIVED_INCONCLUSIVE`; the endpoint and
Conway-99 remain `UNKNOWN`.
