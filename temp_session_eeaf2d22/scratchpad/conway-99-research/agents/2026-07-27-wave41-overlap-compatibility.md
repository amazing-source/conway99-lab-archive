# Wave 41 overlap-compatibility discovery lane

```yaml
role: construction
date_utc: 2026-07-27T05:10:34Z
git_commit: 4f1754a28723a8e0e4ea3025312cd264b1b117d2
claim_label: CANDIDATE
scope: one exact two-triangle overlap of the canonical rank-33 all-222 lift
inputs:
  - attempts/wave41-allquotient-lifts/exact-results.json
method: exact F7 elimination, explicit 19-vertex gluing, exhaustive balanced-column signature DP
command: .\.venv\Scripts\python.exe -B attempts\wave41-overlap-compatibility\exact_check.py --verify attempts\wave41-overlap-compatibility\exact-results.json
outputs:
  - attempts/wave41-overlap-compatibility/exact-results.json
limitations:
  - one overlap class only
  - individual columns, not a simultaneous B/H completion
  - no endpoint exclusion or upper-bound improvement
```

The bounded lane found a hostile positive control rather than a
contradiction. Two copies of the canonical rank-33 block agree on the
19-vertex overlap forced by adjacent base triangles. Even after exact
two-per-fibre balance and the individual common-neighbor support cap, the
twenty new border signatures can jointly span one dimension, so the raw
congruence lemma gives only rank 35.

This is retained because it prevents repeating the tempting but insufficient
argument that two rank-33 neighborhoods must automatically force rank 45.
The unresolved next step is simultaneous column coupling through the full
`B/H` equations or a complete census of overlap classes.
