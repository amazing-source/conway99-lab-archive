# Independent adversarial baseline for a Wave 19 `n3=60` closure audit

Verdict: **READY FOR COMPARISON / target status still UNKNOWN.**  The exact
SRG rectangle identity, its perfect-matching refinement, the complete local
component classification, the active-point local consequences, the outside
Gram equations, and all nine abstract `Z` types through three edges have
been derived and replayed independently.  Twenty-seven hostile tests pass.

This baseline is deliberately not a closure.  It neither catalogs all
residual-A point families nor all residual-B `(F,R,Z)` placements, and it
does not claim a binary outside-incidence factor is impossible.  Conditional
`n3=60`, Conway-99, and novelty remain `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T14:32:51Z
git_commit: f16ec3d49e5e7f7fde0a8f20ea324d6f49c5b24c
claim_label: DERIVED
scope: independent local, component, and outside-Gram baseline for adversarial verification of both conditional n3=60 residuals; no residual exclusion claimed
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  agents/2026-07-23-wave19-n3-60-structural.md: b2f90af07f34a6525ea35cdf4d392d95aea10fc319633cd17037d00145690744
  verification/2026-07-23-wave15-global-lift-audit.md: edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036
  verification/2026-07-23-wave16-n3-51-structural-audit.md: 99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6
  verification/n3-60-closure/2026-07-23T140227Z-preinspection-freeze.md: 05111263664277f446217fd43aa1b4b494be611285ea44cf2e643845dc43b34b
  verification/n3-60-closure/2026-07-23T140227Z-preinspection-freeze.sha256: 96ca641cb9a8b677abc9fbc7fd81298e4483d8863d6077225056f689f36554fd
method: direct SRG counting and block-matrix derivation; exhaustive standard-library enumeration of four-index identities, zero-or-two crossing shapes, local component partitions, Z types, outside moment histograms, and hostile mutations
command: |
  .venv\Scripts\python.exe -B verification\n3-60-closure\independent_baseline.py
  cd verification\n3-60-closure
  ..\..\.venv\Scripts\python.exe -B -m unittest -v test_independent_baseline.py
  cd ..\..
outputs:
  verification/n3-60-closure/independent_baseline.py: b223ac7ee4ac059d52b57acca7a0d85986d06f2be9d335e396dda50aa800c2db
  verification/n3-60-closure/test_independent_baseline.py: 7681d30fdc295fa3f996da676a5482484cb0a3a6ac0e8328d2d0810031e1966a
  rectangle_identity_cases: 17065
  local_component_length_multisets: 11
  abstract_Z_types_through_three_edges: 9
  independent_hostile_tests: "27/27 PASS"
  residual_A: UNKNOWN
  residual_B: UNKNOWN
  conditional_n3_60: UNKNOWN
  conway_99_target: UNKNOWN
  novelty: UNKNOWN
limitations: conditional on the frozen audited H/L and indexed-point framework rather than a raw 99-by-99 adjacency derivation; local component completeness is not global residual completeness; Z type enumeration is not labeled Z placement coverage; moment, entrywise, spectral, and PSD tests do not replace a verified binary factor or full block certificate; no Wave 17, Wave 18, alternate-frontier artifact, prospective alternate report, or closure catalog was inspected
```

The `git_commit` value was read directly from `.git/HEAD` and its referenced
file before the freeze was written.  No Git command or Git write was used.
The shared branch may move independently.

## 1. Source separation

The source boundary in the timestamped preinspection freeze was maintained.
In particular, no file under `attempts/wave19-alternate-frontier`, no
prospective alternate report, and no Wave 17 or Wave 18 content was opened,
searched, imported, or executed.

The checker is an independent standard-library module.  It imports no
discovery implementation and contains no submitted catalog count as a
control-flow premise.  The expected nine `Z` names and their public moment
rows occur only in the hostile tests; the program independently generates
the unlabeled graph types and recomputes the rows.

