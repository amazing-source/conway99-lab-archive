# Wave 21 exact six-/seven-vertex count feasibility audit

Verdict: **rigorous inconclusive exhaustion of the encoded published count
identities.**  The complete affine, nonnegativity, integrality, and congruence
system does not improve or contradict the independently audited conditional
bound `n3>=705`.

The audit also finds one exact omission in the supporting deck equations of
arXiv:2508.03377v2: the printed `m7(n-5)` equation is missing `+n23`.
This is retained as a raw source failure and repaired only in a separately
named checker path.  The correction does not change any `n3` feasibility
conclusion.

```yaml
role: proof_b
date_utc: 2026-07-23T17:19:05Z
git_commit: 74af1fa495971d04c7363ec05aa77ef15857b04a
claim_label: DERIVED
scope: >
  Exact specialization at n=99,k=14 of all 62 published induced
  six-vertex counts and all 19 published Hamiltonian seven-vertex
  counts, including nonnegativity, integrality, congruence, supporting
  deck identities, and independent local graph-index alignment.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  CONJECTURE.md: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  agents/2026-07-23-wave20-global-schur.md: 64352e1d96ed9a924e075c2d0659be8de887751194068a14b096e112a9320632
  arxiv:2409.10620v1_archive: 9e31eb63e878531124cb20df306698827b93057b4ef9feed207654aea8f31112
  arxiv:2409.10620v1_tex: f6b4fc65043f825e1888b3aff4552c883bb38ba9a15745d1822037ceba1800df
  arxiv:2508.03377v2_archive: f8429d2f839267e2aaf98b04451cb2f0252c0353f75bee6ec6e6947eab0d5834
  arxiv:2508.03377v2_tex: 823bcaf636a99f6655af453b2a910b9953338db980480572bca81730cfa1b44f
  arxiv:2511.06572v1_archive: 10f8d9ea09dc72f4ca6bce4e9427ff1df32718d2978bb35a16db1af3c27cc39a
  arxiv:2511.06572v1_tex: 0b06fdc1c2951a344592c6af23abd133c4a8a68d717f199e7a0e2d7ceb909d0a
method: >
  Transcribe every affine count with Fraction arithmetic; verify the
  published four-to-five, five-to-six, and six-to-seven identities;
  independently enumerate locally admissible unlabeled graphs and
  reconstruct vertex-deletion decks; derive the exact integer feasible
  set and exhaust it without floating point or a solver.
command: |
  .venv\Scripts\python.exe -B -m unittest -v attempts\wave21-six-vertex-lp\test_exact_check.py
  .venv\Scripts\python.exe -B attempts\wave21-six-vertex-lp\exact_check.py --output attempts\wave21-six-vertex-lp\exact-results.json
  .venv\Scripts\python.exe -B attempts\wave21-six-vertex-lp\exact_check.py --verify attempts\wave21-six-vertex-lp\exact-results.json
outputs:
  exact_checker: attempts/wave21-six-vertex-lp/exact_check.py
  exact_checker_sha256: 0dd44ca37ca21aeaa757f3b2d7f7f9639907f22b95da39472ed9d836027a94a3
  hostile_tests: attempts/wave21-six-vertex-lp/test_exact_check.py
  hostile_tests_sha256: f51ecc8e88e9f231dfab74cf15d4d9ed23d5937bc66c61ef458ecfe24de571b5
  exact_results: attempts/wave21-six-vertex-lp/exact-results.json
  exact_results_sha256: 5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b
  focused_tests: "16/16 PASS"
  exact_json_replay: PASS_BYTE_IDENTICAL
limitations: >
  This is a proof-agent audit, not an independent verifier promotion.
  Formula feasibility is only a necessary condition for a global target
  graph.  The seven-vertex source enumerates Hamiltonian types, not every
  order-seven induced type.  No target-resolution or novelty claim is
  made, and the source equation repair needs independent review.
```

## 1. Sources and definition alignment

The exact primary sources were downloaded from arXiv on 2026-07-23:

