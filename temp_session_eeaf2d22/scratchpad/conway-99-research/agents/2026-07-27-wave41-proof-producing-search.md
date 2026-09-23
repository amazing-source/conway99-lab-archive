# Wave 41 construction agent: proof-producing search

## Assignment

Audit and advance the strongest proof-producing computational route toward
resolving Conway-99: an unrestricted full-target exact solve or the 33-case
prism-free endpoint queue. Preserve exact commands and artifacts, never treat
a timeout or unchecked `UNSAT` as proof, and do not self-verify discoveries.

## Verdict

No graph, full assignment, checked endpoint-case UNSAT proof, new failed
polarity, endpoint exclusion, or general upper-bound improvement was found.
Endpoint proof coverage remains exactly `0/33`.

The strongest practical computational route remains the 33-case endpoint
queue with exact lazy prism separation. The unrestricted rooted formula is
smaller, but even prior ten-second Exact runs ended in checked
`NO CONCLUSION`; moreover it does not directly impose the global prism-free
endpoint. The monolithic complete endpoint formula is blocked by more than
24 billion residual-only prism clauses.

## Material advance

I extracted the entire generalized-unit propagation closure of the published
refined branch-15 OPB. The candidate certificate is bound to the existing
compressed and raw hashes and records every source line:

```text
total forced variables:        830
forced primary edge variables: 174
positive / negative primary:   7 / 167
unfixed primary variables:     3,312
contradiction:                 none
```

This exactly reproduces Exact's earlier parser-level count of 830 unit
literals. It expands the public proof-producing reduction beyond the single
previously isolated `x187=0` consequence, but the whole closure requires
independent replay before promotion.

The residual formula has 574,351 open constraints, including 2,975 with
exactly one residual slack unit. I tested both polarities of the 32 primary
variables with highest incidence in those tight constraints. None failed.
Some positive polarities forced 92--112 additional variables, supplying
useful branching pressure, but all 64 probes ended at noncontradictory fixed
points and therefore have no SAT meaning.

## Infrastructure result

The local virtual environment supplies PySAT backends for CaDiCaL, Glucose,
Gluecard, Kissat, Lingeling, Maple, MergeSat, MiniCard, and MiniSat. They are
discovery solvers here, not an accepted proof chain for the 5,838 native
pseudo-Boolean cardinality rows.

Exact, VeriPB, and CakePB remain pinned by the existing calibration. A fresh
WSL shell/tool recheck did not complete within two bounded probes under severe
memory pressure, so the tools are recorded as previously pinned and used but
not rechecked in this run. No new target solver was launched.

Two old embedded scouts remained CPU-active during a two-second sample and
still had no output. They were not touched. Since their scripts do not journal
per case, their live state cannot establish any completed prefix.

## Recommended next proof-producing move

1. Preserve or replace the two legacy scouts with a case-owned atomic runner
   that journals after every refined case.
2. Start with branch 15 because its OPB and exact propagation closure are
   already frozen.
3. Run solve--decode--global-prism-oracle iterations, accumulating only
   independently rederived cuts.
4. For terminal `UNSAT`, retain the raw proof, strict VeriPB replay, kernel
   elaboration/replay, and CakePB conclusion.
5. For terminal `SAT`, retain the complete 99-vertex assignment and require an
   independent SRG and exhaustive prism-free check.

The negative shallow-propagation result is important: a breakthrough now
appears to require real branching, a stronger mathematical reduction, or a
much better global-prism encoding—not another round of unit propagation.

## Artifacts

- `attempts/wave41-proof-producing-search/branch-15-propagation-certificate.json`
- `attempts/wave41-proof-producing-search/branch-15-residual-profile.json`
- `attempts/wave41-proof-producing-search/branch-15-failed-literal-scout.json`
- `attempts/wave41-proof-producing-search/solver-infrastructure.json`
- `attempts/wave41-proof-producing-search/failed-routes.md`
- `attempts/wave41-proof-producing-search/run-report.yaml`