## 2. Exact SRG and rectangle identity

For the adjacency matrix `A` of an `srg(99,14,1,2)`,

```text
A^2=(14-2)I+(1-2)A+2J=12I-A+2J.             (1)
```

Thus the global eigenvalues are

```text
14^1, 3^54, (-4)^44.
```

Let `r_x` be adjacency row `x`.  For arbitrary vertices `a,b,c,d`, with
repetitions allowed, apply (1) to row differences:

```text
<r_a-r_b,r_c-r_d>
 =12(delta_ac-delta_ad-delta_bc+delta_bd)
  -A_ac+A_ad+A_bc-A_bd.                     (2)
```

For four distinct vertices only the alternating four cross-edge indicators
remain.  Dropping the Kronecker terms is unsound when indices repeat.
Changing either middle sign is also unsound.  The independent checker
compares the two sides for every ordered four-tuple in every simple graph
on one through four vertices: 17,065 exact cases pass.

Equation (2) is the algebraic rectangle identity used by this baseline.  It
does not assume that any of the four possible cross edges is present.

## 3. Rectangle matching refinement around an edge

Fix an original graph edge `uv`.  It has one common neighbor `w`.  Put

```text
A_u=N(u)\{v,w},
A_v=N(v)\{u,w}.
```

Each side has twelve vertices.  If `x in A_u`, then `x` is not adjacent to
`v`: otherwise `x` and `w` would be two common neighbors of the adjacent
pair `u,v`.  The nonadjacent pair `x,v` has exactly two common neighbors.
One is `u`; call the other `y`.  It lies in `A_v`.  It is unique.  Reversing
the roles proves that every vertex of `A_v` also has exactly one neighbor
in `A_u`.  Therefore:

```text
G[A_u,A_v] is a perfect matching with twelve edges.      (3)
```

This is stronger than a rectangle count.  The twelve opposite edges of the
induced rectangles through `uv` have pairwise distinct endpoints on both
sides.  A proposed local certificate that gives the right count but reuses
one endpoint fails.

There is a second independent-matching consequence for the active point
model.  Suppose indexed vertices `u,v` are adjacent but their active points
are disjoint.  They cannot have an indexed vertex `x` that is a meeting
neighbor of both.  If they did, `uvx` would be the unique graph triangle on
`ux`; but `ux` already lies in the active triangle labeling the meeting of
their points, forcing `v` into that active label and contradicting
disjointness.  Thus:

```text
N_meet(u) intersect N_meet(v) is empty.                  (4)
```

In residual B, points are edges of `F`.  Equation (4) says that the two
`F`-edges representing any disjoint actual graph edge form an induced
`2K2`, not merely two vertex-disjoint edges: no endpoint of one may be
joined in `F` to an endpoint of the other.  The checker distinguishes these
conditions and rejects the hostile added cross edge.

## 4. Complete local component classification

For any vertex `u`, the induced graph on its fourteen neighbors is
1-regular: an adjacent neighbor `x` has exactly one common neighbor with
`u`.  Hence `N(u)` is the matching of the seven unique graph triangles
through `u`.

For fixed `uv`, deleting the triangle pair `{v,w}` leaves a six-edge
matching on `A_u`; likewise there is a six-edge matching on `A_v`.  Add the
twelve-edge rectangle matching (3).  Every vertex now has degree two.
Every component is a cycle alternating a within-side triangle edge with a
cross-side rectangle edge.

A cycle must use an even number of side-switching rectangle edges to return
to its starting side.  Its total length is twice that even number, hence is
divisible by four.  The components use all 24 vertices.  The complete list
of component-length multisets is therefore the eleven partitions of 24
into multiples of four:

```text
4+4+4+4+4+4
4+4+4+4+8
4+4+4+12
4+4+8+8
4+4+16
4+8+12
4+20
8+8+8
8+16
12+12
24.
```

