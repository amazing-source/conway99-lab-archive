# Wave 81 graphical refinement: independent verification

Status: `VERIFIED`, conditional on the previously verified Wave 81
outside type-degree histogram domain.

This second-verifier package freezes the 43 `t=0` and seven `t=1`
histogram triples, reconstructs the degree sequences of all six
type-pair subgraphs, and checks each sequence by two independent exact
criteria. It confirms:

- exactly three `t=0` rows fail;
- each failure occurs only for the `X0` induced graph;
- the three failed degree sequences are
  `[4,3,1,1,1,0^6]`, `[4,2,2,2,0^7]`, and
  `[3,3,3,1,0^7]`;
- no `t=1` row is removed;
- the final necessary degree-level census is 40 plus seven.

The result is only an individual-subgraph graphicality filter. It does
not realize all six subgraphs simultaneously, construct an outside
graph, or exclude the norm-16 branch. Conway-99 and novelty remain
`UNKNOWN`.

## Replay

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave81-norm16-graphical-refinement\independent_check.py `
  --verify `
  verification\wave81-norm16-graphical-refinement\independent-results.json

.\.venv\Scripts\python.exe -B -m unittest -v `
  verification\wave81-norm16-graphical-refinement\test_independent_check.py
```

The checker uses only the Python standard library and refuses to run
below 15% free physical memory.
