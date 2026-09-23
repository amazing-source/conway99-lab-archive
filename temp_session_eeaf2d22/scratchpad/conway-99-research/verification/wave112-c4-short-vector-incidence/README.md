# Wave 112 clean-room verification

Verdict: **VERIFIED, conditional on the frozen previously verified
short-vector and rank-28 inputs**.

The independent checker confirms:

- exactly 2,079 induced four-cycles in an `srg(99,14,1,2)`;
- alternating-cycle lower bounds `21,20,18,26` for norm 14, norm 16,
  norm-18 `h=0`, and norm-18 `h=1`;
- `N14,N16,N18` are oriented counts, so antipodal parity strengthens the raw
  pigeonhole ceiling 51 to 52 oriented occurrences, or 26 antipodal pairs;
- a universal cap of 25 antipodal extensions would contradict the rank-28
  total 5,868;
- the rooted outside partition is exactly `51,20,20,4`, and an `h=0` side of
  size `7,8,9` chooses four one-opposite-anchor vertices plus `1,2,3`
  neither-anchor vertices.

The four-cycles are induced: if the two common neighbours of a nonedge were
adjacent, that adjacent pair would have at least two common neighbours,
contradicting `lambda=1`.  In the norm-18 `h=1` lane the same-sign edge is
not counted; at most one of the 62 pair incidences can land on that adjacent
pair, forcing at least 26 codegree-two nonadjacent pairs.

The cap of 25 is **not proved**.  Rank 28, Conway-99, and literature novelty
remain `UNKNOWN`.

Reproduce:

```powershell
python -B verification\wave112-c4-short-vector-incidence\independent_check.py `
  --verify verification\wave112-c4-short-vector-incidence\independent-results.json
python -B -m unittest discover `
  -s verification\wave112-c4-short-vector-incidence -p "test_*.py" -v
```
