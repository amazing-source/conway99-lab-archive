# Wave 34 rootless actual-incidence/global attack

```yaml
role: proof_a
date_utc: 2026-07-24T20:16:59Z
git_commit: 0fa5b8161baf8b2a5404a67051b7d61cbc906da3
claim_label: UNKNOWN
scope: "Target I at n3=708: actual triangle incidence plus the rootless integrally indecomposable endpoint and tr(A_-1 A_-2^2)=0"
inputs:
  - "AGENTS.md | sha256 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3"
  - "CONJECTURE.md | sha256 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58"
  - "STATUS.yaml | sha256 feda17934162602804015e17130c029ffdba7bf0307cdf234f4a7d8979298864"
  - "verification/wave34-continuation-protocol.md | sha256 60e6c3aba152e924a51bd2503e82de3d05bb39fada258da4a2796e344ae23cd4"
  - "verification/2026-07-24-wave33-clean-clone.md | sha256 d83e18052114affaed873ddaa7bdc6a26c63afc6432345e1027aeef5bd66d052"
  - "verification/wave33-rootless-motif/comparison-results.json | sha256 8b7b27fd67f12bb82c60eb27c72a62c913d06f2d86f3eb626dcddd6ac75afeb"
  - "verification/wave33-rootless-motif/audit.md | sha256 a761d48419664b3db8605ca2a7dd203c2a1ce6ccd1e96d1ac2c028b1c5209bc9"
method: "Uncontracted three-fibre incidence around every actual graph triangle, followed by the exact 21P0 projector Gram constraint and a finite local extension attack."
command:
  - "python -B attempts/wave34-rootless-global/check_local_model.py --max-witnesses 1"
  - "python -B -m unittest discover -s attempts/wave34-rootless-global -p \"test_*.py\" -v"
outputs:
  - "attempts/wave34-rootless-global/check_local_model.py | sha256 33577962a44241cf3fd9d5a6b5948c35ddd757aed5975bd755c384ded00deed6"
  - "attempts/wave34-rootless-global/test_local_model.py | sha256 21d4dc17c19098ee826202af4688611dbbf5982d0ab9216bb87da6839452a378"
  - "attempts/wave34-rootless-global/local-control.json | sha256 a25d19e3eda3ec77b55065b7f39a68345fa911b80eafbff0e4c37b1857e10301"
  - "attempts/wave34-rootless-global/exact-results.json | sha256 fd4ff04bd13128a26d9a5ecb4bd1c2a8832d29d0056a592d4d90074747a0c331"
limitations: "The exact reduction does not couple the 231 triangle-centred systems strongly enough to force a double overlap. The emitted 45-vertex object is a partial control, not an endpoint, lattice, or graph."
```

## 1. Exact claim and domain

Assume a putative `srg(99,14,1,2)`, its actual 99-by-231
vertex-triangle incidence matrix `N`, the frozen `n3=708` rootless
integrally indecomposable endpoint, and

```text
tr(A_-1 A_-2^2)=0.
```

For disjoint graph triangles, write `R_j` for the relation in which there
are exactly `j` graph edges between the two triangles.  In the frozen
projector Gram, `A_-1=A_R2` and `A_-2=A_R3`.

The intended conclusion was positivity of the mixed trace, another complete
contradiction, or a complete endpoint.  None was obtained.  What was obtained
is an exact actual-incidence/global reformulation which is strictly finer
than the Wave 33 bilinear `Q[Gamma]` tables, plus a projector-derived global
overlap cap and an explicit local control showing where this route still
fails.

No automorphism, transitivity, orbit restriction, or graph symmetry is used.
Before this report and its artifacts were frozen, I inspected only the
protocol and the frozen rootless inputs listed above, not another Wave 34
track.

## 2. Assumptions and imported results

Imported from the frozen package:

1. the exact target and triangle incidence;
2. the endpoint has 708 unordered `R2` pairs;
3. the rootless endpoint forbids the `{-2,-2,-1}` marked-row motif;
4. its count is
   `tr(A_R2 A_R3^2)/2`;
5. the Wave 33 board gives four candidates per `R2` pair but does not control
   their global closure; and
6. the contracted `Q[Gamma]` and `N^T p(A)N` families alone admit the audited
   null trade.

The lemmas below use labelled fibres and three simultaneous matchings, not
only those contracted families.

## 3. Numbered lemmas

### Lemma 1 (DERIVED): actual three-fibre permutation model

Fix an actual graph triangle `T={t0,t1,t2}` and put

```text
Xi = N(ti) \ T.
```

The three sets are disjoint and have size 12.  The local graph on
`N(ti)` is `7 K2`, so its restriction to `Xi` is a perfect matching `gi`.

For `i != j`, every `x in Xi` is nonadjacent to `tj`.  Its two common
neighbours with `tj` are `ti` and one unique vertex of `Xj`.  This defines a
perfect matching/bijection

