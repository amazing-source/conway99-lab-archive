# Wave 42 construction agent: branch-15 endpoint certificate

## Assignment

Advance the proof-producing endpoint route beyond Wave 41 for one exact
refined case, preferably branch 15, while retaining a graph, checked UNSAT
proof, or materially stronger replayable reduction. Do not disturb legacy
processes or promote solver status without a certificate.

## Verdict

I found a sound, exact branch-15 strengthening, but no terminal SAT or UNSAT
event. Branch 15 and `n3=4158` remain `UNKNOWN`; endpoint coverage is `0/33`.

## Material reduction

The published Wave 37 formula adds prism families for the six triangles fixed
by branch 15's parent case. Refined branch 15 additionally fixes `x2=1`.
Reconstructing the frozen lexicographic numbering gives

```text
x2 = edge((0,2),(0,4)),
```

which fixes the seventh full-vertex triangle `[1,15,17]`. Exhaustively
enumerating every compatible second triangle and matching produces 64,932
prism-blocking clauses: 132 of width three and 64,800 of width five. A complete
streaming scan finds zero exact row overlaps with the Wave 37 OPB.

After the SHA-bound Wave 41 closure, 31,154 clauses are already satisfied and
33,778 distinct active clauses remain. Both the raw and active catalogues are
retained as deterministic compressed OPB streams with explicit serialization.
The unsimplified catalogue is sound independently of the Wave 41 discovery
closure.

## Exact continuation result

Combined generalized-unit propagation reproduces the Wave 41 fixed point
exactly:

```text
forced variables:             830
forced primary variables:     174
delta-sourced derivations:       0
```

Both polarities of the prior 32 high-pressure primary variables were replayed.
All 64 probes remain noncontradictory, none changes relative to Wave 41, and
there are zero candidate implications. These fixed points are not SAT
witnesses.

## Evidence boundary

The new family covers only prisms using `[1,15,17]` as one triangle. A model of
the partial formula could still contain a prism with two unfixed triangles.
No target solver was launched, no long-running process was modified, and no
SAT assignment, terminal proof, checker replay, endpoint exclusion, upper
bound improvement, or global Conway resolution is claimed.

## Artifacts

- `attempts/wave42-endpoint-certificate/branch-15-seventh-triangle-result.json`
- `attempts/wave42-endpoint-certificate/branch-15-seventh-triangle-delta.opb.gz`
- `attempts/wave42-endpoint-certificate/branch-15-seventh-triangle-active-delta.opb.gz`
- `attempts/wave42-endpoint-certificate/branch-15-combined-propagation-certificate.json`
- `attempts/wave42-endpoint-certificate/branch-15-combined-failed-literal-scout.json`
- `attempts/wave42-endpoint-certificate/run-report.yaml`