- [hexagon paper, arXiv:2409.10620v1](https://arxiv.org/abs/2409.10620v1);
- [six-vertex paper, arXiv:2508.03377v2](https://arxiv.org/abs/2508.03377v2);
- [Hamiltonian seven-vertex paper, arXiv:2511.06572v1](https://arxiv.org/abs/2511.06572v1).

The hashes in the run header pin both each source archive and its top-level
TeX.  The checker transcribes the v2 six-vertex summary at TeX lines 345--407
and the v1 seven-vertex summary at lines 177--195.

The six-vertex paper defines `N_i` by its figure and `n_i` as the number of
induced copies.  The `N3` cell in `all_six_vertex.jpg` depicts two disjoint
triangles with two cross edges.  The independent deck alignment recovers the
same source index and verifies exactly:

```text
two vertex-disjoint triangles;
two cross edges;
the cross edges form a matching;
eight total edges.
```

Thus this source's `n3` is the project's induced `N3` count.  It is **not**
the number of independent triples.

## 2. Independent finite index audit

Any induced subgraph of an `srg(n,k,1,2)` must satisfy:

```text
an adjacent pair has at most 1 common neighbor inside the subgraph;
a nonadjacent pair has at most 2 common neighbors inside the subgraph.
```

The checker enumerates every labeled graph mask and quotients by all vertex
permutations.  It independently obtains:

| order/type | locally admissible isomorphism classes |
|---|---:|
| 4 vertices | 9 |
| 5 vertices | 21 |
| 6 vertices | 62 |
| 7 vertices, Hamiltonian | 19 |

For order seven it fixes one labeled cycle
`0-1-2-3-4-5-6-0`, enumerates all subsets of the fourteen remaining chords,
and then canonicalizes.  This is complete for Hamiltonian graphs: every such
graph has a Hamiltonian cycle that can be relabeled to the fixed one.  No
automorphism of the unknown target is assumed.

The Hamiltonian edge-count distribution is

```text
7^1, 8^2, 9^7, 10^7, 11^2,
```

agreeing with one bare `C7` plus the eighteen types in the source figure.

The checker next reconstructs every vertex-deletion deck.  The nine
four-to-five rows uniquely map all `L_i` and `M_i` indices to canonical graph
masks.  Those fixed `M_i` indices then uniquely map all 62 `N_i` after the
single explicit correction in the next section.

This audit establishes source-index consistency and local census
completeness.  It does not assert global embeddability.

## 3. One raw source equation is false as printed

The paper states that the five-to-six equations count the six ways to delete
one vertex from an induced six-vertex graph.  Therefore each `N_j` column
must have coefficient sum six.

In the printed v2 TeX:

```text
61 columns sum to 6;
the N23 column sums to 5.
```

Substitution of the paper's own affine formulas into the printed equations
gives:

```text
20 equations: residual 0;
m7(n-5) equation: residual n23.
```

Independent graph-deck reconstruction identifies the missing sixth card
uniquely as `M7`.  The explicit correction is:

```text
printed m7(n-5) right-hand side  +  n23.
```

After that correction:

```text
all 21 symbolic deck identities pass;
all 62 deletion columns sum to 6;
all 62 source indices map bijectively to canonical graph masks.
```

The raw table remains unchanged in `FIVE_TO_SIX_RAW`; the checker applies the
repair only in `corrected_five_to_six()`.  This follows the verifier rule that
a defect cannot be silently repaired.  It is best classified as a supporting
equation omission, not a target contradiction: the corrected identity is the
actual vertex-deletion deck and is satisfied by the published count formulas.

## 4. Complete six-vertex feasibility

At `n=99,k=14`, each published count has the form

```text
ni = ai + bi*n3
```

with exact rational coefficients.  The full table passes the aggregate
identity

```text
sum_{i=1}^{62} ni = binom(99,6) = 1,120,529,256,
sum_{i=1}^{62} bi = 0.
```

The fractional coefficients give the exact simultaneous integrality
condition

```text
n3 = 0 (mod 3).
```

Simultaneous nonnegativity of all 62 counts gives the exact rational
interval

```text
0 <= n3 <= 4158.
```

The lower facet is attained by both

```text
n3=n3,  n4=2n3.
```

The tight upper facet is

```text
n1 = 1386 - n3/3 >= 0.
```

The next strongest upper inequality, from `n5`, is only `n3<=20790`.
Combining integrality and nonnegativity, the complete six-vertex feasible set
is therefore

```text
n3 in {0,3,6,...,4158}.                              (1)
```

This is an exact analytical envelope followed by a byte-recorded enumeration
of all 1,387 values, not a floating-point LP sample.

## 5. Complete Hamiltonian seven-vertex feasibility

Write `y=h11`.  Each published Hamiltonian count is

```text
hi = ci + ai*n3 + bi*y.
```

All eighteen displayed derivation identities pass symbolically against the
five- and six-vertex formulas.  Simultaneous integrality of the nineteen
counts is exactly

```text
y = 0 (mod 4).                                       (2)
```

For every `n3` in (1), simultaneous nonnegativity is exactly

```text
ceil_to_multiple_of_4(2*n3) <= y <= 4*n3.            (3)
```

The lower and upper facets are respectively

```text
h16 = y-2n3 >= 0,
h18 = n3-y/4 >= 0.
```

Every other Hamiltonian count inequality is redundant over (1)--(3).  The
universal exact choice

```text
y=4n3
```

is feasible for every `n3` in (1).  Hence the seven-vertex table removes no
six-vertex-feasible value.

At the incumbent frontier:

```text
n3=705;
1412 <= h11 <= 2820;
h11 = 0 (mod 4);
353 feasible h11 values.
```

More globally, all 1,152 values

```text
n3=705,708,...,4158
```

remain feasible.

## 6. Cycle-count collateral

The 2024 source and the six-vertex v2 table both give

```text
n12 = induced_C6 = 209286+n3.
```

Thus the incumbent `n3>=705` reproduces

```text
induced_C6 >= 209991.
```

This lane does not strengthen that bound.

For the seven-vertex source's induced `H0=C7` count,

```text
h0 = 1247400-10n3-h11.
```

At `n3=705`, the exact feasible `h11` interval gives

```text
1,237,530 <= h0 <= 1,238,938.
```

This is a collateral conditional range only.  The `h0>=0` constraint is not
active anywhere in (1)--(3) and supplies no obstruction.

## 7. Exhaustion result

Intersecting every encoded published count constraint with the audited
incumbent bound yields

```text
n3=705,708,...,4158;
for each n3, at least one and usually many feasible h11 values.
```

Therefore:

```text
stronger lower bound than 705:  none;
upper bound below 705:          none;
contradiction:                  none;
target resolution:             UNKNOWN;
novelty:                       not assessed.
```

The correct scientific result of this lane is a rigorous negative result:
the published six-vertex and Hamiltonian seven-vertex affine count systems,
even with all their integer and congruence information, do not obstruct the
remaining Conway-99 parameter range.

## 8. Reproduction and limitations

Run:

```powershell
.venv\Scripts\python.exe -B -m unittest -v attempts\wave21-six-vertex-lp\test_exact_check.py
.venv\Scripts\python.exe -B attempts\wave21-six-vertex-lp\exact_check.py --output attempts\wave21-six-vertex-lp\exact-results.json
.venv\Scripts\python.exe -B attempts\wave21-six-vertex-lp\exact_check.py --verify attempts\wave21-six-vertex-lp\exact-results.json
```

The implementation uses only `Fraction`, integers, and exhaustive finite graph
masks.  Sixteen tests include hostile mutations of the tight `n1` facet, the
`N23` repair row, the `N3`/`N4` index, and the `h11 mod 4` requirement.

The strongest self-objection is scope.  Internal consistency, deletion decks,
and exact formula feasibility do not independently re-prove every prose
derivation in the source papers.  More importantly, the seven-vertex source
lists only Hamiltonian types; additional non-Hamiltonian order-seven
relations, higher-order flag inequalities, or unpublished identities could
still constrain `n3`.  Conversely, a feasible count vector is not an
adjacency matrix and gives no construction.

Final status:

```text
raw printed m7 deck equation:                 REFUTED
explicit +n23 deck correction:                DERIVED
9/21/62/19 local class census:                DERIVED
complete encoded integer feasibility:         DERIVED
improvement beyond n3>=705:                   NONE
Conway srg(99,14,1,2):                        UNKNOWN
novelty:                                      NOT ASSESSED
```