```text
fij : Xi -> Xj.
```

Transporting labels to `X0`, define

```text
sigma_T = f20 f12 f01.
```

A triangle disjoint from `T` is in relation `R3` with `T` exactly when it is
a cross-fibre transversal, and these transversals are exactly the fixed
points of `sigma_T`.

### Lemma 2 (DERIVED): exact relation degrees and endpoint sum

Set

```text
q(T) = 12 - |Fix(sigma_T)|.
```

There are 36 cross-fibre matching edges.  Each fixed transversal consumes
three.  Every remaining cross-fibre edge lies in a unique triangle having
exactly two cross edges to `T`, and every `R2` neighbour arises uniquely in
this way.  Hence

```text
deg_R3(T) = 12 - q(T),
deg_R2(T) = 3 q(T).
```

There are 212 triangles disjoint from `T`.  Counting cross edges and pairs of
cross edges gives

```text
sum_j j deg_Rj(T)          = 216,
sum_j binom(j,2) deg_Rj(T) = 36.
```

Solving yields the full labelled degree profile

```text
deg_R0(T) =  20 + q(T),
deg_R1(T) = 180 - 3 q(T),
deg_R2(T) =       3 q(T),
deg_R3(T) =  12 - q(T).
```

The frozen 708 unordered `R2` pairs therefore give

```text
3 sum_T q(T) = 2*708,
sum_T q(T)   = 472.
```

Consequently the endpoint has exactly

```text
|E(R3)| = (231*12 - 472)/2 = 1150
```

unordered `R3` pairs.

### Lemma 3 (DERIVED): exact three-leg closure formula

For fixed points `x,y` of `sigma_T`, let `V_x,V_y` be their transversal
triangles.  Between `V_x` and `V_y`, no cross-fibre edge can join different
fibres: the cross-fibre matching partner of a vertex of `V_x` already lies in
`V_x`.  The only possible edges are therefore the three within-fibre edges
from `g0,g1,g2`.

After transporting the three `gi` to `Fix(sigma_T)`, let

```text
m_T(x,y) = number of transported matchings that pair x and y.
```

Then `V_x,V_y` are in relation `R_m`.  In particular,

```text
unordered forbidden motifs
  = sum_T #{ {x,y} subset Fix(sigma_T) : m_T(x,y)=2 },

tr(A_R2 A_R3^2)
  = 2 sum_T #{ {x,y} subset Fix(sigma_T) : m_T(x,y)=2 }.
```

Thus trace zero is equivalent to the following labelled global condition:
for every actual triangle `T`, no edge on `Fix(sigma_T)` belongs to exactly
two of the three transported matchings.  Equivalently, their three pairwise
edge-set intersections all equal their common triple intersection.

This is additional three-leg information.  It retains the individual
vertices and all three local perfect matchings, which the Wave 33 contracted
tables discard.

### Lemma 4 (DERIVED): projector uniqueness and the global triple-overlap cap

Let `P0` be the rank-44 projector on the zero eigenspace of the triangle
graph and set `M=21P0`.  From actual incidence,

```text
M = J + 3 N^T N - N^T A N.
```

Thus `M_TT=4`, while a disjoint pair in `R_j` has entry `1-j`.  Three marked
rows which are pairwise in `R3` have Gram matrix with diagonal 4 and all
off-diagonal entries `-2`; their vector sum has norm zero.  Hence, for any
`R3` edge `{X,Y}`, a common `R3` neighbour must be the unique marked vector
`-(X+Y)`.  An `R3` edge lies in at most one `R3` triangle.

Since there are 1150 `R3` edges, the `R3` triangles are edge-disjoint and

```text
# R3 triangles <= floor(1150/3) = 383.
```

The total number of central triple-overlap events in Lemma 3 is therefore at
most `3*383=1149`.  This is a genuine global/projector consistency bound, but
there is no positive lower bound on the triple overlaps or the forbidden
double overlaps from the present premises.

## 4. Exact finite local control (CANDIDATE only)

To attack the remaining local gap, the checker fixes `q(T)=2` with
`sigma_T=(0 1)`.  It uses factors `0,1,2` of a canonical one-factorization of
`K12` for the three within-fibre matchings.

The resulting 39-vertex core has:

```text
10 fixed transversal R3 neighbours of T,
 6 nonclosed cross-fibre edges, hence 6 R2 neighbours of T,
fixed-transversal pair multiplicities (m=0,1,2,3) = (33,12,0,0).
```

Thus it has neither a forbidden double overlap nor a triple overlap about
`T`.  Six distinct completion vertices close the six defective cross-fibre
edges.  The emitted 45-vertex, 129-edge partial object satisfies:

1. every edge of the 39-vertex core has exactly one current common neighbour;
2. every pair consisting of `ti` and a completion vertex has exactly two
   current common neighbours;
