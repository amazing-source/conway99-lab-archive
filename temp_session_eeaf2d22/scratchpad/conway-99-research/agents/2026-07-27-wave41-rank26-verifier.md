---
role: verifier
date_utc: 2026-07-27T05:57:01Z
git_commit: 4f1754a28723a8e0e4ea3025312cd264b1b117d2
claim_label: VERIFIED
scope: >
  Independently exclude rank 25 for all seven even-part edge types, compare
  only after implementation freeze, and compose with the separately frozen
  four-type all-odd verifier to cover all eleven partitions of six.
inputs:
  verification/wave40-exact-coupling-model/independent-results.json: ff7916d0f5c74c47c8d7787c5cbcc84785cbccd3644d8d03d73e47b73908c0f5
  attempts/wave41-evenpart-equality/exact-results.json: 8a9e58aaa1073ae4a87e183f904ce7f43eaa620bbac5a6f5d1f8445dd795dc85
  verification/wave41-multiedge-rank-packing/independent-results.json: 20cfac8928e1a9d52a586a833d8e52cc7f64f7998bdd641467ded5121e2da133
method: >
  Freeze Wave 39/40 premises; independently derive the singular Schur
  equality condition for the full 39-block and cubic core Laplacian;
  exhaust every minimum-projection permutation, canonical right kernel and
  equality target, and all 10,395 labelled Z matchings per kernel; run dense
  rank and positive hostile controls; freeze; then compare discovery and
  compose with the finalized all-odd verifier.
command: |
  .\.venv\Scripts\python.exe -B -m unittest discover -s verification\wave41-evenpart-equality -p "test_*.py" -v
  .\.venv\Scripts\python.exe -B verification\wave41-evenpart-equality\comparison_check.py --verify verification\wave41-evenpart-equality\discovery-comparison.json
  .\.venv\Scripts\python.exe -B -m unittest discover -s attempts\wave41-evenpart-equality -p "test_*.py" -v
  .\.venv\Scripts\python.exe -B -m unittest discover -s verification\wave41-multiedge-rank-packing -p "test_*.py" -v
outputs:
  verification/wave41-evenpart-equality/independent-results.json: ec371dad71c794d57d4e27b21d17b08fac1d17e22167749ef797d950c18299e4
  verification/wave41-evenpart-equality/discovery-comparison.json: 6ece1335fa595e4feed57b45cf63e6229697d0f410b2ebae1c32cde9e1cdcc1c
limitations:
  - No graph is constructed and Conway-99 existence remains UNKNOWN.
  - The endpoint n3=4158 remains UNKNOWN.
  - No general upper-bound improvement below 4158 is proved.
  - Literature novelty and priority remain UNKNOWN.
---

# Result

The seven even-part types contain 164,928 minimum-projection permutations,
52 distinct right kernels, and 164,278 equality targets. Exactly 540,540
kernel/matching evaluations cover all 10,395 labelled third-fibre matchings
per kernel. Zero rank-25 equality case survives.

The independent counts agree exactly with the frozen discovery package.
The separately frozen verifier excludes rank 25 for the remaining four
all-odd types. These disjoint families exhaust all eleven positive partitions
of six. Therefore:

```text
rank_F7(M)>=26.  VERIFIED
```

Conway-99, `n3=4158`, improvement below 4158, construction, novelty, and
priority remain outside the theorem and retain their conservative status.
