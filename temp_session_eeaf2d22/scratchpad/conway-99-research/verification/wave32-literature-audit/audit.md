# Wave 32 rooted-or-indecomposable endpoint literature audit

## Bottom line

```text
exact rooted endpoint statement:                         FROZEN
exact rootless indecomposable endpoint statement:        FROZEN
actual incidence versus weaker matrix package:           SEPARATED
rootless integrally decomposable actual endpoint:         VERIFIED IMPOSSIBLE upstream
rooted endpoint:                                          UNKNOWN
rootless integrally indecomposable endpoint:              UNKNOWN
exact prior result for either surviving endpoint:         NOT FOUND IN SEARCHED SOURCES
actual 231-triangle spectrum:                             CITED prior art
n3=708, Conway-99 existence/nonexistence, novelty:        UNKNOWN
```

The strongest permitted literature conclusion is:

> No exact prior result for either surviving endpoint branch was found in
> the sources searched as of 2026-07-24.

This is a bounded search result. It is not proof of novelty, priority,
nonexistence, global openness, or completeness of the literature.

## 1. Exact surviving boundary

Wave 31 proves, under actual target vertex-triangle incidence, that a
rootless endpoint lattice cannot have a nontrivial integral orthogonal
decomposition. For an even positive-definite endpoint form `S`, the
exhaustive surviving split is therefore:

```text
(A) S has a norm-two root; or
(B) min(S)>=4 and S is integrally orthogonally indecomposable.
```

Neither branch fixes

```text
h=det(S)
```

to `729`. Both quantify over

```text
h in {9,21,49,81,189,441,729,1029}.
```

No automorphism, orbit structure, transitivity, root-system type, lattice
catalogue representative, or coordinate marking is assumed.

The weaker matrix/projector/Schur target is the existence of

```text
S in Sym_44(Z), even and positive definite,
X in Z^(231 x 44), full column rank,
G=X^T X=21S^(-1),
M=XSX^T,
W=M o M,
Q=X^T W X,
B=SQ=I+2C,
```

with the full inherited alphabet, trace, determinant, and positivity
conditions in `protocol-freeze.md`.

An actual putative graph additionally supplies its `99 x 231`
vertex-triangle incidence matrix `N`, triangle-intersection adjacency
matrix `Gamma`, and

```text
N N^T=7I+A,
N^T N=3I+Gamma,
M=7N^T P_-4 N,
spec(Gamma)=18^1,7^54,0^44,(-3)^132.
```

It also supplies unique edge-triangles and graph-local signed-incidence
identities. None of those extra facts follows from an arbitrary tuple
`S,G,X,M,W,Q,B`. A matrix-only realization would not construct a graph,
and a matrix-only obstruction may not use `N`, `A`, `Gamma`, unique
triangles, or the Wave 31 sign argument without separately deriving them.

## 2. Strongest rooted endpoint

For a root `r` with `r^T S r=2`, the independently verified inherited
conditions include:

```text
r primitive,
div(r)=1,
K_r=r^perp intersect L,
[L:Zr orthogonal_sum K_r]=2,
det(K_r)=2h.
```

Thus a root is not automatically an integral `A1` summand. The index-two
glue is part of the target.

The marked-frame image

```text
t=XSr in Z^231
```

must satisfy

```text
t_i in {0,+1,-1,+2,-2},
sum_i t_i=0,
t.t=42,
Mt=21t,
t(r).t(s)=21(r,s)_S.
```

At the stronger actual-incidence layer it must also satisfy

```text
Gamma t=0,
Nt in ker(A+4I),
||Nt||^2=126.
```

All roots together generate an ADE root lattice `R`; its saturation
`Rbar=(R tensor Q) intersect L` is primitive, its orthogonal complement is
rootless, and `L` is obtained by isotropic glue. This is a reduction, not a
classification. The exact surviving rooted problem is:

> Classify or obstruct every root-preserving primitive ADE closure and
> rootless complement/glue, for all eight determinants, while realizing the
> complete 231-coordinate root-image code and full projector/Schur package;
> for the actual target, also realize the vertex-triangle incidence.

The 32 surviving scalar coordinate-count patterns for one root are only
necessary patterns. They do not produce a vector, a mutual root code, a
lattice, a frame, a Schur certificate, or a graph.

