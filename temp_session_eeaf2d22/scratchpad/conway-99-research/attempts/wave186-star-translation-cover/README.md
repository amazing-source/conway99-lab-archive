# Wave 186: star-translation cover amplification

This package strengthens the conditional rank-11 endpoint circuit bound by
using the seven-column star relations as circuit-elimination moves.

Let `Q` be the number of projective short circuits that cross-realize at
least one graph nonedge.  Under the verified conditional endpoint model,

```text
Q>=3696.
```

The 693 edge-isolated projective circuits are disjoint from this family, so

```text
projective circuits of weights 4..9 >=4389,
B_4+B_5+B_6+B_7+B_8+B_9>=8778.
```

In particular, Wave 181's former equality face `Q=2079` is impossible.  The
root-gluing developments in Waves 182--185 remain valid conditional
implications, but their shared antecedent is now excluded.

The proof is analytic.  It combines exact multiplicity-two and
multiplicity-three circuit shapes, star-translation, private labels in a
minimal set cover, and a two-line capacity inequality.  No graph or code is
searched for.

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave186-star-translation-cover\exact_check.py --verify `
  attempts\wave186-star-translation-cover\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v `
  attempts\wave186-star-translation-cover\test_exact_check.py
```

This does not exclude the rank-11 endpoint itself or resolve Conway 99.
