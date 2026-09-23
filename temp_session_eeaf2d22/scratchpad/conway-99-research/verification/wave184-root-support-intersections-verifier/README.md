# Wave 184 root-support intersection verification

Verdict: **VERIFIED_WITH_SCOPE**.

Conditional on the Wave 181 equality regime and the verified Waves
182--183 structure, this package independently verifies:

- distinct global-root supports meet in at most two vertices, and a
  two-vertex intersection is a graph edge;
- every root/internal-support-edge incidence produces a genuine projective
  weight-four circuit on four distinct outer-star columns;
- these circuits are injective across roots and graph edges and are
  disjoint from the 2,079 canonical nonedge conics;
- their exact count is `E=3*n6+7*n7`, with the incidence congruence forcing
  `E>=12`;
- consequently there are at least 2,091 projective weight-four circuits
  and `B4>=4182`.

No graph, code, or support configuration is enumerated.  There is no known
incompatible upper bound for `B4`; equality existence, rank 11, the
endpoint, and Conway-99 remain **UNKNOWN**.

Reproduce:

```powershell
python -B verification/wave184-root-support-intersections-verifier/independent_check.py
python -B -m unittest verification.wave184-root-support-intersections-verifier.test_independent_check
```