3. every currently decidable adjacent/nonadjacent common-neighbour cap;
4. all ten `R3` neighbours and all six `R2` neighbours of the central
   triangle are present; and
5. none of the six `R2` neighbours has an `R3` cross-matching to a fixed
   transversal.

The complete restricted factor scan checked all `11^3=1331` ordered triples
from that one fixed `K12` factorization.  Of these, 1300 pass the current
common-neighbour caps and 1000 also avoid exactly-double fixed-point
overlaps.  For the emitted factor triple, the six completion-neighbourhood
domains have sizes

```text
2345, 2353, 2346, 2346, 2346, 2353,
```

and deterministic backtracking finds the frozen witness after 31 nodes.

This is not a 99-vertex partial extension certificate.  Edges among the six
completion vertices, their remaining degrees, 54 further vertices, missing
common-neighbour witnesses, all other triangle-centred systems, and the full
231-row projector/Schur identities remain unset.

## 5. Commands, dependencies, versions, seeds, and runtime

Run from the repository root:

```powershell
python -B attempts/wave34-rootless-global/check_local_model.py --max-witnesses 1
python -B -m unittest discover -s attempts/wave34-rootless-global -p "test_*.py" -v
```

Environment:

```text
CPython 3.13.14
third-party dependencies: none
random seed: none; enumeration and backtracking are deterministic
observed checker wall time: 1.541 s
observed 12-test wall time: 1.113 s (unittest body: 0.844 s)
```

All 12 tests pass.

## 6. Complete versus restricted coverage

Complete:

1. Lemmas 1-3 for every actual triangle of any putative target graph;
2. the endpoint sums `sum q(T)=472` and `|E(R3)|=1150`;
3. projector uniqueness of an `R3`-triangle completion and the cap 383;
4. the stated `11^3` restricted factor domain; and
5. the stated completion-neighbourhood domain for the emitted local control.

Restricted or absent:

1. the canonical one-factorization scan is not a classification of arbitrary
   triples of perfect matchings;
2. the positive local control is not asserted extendible;
3. no global coupling of the 231 local permutation/matching systems is
   constructed or excluded;
4. the full projector/Schur package is not satisfied by the partial control;
   and
5. no endpoint lattice or graph is supplied.

## 7. Failed routes retained

1. **Per-centre incidence forcing fails.**  The 45-vertex control has the
   exact `q(T)=2` fixed-point structure, closes all six defective
   cross-fibre edges, and still has no forbidden closure about `T`.
2. **The projector triangle cap is one-sided.**  Edge-disjointness bounds
   triple overlaps above but supplies no lower bound forcing a double
   overlap.
3. **Endpoint averaging is insufficient.**  `sum q(T)=472` and the exact
   local relation degrees do not couple the transported matching overlaps at
   different centres.
4. **Current radius extension remains feasible.**  Exact completion search
   finds the frozen 45-vertex partial control quickly; a local UNSAT route
   does not begin at this radius.
5. **The Wave 33 contraction wall remains binding.**  No contracted moment
   was reinterpreted as global motif positivity.

## 8. Strongest self-objection

The no-double-overlap condition is exact, but it is still a reformulation
until one enforces compatibility among different central triangles and the
full 231-row projector/Schur identities.  The finite control only proves that
one-centre actual incidence, even with all six defective edges closed and
several exact `lambda/mu` equations saturated, does not force the motif.  It
does not establish that the control extends by even one globally consistent
layer, much less to a rootless endpoint or a target graph.

## 9. Machine-readable outputs and hashes

```text
attempts/wave34-rootless-global/check_local_model.py
  33577962a44241cf3fd9d5a6b5948c35ddd757aed5975bd755c384ded00deed6
attempts/wave34-rootless-global/test_local_model.py
  21d4dc17c19098ee826202af4688611dbbf5982d0ab9216bb87da6839452a378
attempts/wave34-rootless-global/local-control.json
  a25d19e3eda3ec77b55065b7f39a68345fa911b80eafbff0e4c37b1857e10301
attempts/wave34-rootless-global/exact-results.json
  fd4ff04bd13128a26d9a5ecb4bd1c2a8832d29d0056a592d4d90074747a0c331
```

## 10. Strongest justified conclusion

`DERIVED`: motif avoidance is exactly a no-double-overlap condition on three
transported perfect matchings over the fixed points of a labelled
12-permutation at every actual triangle.  The endpoint has
`sum q(T)=472`, 1150 `R3` edges, and at most 383 edge-disjoint `R3`
triangles.

`CANDIDATE` finite control: a 45-vertex `q(T)=2` partial incidence object
passes the stated exact checks while avoiding both double and triple overlaps
about its central triangle.

`UNKNOWN`: this run does not prove
`tr(A_-1 A_-2^2)>0`, derive another complete contradiction, construct an
endpoint, exclude `n3=708`, or change Conway-99 status.
