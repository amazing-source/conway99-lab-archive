# Wave 38 complete endpoint construction

Status: `CANDIDATE/UNKNOWN`. No target formula was solved, no graph was found,
and no UNSAT certificate was produced.

This package closes the **encoding-scope** gap left by Waves 36--37. Those
waves added exact clauses only for prisms meeting six triangles fixed in one
rooted parent branch. Wave 38 specifies a clause for every labelled
triangular prism compatible with the complete 99-vertex rooted scaffold and
provides an exhaustive separation oracle for practical solve--cut--check
iterations.

This is not a new upper bound. Until all 33 cases are closed by checked UNSAT
proofs, the endpoint `n3=4158`, Conway-99, and the bound improvement all remain
`UNKNOWN`.

## Exact scope

The normalized `N3` cover and endpoint units leave exactly these 33 refined
cases:

```text
parent 4:  15,16,17,18
parent 5:  19,20,21,22
parent 8:  36,37,38,39,40,41
parent 10: 50,51,52,53,54,55,56,57
parent 12: 68,69,70,71,72,73,74,75,76,77,78
```

No automorphism of a completed graph is assumed. The only relabeling is the
already verified normalization and its exact stabilizer-orbit cover.

For two disjoint triples `T` and `U` and one of their six perfect matchings,
the static schema forbids simultaneous presence of:

- the three edges of `T`;
- the three edges of `U`; and
- the three matching edges between them.

Fixed scaffold edges are evaluated exactly. Fixed nonedges discard an
impossible pattern; fixed edges disappear from the clause; residual edges
become the original variables `x1,...,x3486`.

These positive-edge clauses are exact inside the base SRG encoding. If an
extra unmatched cross edge were present, one edge of a triangle would have
two common neighbors, contradicting `lambda=1`. The six-vertex exhaustive test
checks all `2^15` graphs and confirms that the nine-edge prism pattern has no
proper supergraph satisfying the required adjacent-pair common-neighbor
bound.

## Why the static formula is not the practical route

The rooted scaffold has exactly:

```text
fixed root triangles:                       7
coordinate plus two-residual candidates:  924
residual-only candidates:               95,284
total potential triangles:              96,215
```

Even the residual-only prism subfamily contains exactly

```text
60 * binomial(84,6) = 24,388,892,640
```

labelled clauses before branch simplification. The coarse all-triangle-pair
upper bound is `27,771,690,030`. A monolithic OPB would therefore be far too
large for the current machine. The static exporter is implemented for
completeness and deliberately requires an explicit size acknowledgement; it
was not run.

## Exact lazy separation

The practical route is finite and exact:

1. Export one refined branch with the cumulative cut pool.
2. Solve it.
3. If SAT, decode the complete edge-list candidate.
4. Independently check the SRG parameters.
5. Exhaustively enumerate all graph triangles and all disjoint triangle
   pairs. Emit a blocking clause for every induced prism found.
6. Strictly rederive each cut from its recorded two triangles and perfect
   matching, merge it into the cumulative pool, and repeat.
7. Promote only a checked prism-free SRG witness or a checked UNSAT proof.

The loop terminates in principle because every cut removes at least the
current labelled prism-containing assignment and the assignment space is
finite. A timeout, partial cut pool, solver exit code, or exported formula is
not a certificate.

An UNSAT proof from an intermediate cut pool is sound: every admitted cut is
a direct logical consequence of `P=0`. A SAT result is terminal only after the
oracle reports zero prisms and the independent SRG checker accepts the graph.

## Reproduce the lightweight evidence

```powershell
.\.venv\Scripts\python.exe -B attempts\wave38-complete-endpoint\export_complete_endpoint.py `
  --inventory `
  --output attempts\wave38-complete-endpoint\static-schema-estimate.json

.\.venv\Scripts\python.exe -B attempts\wave38-complete-endpoint\prism_oracle.py `
  --candidate attempts\wave38-complete-endpoint\fixture-residual-prism.json `
  --catalog attempts\wave38-complete-endpoint\fixture-residual-prism-cuts.json

.\.venv\Scripts\python.exe -B attempts\wave38-complete-endpoint\prism_oracle.py `
  --candidate attempts\wave38-complete-endpoint\fixture-residual-prism.json `
  --catalog attempts\wave38-complete-endpoint\fixture-residual-prism-cuts.json `
  --verify-only

.\.venv\Scripts\python.exe -B attempts\wave38-complete-endpoint\cut_pool.py `
  --catalog attempts\wave38-complete-endpoint\fixture-residual-prism-cuts.json `
  --pool attempts\wave38-complete-endpoint\fixture-cut-pool.json `
  --verify-only

.\.venv\Scripts\python.exe -B attempts\wave38-complete-endpoint\cut_pool.py `
  --catalog attempts\wave38-complete-endpoint\fixture-residual-prism-cuts.json `
  --output attempts\wave38-complete-endpoint\fixture-cut-pool.json

.\.venv\Scripts\python.exe -B attempts\wave38-complete-endpoint\audit_package.py `
  --output attempts\wave38-complete-endpoint\construction-audit.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave38-complete-endpoint -p "test_*.py" -v
```

Expected discovery result: `12` tests pass. The fixture is intentionally not
an SRG; it is a six-vertex residual prism embedded in a 99-vertex edge-list
container so that the exact witness-to-cut path can be replayed cheaply.

## Export one lazy-cut OPB candidate

The following builds the same exact native-cardinality SRG base as Wave 37,
adds the endpoint units and one of the 33 refined cases, then appends every
strictly validated clause in the cumulative pool:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave38-complete-endpoint\export_complete_endpoint.py `
  --branch-opb `
  --refined-branch 15 `
  --cut-catalog path\to\cumulative-cut-pool.json `
  --opb path\to\branch-15-iteration.opb `
  --metadata path\to\branch-15-iteration.json
```

The OPB is a `CANDIDATE_FORMULA_ONLY`. Proof-producing solving and independent
proof replay must use the project's pinned Exact/VeriPB/CakePB toolchain.

## Static exporter guard

`--static-complete-opb` implements the complete monolithic stream. It refuses
to start unless the caller passes:

```text
--acknowledge-static-size I_ACKNOWLEDGE_MORE_THAN_24_BILLION_STATIC_CLAUSES
```

This is documentation of an exact fallback, not a recommendation to run it on
the present host. Generated OPBs, candidates, iteration catalogs, solver
records, and temporary files are ignored until a terminal artifact is
deliberately packaged.

## Promotion boundary

- `SAT` plus one or more cuts: `UNKNOWN`.
- zero-prism candidate without independent SRG validation: `CANDIDATE`.
- `UNSAT` without retained proof and replay: `UNKNOWN`.
- one checked UNSAT case: only that refined case is closed.
- all 33 checked UNSAT cases: endpoint `n3=4158` is excluded, giving the new
  general bound `n3<=4155`.
- checked prism-free SRG witness: Conway-99 is resolved in the opposite
  direction and must receive independent external scrutiny before any claim.
