# Wave156 late four-root feedback verification

Verdict: **VERIFIED with finite scope**.

The clean-room verifier independently reconstructed the late root-mask 3, 12,
and 13 covariance directions and replayed every retained exact equality on
the five- and eight-cut rational witnesses.  Each witness passes:

- 170 Wave44 equalities;
- 208 deletion equalities;
- 5,384 marked equalities;
- 2,211 ordered-edge and 3,828 ordered-nonedge moment entries;
- two active scalar cuts;
- 10,312 exact equalities total, with exact full modular column rank 886.

The mask-13 principal minor on flags 181 and 6181 was independently recovered
with a strictly negative determinant.  The later mask-3, mask-12, and mask-13
directions for both rational witnesses also replay to their exact negative
integer values.

The first simplified mask-12 direction `(1,-1)` on flags 5428 and 6324 gives

```text
320166 + x7[7864]
  + 6*x8[2022000] - x8[5691760] - x8[14332512]
  + x8[15434592] - 2*x8[23804464] + 2*x8[51173472]
  - x8[51205216] - x8[127242964] - x8[144594160] >= 0.
```

It has the exact positive value

```text
4877445335571096995366917775406 / 2619572513456614590392509237
```

on the eight-cut witness.  Thus that same pseudowitness exactly establishes
feasibility of the retained **nine-cut finite relaxation**.

A second serialization appeared only after the evidence freeze closed, so its
bytes were not inspected.  Independently deriving its `(1,-1)` direction from
the already frozen mask-12 principal entries gives

```text
18711 + 6*x8[2022000] - 2*x8[5683824] >= 0,
```

which the eight-cut witness violates exactly.  Therefore the ten-cut finite
relaxation remains **UNKNOWN**.

All HiGHS statuses are diagnostic only.  These certificates concern rational
pseudowitnesses for finite relaxations.  They do not prove endpoint
infeasibility, construct a graph, improve the `n3` bound, or resolve
Conway-99.

## Reproduce

```powershell
python verification/wave156-four-root-late-feedback/independent_verify.py `
  --verify verification/wave156-four-root-late-feedback/exact-results.json

python -m unittest discover `
  -s verification/wave156-four-root-late-feedback -p "test_*.py" -v
```