This classification is complete for the displayed local graph around one
edge.  It is not a classification of residual-A point families, cubic
graphs `F`, two-factors `R`, or full induced graphs `D`.

## 5. Active crossing components and local residual consequences

An active triangle label through `u` contributes its two other triangle
vertices as one of the within-side pairs above.  A crossing between active
labels records which of these remote vertices are joined by the rectangle
matching.  The matching property caps every active label-block at two
crossing edges.  The audited two-sided zero-or-two rule says every row and
column has degree zero or two.  Consequently every nonisolated crossing
component is an even bipartite cycle.

Independent exhaustive matrix enumeration gives:

| crossing size | exact nonzero shapes |
|---|---|
| `1 x q` | none |
| `2 x 2` | one `C4`, four edges |
| `2 x 3` | one `C4`, four edges |
| `3 x 3` | one `C4` or one `C6`, four or six edges |
| `4 x 4` | one `C4`, one `C6`, one `C8`, or two disjoint `C4`s |

The six-edge `3 x 3` crossing is genuinely legal under the local rule.  It
cannot be silently accepted at a size-two endpoint.

Let `M_u` be the four meeting neighbors of a size-two point `u`.  If
disjoint points `u,v` form a positive four-crossing actual edge, all four
active remote vertices on each side are consumed by (3), so:

```text
G[M_u,M_v] is a perfect matching of size four.           (5)
```

If their crossing is zero, then:

```text
e_G(M_u,M_v)=0.                                          (6)
```

Equations (4)-(6) apply to every residual-A positive-disjoint two-factor
edge, every residual-B `R` edge, and every residual-B `Z` edge with the
appropriate crossing count.  In residual B, they are placement-dependent
conditions on `D=L(F) union R union Z`.  A cycle-length multiset for `R`
cannot check them.

## 6. Outside Gram constraints

Write the full adjacency matrix in blocks:

```text
A = [ D  B ]
    [B^T C],
```

where `D=G[X]`, `B` is the binary `X`-to-outside incidence matrix, and `C`
is the outside induced graph.  The three blocks of (1) give:

```text
BB^T       = 12I-D+2J-D^2 =: M,                         (7)
DB+BC      = 2J-B,                                      (8)
B^TB+C^2   = 12I-C+2J.                                  (9)
```

Thus a proposed `D` must first satisfy:

- `M_xx=14-d_D(x)`;
- for adjacent `x,y`, `M_xy=1-|N_D(x) intersect N_D(y)|`;
- for nonadjacent `x,y`, `M_xy=2-|N_D(x) intersect N_D(y)|`;
- every entry is a nonnegative integer;
- `M` is positive semidefinite; and
- `M` has an actual binary factor with exactly `99-m` columns.

The last condition is strictly stronger than the preceding ones.  For
example,

```text
[1 2]
[2 4]
```

is nonnegative, integral, and positive semidefinite of rank one, but it
cannot be the Gram matrix of binary rows: two rows of weights one and four
cannot have intersection two.  The hostile suite checks that PSD is not
accepted as a binary-factor certificate.

If `D` is 6-regular of order `m`, then:

```text
M 1 = (2m-30) 1.
```

On a `D`-eigenvector perpendicular to `1` with eigenvalue `theta`,

```text
M` has eigenvalue 12-theta-theta^2
                  =(3-theta)(theta+4).                  (10)
```

Hence Gram PSD forces every nonprincipal `D` eigenvalue into `[-4,3]`.
The principal Gram eigenvalue is 24 for residual A (`m=27`) and 30 for
residual B with `Z` empty (`m=30`).

Let `a_z` be the outside column degrees.  From (7):

```text
sum_z a_z   =14m-sum_x d_D(x),
sum_z a_z^2 =1^T M 1
             =2m^2+12m-sum_x(d_D(x)^2+d_D(x)).