## 3. Strongest rootless indecomposable endpoint

This branch has

```text
min(S)>=4
```

and no nontrivial integral orthogonal direct sum. Wave 31's coordinate-block
and diagonal-sign contradiction begins only after a rootless integral split
forces every norm-four frame row into one lattice summand. That trigger is
absent here.

The exact surviving problem is therefore:

> Classify or obstruct every integrally indecomposable even rank-44 form in
> the eight determinant rows that admits the complete 231-row integral
> scale-21 frame and Schur-defined `Q,B`; for the actual target, also realize
> the vertex-triangle incidence.

This is not the same as additive indecomposability of a quadratic form, an
indecomposable root system, rational indecomposability, or irreducibility of
an automorphism representation. No such stronger or different property is
available.

Algorithms can determine the orthogonal decomposition of a supplied Gram
matrix and can test isometry of supplied lattices. They do not enumerate all
rank-44 endpoint forms and cannot turn failure to locate a candidate into a
nonexistence certificate.

## 4. The modularity shortcut is unavailable

The author-maintained Nebe-Sloane definition requires an `N`-modular lattice
to be similar to its dual through a norm-multiplier-`N` similarity. For a
rank-44 lattice of Gram determinant `h`, such a similarity gives

```text
h = det(N S^(-1)) = N^44/h,
h=N^22.
```

The independent Wave 28 theta/modular verifier already checked this
determinant veto. None of

```text
9,21,49,81,189,441,729,1029
```

equals `3^22`, `7^22`, or `21^22`. Hence no endpoint form is modular at its
exact level, and none is strongly 21-modular.

The actual inherited relation

```text
21L* subset L
```

only controls the exponent/level and 3- and 7-primary discriminant groups.
It does not supply a scaled-dual isometry or any partial-dual
Atkin-Lehner symmetry. Therefore:

- strongly modular shadow or extremal bounds cannot be imported;
- a level-21 lattice table is not an endpoint classification;
- known 21-modular examples in other ranks do not select an endpoint form;
- no modular automorphism may be assumed.

This is an exact hypothesis wall, not merely a literature no-hit.

## 5. Root/reflection and decomposability literature

Nikulin's discriminant-form machinery supports the standard primitive
overlattice and orthogonal-complement bookkeeping already used and
independently checked in Wave 28. It does not classify positive-definite
forms within the relevant genera or solve the marked-frame problem.

Blaschke and Scharlau classify structural data for **reflective** integral
lattices, meaning the root system has maximal rank in their setting. A
rooted endpoint may have a proper-rank root system, so reflectivity is not
available. Their scaled-root-system/code framework is useful vocabulary,
not an endpoint classification.

Hemkemeier-Vallentin provide an orthogonal-decomposition algorithm once a
complete generating system containing all lattice vectors through the
required bound is supplied. Plesken-Souvignier provide lattice-isometry
algorithms. Neither supplies such generators for every endpoint form or a
complete rank-44 determinant census with the frozen frame and Schur
constraints.

Wang's 2025 paper concerns the distinct notion of **additive**
indecomposability and discriminants `2,3,4,5`. The endpoint determinants
start at `9`, and the frozen branch asks only about integral orthogonal
decomposition. No determinant row is removed.

## 6. Primitive idempotents and commutants

The searches found standard association-scheme facts but no exact theorem
matching the needed endpoint implication.

Two notions must not be conflated:

1. a primitive strongly regular graph is one for which the graph and its
   complement are connected; and
2. a primitive idempotent is a minimal idempotent of the commutative
   Bose-Mesner algebra.

Neither statement alone says that the corresponding real projector has no
proper coordinate block, nor that every diagonal sign matrix in its full
matrix commutant is scalar. Wave 31 obtains its contradiction from the much
stronger actual incidence support and local unique-triangle cancellation.
No searched source supplied an abstract commutant theorem that would extend
that result to the rootless indecomposable or matrix-only branch.

## 7. Exact prior-art hit and chronology

The strongest exact prior-art hit is not new to Wave 32:

```text
Petro-Phillips, Discrete Mathematics 349(3), 114862 (2026)
```

conditionally derives the spectrum of the clique graph on the `231`
triangles of a putative target:

