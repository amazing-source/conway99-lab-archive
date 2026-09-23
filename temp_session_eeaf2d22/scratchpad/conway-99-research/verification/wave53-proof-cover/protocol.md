# Wave 53 proof-cover verification protocol

Freeze time: `2026-07-27T19:49:33Z`

Role: independent verifier under the repository `AGENTS.md`.

## Frozen scope

Verify, without importing `attempts/wave53-proof-cover/*.py`, whether:

1. the normalized endpoint space has exactly 10,395 labelled
   matching/candidate states and 78 exact oriented-stabilizer orbits;
2. the endpoint units split those orbits into 33 compatible cases of total
   weight 6,644 and 45 incompatible orbits of total weight 3,751;
3. every recorded endpoint unit, parent unit, refinement literal, orbit
   representative, stabilizer size, and orbit weight agrees with an
   independent reconstruction;
4. the coordinate relabellings used for orbit reduction are the full
   stabilizers of the frozen local scaffold, not assumed automorphisms of a
   completed graph;
5. `branch15 AND x187=0` is the exact byte-level complement shard obtained
   from the pinned branch-15 gzip source by changing only the declared
   constraint count and appending `+1 ~x187 >= 1 ;`;
6. the retained Exact transcript is nonterminal and fresh bounded
   Exact/VeriPB/CakePB executions, when physical free memory is at least 15%,
   have their exact statuses recorded;
7. a checked `VERIFIED NO CONCLUSION` transcript contributes zero UNSAT case
   coverage, leaving complete-case coverage `0/33` and the endpoint
   `UNKNOWN`; and
8. the input freeze, discovery manifest, raw/gzip mapping, and report schemas
   contain no stale or omitted material inputs.

## Frozen independent inputs

```text
58c4994ff0eef9c5e1702840f791d1400c3da71b445e3c217e3704c5e70de172  verification/n3-joint-cover/n3-joint-cover.json
fd9a14193365bf40d3d7bcbe53d56c6f1ffa8a93ca63d5b68506c3354f3b9f8a  verification/n3-refined-cover/n3-refined-cover.json
7551c7b9d956705e41f9feb42d76d3bb5ab60dab0b46416fa9c0e58e5346a46a  attempts/wave35-n3-upper-triple-overlap/root-endpoint-reduction.json
2039681ef17eafea7ace392682317d1baf250585d35474fe7dafa35a3cbca3f3  verification/wave37-rooted-branches/independent_check.py
2de85c3f73d4b12a579b281c10171a47c12e26a323ecdf9617c1a842a81d8bf2  attempts/wave38-solver-harvest/coverage-plan.json
2aa691682aa434d1166a98bf4af820652187ffe664911b8aa112104831fe8f6c  verification/wave38-solver-harvest/independent-results.json
3a6d4181445a2bdd7859faa0b493376891b4498eb0987989dcdcdc4b8ffe97d6  attempts/wave37-proof-producing-endpoint/branch-15-formula.json
7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e  attempts/wave37-proof-producing-endpoint/branch-15.opb.gz
3afc665de9d8d0e5a5a4dab6b600db1e5b726ef1dfba685eeba92c80da1df5e4  verification/wave39-proof-solver/exact-results.json
```

The discovery package and its agent report are comparison targets, not
trusted inputs. The uncompressed Wave 53 OPB is likewise checked against both
the source gzip and the published Wave 53 gzip rather than trusted directly.

## Status gates

- `VERIFIED` is available only for exact scoped facts independently
  reconstructed or replayed.
- `VERIFIED NO CONCLUSION` means the proof transcript is valid but derives no
  terminal contradiction or model. Its mathematical and case-coverage
  contribution is exactly zero.
- No complete refined case is `UNSAT` unless a terminal proof for the whole
  case is independently replayed.
- The endpoint stays `UNKNOWN` unless all 33 complete cases are closed or an
  independently checked graph is produced.
- A resource-bound tool run is skipped or aborted if free physical memory
  would be below the frozen 15% reserve.