```

Writing `d_D(x)=6+s_x`, `T=sum s_x`, and `U=sum s_x^2` recovers:

```text
sum_z a_z   =8m-T,
sum_z a_z^2 =2m^2-30m-13T-U.                            (11)
```

For residual A, (11) forces 72 outside columns of degree exactly three.
That is a moment equality, not a binary factor or full lift.

## 7. Every abstract `Z` type through three edges

Independent generation of all simple graphs with no isolated support
vertices and at most three edges gives exactly:

```text
empty, K2, 2K2, P3, 3K2, P3+K2, P4, K1,3, K3.
```

The recomputed rows are:

| `Z` | `T` | `U` | `sum a_z` | `sum a_z^2` | histogram count |
|---|---:|---:|---:|---:|---:|
| empty | 0 | 0 | 240 | 900 | 1297 |
| `K2` | 2 | 2 | 238 | 872 | 354 |
| `2K2` | 4 | 4 | 236 | 844 | 69 |
| `P3` | 4 | 6 | 236 | 842 | 52 |
| `3K2` | 6 | 6 | 234 | 816 | 6 |
| `P3+K2` | 6 | 8 | 234 | 814 | 3 |
| `P4` | 6 | 10 | 234 | 812 | 2 |
| `K1,3` | 6 | 12 | 234 | 810 | 1 |
| `K3` | 6 | 12 | 234 | 810 | 1 |

The histogram counts are exact counts of bounded integer histograms, not
assignments or lifts.  `K1,3` and `K3` have identical `(T,U)` and identical
moment rows, proving concretely that moments do not identify the topology.
Even within one topology, (7) depends on the labeled placement through
`D^2`.  Therefore the nine-type list does not replace the all-placement
coverage required by the preinspection freeze.

## 8. Executable hostile coverage and failed runs

The 27 passing tests cover:

- all repeated-index and distinct-index rectangle cases;
- a missing Kronecker term and a sign mutation;
- the exact adjacent-edge matching parameters;
- all eleven local component partitions;
- exact small crossing shapes, one-sided-degree mutation, and legal `C6`;
- the induced-`2K2` refinement;
- positive, zero, and endpoint-reusing local rectangle patterns;
- strict point-family linearity, label multiplicity, duplicate values, and
  Berge-triangle rejection;
- strict two-factor degree checking;
- exact residual-A and residual-B moments;
- regular Gram eigenvalue formulas and target interval;
- PSD versus binary-factor separation;
- exact binary-factor replay and full-block order checking;
- independent enumeration of all nine `Z` types;
- all nine moment/histogram rows;
- a deliberately omitted topology; and
- the indistinguishable `K1,3`/`K3` moment mutation.

Two failed execution attempts are retained:

1. the first baseline run timed out after the initial histogram recursion
   explored too many states; it produced no output used as evidence.  The
   recursion was replaced by a bounded, parity-pruned dynamic program, after
   which the full baseline completed in under one second;
2. the first unittest command invoked the file from the repository root and
   failed to import the sibling module; it ran zero tests.  Running from the
   verifier directory produced `27/27 PASS`.

Neither failure is a mathematical certificate.

## 9. Status boundary before alternate inspection

```text
rectangle identity:                  DERIVED / independently replayed
edge rectangle perfect matching:     DERIVED / independently replayed
local C_(4k) component classes:       DERIVED / complete in local scope
active crossing shape classes:       DERIVED / complete in stated sizes
outside Gram/block equations:         DERIVED / independently replayed
abstract Z topologies through 3 edges: DERIVED / complete
labeled Z placements:                 NOT CATALOGED here
residual A:                           UNKNOWN
residual B:                           UNKNOWN
conditional n3=60:                    UNKNOWN
Conway-99 target:                     UNKNOWN
novelty:                              UNKNOWN
alternate artifacts:                 NOT INSPECTED
```

The baseline is now frozen for comparison.  A later alternate package must
be checked against it without retroactively changing these expectations.