```text
18^1, 7^54, 0^44, (-3)^132.
```

Phillips's May 2026 thesis gives the general regular clique-graph formula
and current Conway-99 motivation. Both sources were already recorded in the
public repository before this wave. Accordingly:

```text
actual triangle-intersection spectrum: CITED prior art
Wave 32 discovery/priority claim for that spectrum: none
```

No inspected source continues from that spectrum to any of:

```text
an integral rank-44 eigenspace lattice;
a norm-42 integral root image in ker(Gamma);
the 32-pattern root census or a compatible mutual root code;
primitive ADE closure plus rootless complement/glue in the endpoint rows;
an indecomposable 231-row scale-21 integral frame;
Q=X^T(M o M)X and B=SQ with the endpoint trace/determinant conditions;
an incidence realization, graph construction, or nonexistence proof.
```

Greaves-Iverson-Jasper-Mixon give related finite-field frame prior art for a
hypothetical Conway graph, but their object has `100` vectors in
`F_5^45`, not the real integral `231 x 44` package.

Keramatipour's current SAT report, already present in the repository before
Wave 32, reports that the tested searches were computationally infeasible.
It supplies no checked negative certificate and resolves neither target
outcome. Its omission from the first frozen Wave 32 metadata set was caught
by the independent source verifier and repaired after that audit.

Current clique-complex and clique-homology papers study broad spectral and
topological questions. No inspected target-specific root, lattice, Schur,
or commutant endpoint appeared.

## 8. Current target status

Cesarz-Woldar's 2025 refereed article still describes existence as an
elusive open problem and proves only conditional automorphism restrictions.
Petro-Phillips and Phillips likewise treat it as an existence question.
The Brouwer-Van Maldeghem parameter index/maintained-table context marks
`(99,14,1,2)` unknown. A June 2026 institutional seminar notice announces
nonexistence for the different parameter set `(85,14,3,2)` and only a
possible analogous approach to Conway-99.

These are current-status signals within the searched record. They cannot
prove that no inaccessible, unindexed, unpublished, or very recent result
exists. The repository's global label therefore remains `UNKNOWN`, not a
literature-certified theorem of openness.

## 9. Recommended proof boundary

The sharpest actual-incidence rooted lane is the discrete root-image code:

```text
t in Z^231 intersect ker(Gamma),
t_i in {0,+1,-1,+2,-2},
sum(t)=0,
||t||^2=42,
Nt in ker(A+4I),
||Nt||^2=126,
```

with mutual inner products scaled by `21` and simultaneous compatibility
with primitive ADE glue. A restricted computation must disclose every
assumed root type, determinant, automorphism, orbit, and marking.

The sharpest rootless indecomposable lane must attack the full marked frame
or the actual incidence commutant without manufacturing a coordinate block
from a nonexistent integral split. A candidate form can be tested exactly,
but a negative finite search needs a complete enumeration certificate before
it can imply nonexistence.

The two lanes should remain separate:

```text
matrix/projector/Schur lane: no N, A, Gamma, or local triangle facts;
actual graph lane: may use verified incidence transport and unique triangles.
```

## 10. Search failures and limitations

The exact 68 query strings, dispositions, metadata inspection events, and
access limits are in `query-ledger.json`. The audit did not have exhaustive
authenticated MathSciNet or zbMATH coverage, did not traverse every citation
network or language, and did not retain source payloads.

Searches for the exact numeric fingerprints

```text
"norm 42" + "231",
"231 x 44" integral frame,
rank 44 + determinant 1029,
rank 44 + determinant 729 + roots,
```

returned no relevant endpoint theorem in the inspected windows. Generic
numeric hits, search snippets, and solver/tool claims were not treated as
evidence.

## 11. Status wall

```text
rooted endpoint S-form:                             UNKNOWN
rootless integrally decomposable actual endpoint:   VERIFIED IMPOSSIBLE
rootless integrally indecomposable endpoint S-form: UNKNOWN
weaker matrix/Schur realization:                    UNKNOWN
actual incidence realization:                      UNKNOWN
n3=708:                                            UNKNOWN
Conway-99 existence/nonexistence:                  UNKNOWN
novelty and priority:                              UNKNOWN
```

No determinant row was removed, no endpoint object was constructed, and no
global claim was promoted.
