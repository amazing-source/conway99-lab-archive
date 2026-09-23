---
role: literature
date_utc: 2026-07-26T23:20:23Z
git_commit: 697cc02bcbe16b69aaf08822298e03c66329c64c
claim_label: CITED
scope: >-
  Narrow primary-source-first prior-art audit of the independently verified,
  conditional Wave 36 endpoint reflection, ternary polar-graph rank bound,
  characteristic-seven symmetric-cube bound, and reciprocal Smith pairing.
inputs:
  agents/2026-07-26-wave36-modular-reflection.md: 1a66e4acae92993f547c74745cfe6da7e53dfc185cf37da31d2590edcb6b558c
  agents/2026-07-26-wave36-ternary-polar-bound.md: 062e8b5478b93195dae4d9a571677688cefcd7397cda75246dbd03503f7c9b85
  verification/wave36-modular-reflection/audit.md: 002a44ab3f5a7841e153d9e6317cbd149333b1e034c1fb361bd8ac02d28ad48a
  verification/wave36-ternary-polar-bound/audit.md: 7446391adceff09a06293f4248a751ceef2bf47d546ea58004f096960e47c88c
method: >-
  Inspect current exact-problem sources and primary or author-hosted general
  sources; run bounded exact-phrase and concept searches; compare theorem
  statements and matrix scopes; and clean-room specialize the published
  regular-adjacency polynomial to the independently verified polar-graph
  parameter table.
command: >-
  See attempts/wave36-literature-audit/source-query-metadata.json for the
  bounded query ledger, source URLs, and the exact Evans substitutions.
outputs:
  attempts/wave36-literature-audit/source-query-metadata.json: a659294c30f925a7f6f65202524b4e89f0b8dc6350357c6c50a9f03b337e0fe6
limitations:
  - A finite source search cannot establish novelty, priority, or absence.
  - Search-engine indexing is incomplete, especially for books and notation.
  - No citation found supplies an endpoint matrix, finite-field factor set, or Conway graph.
  - The audit does not alter the conditional mathematical verification status.
---

# Wave 36 literature audit

## Verdict

```text
exact prior statement of C^2=441I for the Wave 36 C:       NOT LOCATED
exact prior Conway-99 rank_F3(M)>=12 statement:            NOT LOCATED
exact prior Conway-99 rank_F7(M)>=11 cube argument:        NOT LOCATED
exact prior reciprocal SNF statement for the Wave 36 C:   NOT LOCATED
known general theorem reproducing the ternary cutoff:      YES
standard ingredients behind the other three arguments:    YES
novelty or priority:                                      UNKNOWN
```

The most important prior-art finding is Rhys J. Evans's published
regular-adjacency polynomial for regular induced subgraphs of strongly
regular graphs.  Once the Wave 36 target-specific bridge has produced a
231-vertex, 162-regular induced subgraph of the appropriate ternary
orthogonality graph, Evans's theorem excludes exactly the same cases as the
verified Wave 36 spectral argument: both determinant classes through
dimension 11, and the nonsquare class in dimension 12; the square class in
dimension 12 survives.

Accordingly, the ambient exclusion theorem and the numerical cutoff should
not be described as a new general polar-graph bound.  What was not located is
the target-specific combination

```text
prism-free Conway endpoint
  -> 231 distinct norm-two ternary projective points
  -> induced degree 162
  -> Evans/polar-graph exclusion
  -> rank_F3(M)>=12 and square class at equality.
```

That no exact combination was found is a bounded-search result, not a novelty
claim.

## 1. Exact-problem literature checked

All links in this section were accessed on 2026-07-26.

| Source | Exact scope found | Relation to Wave 36 |
|---|---|---|
| A. E. Brouwer and H. Van Maldeghem, *Strongly Regular Graphs* (2022), [author-hosted PDF](https://homepages.cwi.nl/~aeb/math/srg/rk3/srgw.pdf) | Records Conway's prize problem and marks `(99,14,1,2)` unresolved; also gives standard `q=3` orthogonal graphs and spectra in Section 3.1.3. | No endpoint `C`, modular-rank floor, symmetric-cube argument, or reciprocal SNF statement was located. |
| P. G. Cesarz and A. J. Woldar, “On the automorphism group of a putative Conway 99-graph,” *Algebraic Combinatorics* 8 (2025), [DOI 10.5802/alco.418](https://alco.centre-mersenne.org/articles/10.5802/alco.418/) | Automorphism-group restrictions. | Different lane; no overlap with the four audited algebraic claims was located. |
| R. Reimbayev, “The Subgraphs of Order Six of the Family of Strongly Regular Graphs with Parameters `lambda=1` and `mu=2`,” [arXiv:2508.03377](https://arxiv.org/abs/2508.03377) | Introduces `n3` as the free six-vertex count and expresses the remaining six-vertex counts through it. | This is direct ancestry for the endpoint variable, but the PDF contains no matches for `rank`, `Smith`, or `4158`; it does not state the Wave 36 endpoint algebra. |
| R. Reimbayev, “The Lower Bound for Number of Hexagons…,” [arXiv:2409.10620](https://arxiv.org/abs/2409.10620) | Hexagon lower bounds in the `lambda=1, mu=2` family. | No `rank` or `Smith` match was found. |
| A. Keramatipour, “Approaching the Conway-99 problem using SAT solvers,” [arXiv:2604.23037](https://arxiv.org/abs/2604.23037) | SAT encodings and experimental limitations. | No matrix-rank or Smith-form argument matching Wave 36 was located. |
| S. Lou and M. Murin, “On the Strongly Regular Graph of Parameters `(99,14,1,2)`,” [MIT PRIMES PDF](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf) | Structural and automorphism restrictions; the 231-triangle auxiliary graph appears explicitly. | No modular rank argument was located.  The shared number 231 is structural, not evidence of the Wave 36 result. |
| R. Ibrahim, H. LaFayette, and K. McCall, “Minimum 2-percolating sets in 2-connected, diameter 2 graphs,” *Australasian Journal of Combinatorics* 93 (2025), [journal PDF](https://ajc.maths.uq.edu.au/pdf/93/ajc_v93_p060.pdf) | Theorem 4.19 bounds induced `K3 square K3` copies in a hypothetical Conway graph by 231. | A different use of 231; no reflection or finite-field-rank conclusion. |

Bounded exact searches for `"2M-21I"`, `"C^2=441I"`, the Conway graph
together with `rank_F3` or rank over `F_3`, the Conway graph together with
`symmetric cube` or `Hadamard cube`, and the Conway graph together with
`Smith normal form` produced no relevant exact target hit.  The exact query
strings are frozen in the metadata JSON.

## 2. Ternary orthogonality graph and induced-subgraph bound

### The ambient graphs and spectra are standard

Brouwer and Van Maldeghem describe the graph on one quadratic type of
nonisotropic points over `F_3`, adjacent when orthogonal, and give its
strongly regular parameters and spectrum.  Sam Adriaensen and Maarten De
Boeck, “Association schemes and orthogonality graphs on anisotropic points
of polar spaces,” *Designs, Codes and Cryptography* 93 (2025),
[arXiv:2402.05055](https://arxiv.org/abs/2402.05055),
[DOI 10.1007/s10623-024-01514-7](https://doi.org/10.1007/s10623-024-01514-7),
systematically compute the relevant association schemes and orthogonality
spectra.  They explicitly note that for `q=3`, restricting to one quadratic
type gives the known two-class association scheme.

Thus the ambient strongly regular graphs, their two determinant classes,
and their spectra are prior theory.

### The Wave 36 mixing step has a published stronger analogue

Evans, “Bounds for regular induced subgraphs of strongly regular graphs,”
*Discrete Mathematics* 346 (2023) 113154,
[arXiv:2202.03700](https://arxiv.org/abs/2202.03700),
[DOI 10.1016/j.disc.2022.113154](https://doi.org/10.1016/j.disc.2022.113154),
proves that if an `SRG(v,k,lambda,mu)` contains a `d`-regular induced
subgraph of order `y>=2`, then

```text
R(x,y,d)
 = x(x+1)(v-y) - 2xyk
   + (2x+lambda-mu+1)yd
   + y(y-1)mu - yd^2
```

is nonnegative for every integer `x`.

Substituting `y=231`, `d=162`, and the independently verified Wave 36
ambient parameters gives:

| dimension | determinant class | integer witness `x` | `R(x,231,162)` | consequence |
|---:|:---:|---:|---:|:---|
| 7 | square | -71 | -4,857,762 | excluded |
| 7 | nonsquare | -70 | -4,218,732 | excluded |
| 8 | square | 51 | -1,814,976 | excluded |
| 8 | nonsquare | 56 | -2,318,148 | excluded |
| 9 | square | 72 | -1,560,978 | excluded |
| 9 | nonsquare | 68 | -1,717,920 | excluded |
| 10 | square | 75 | -2,244,960 | excluded |
| 10 | nonsquare | 74 | -175,428 | excluded |
| 11 | square | 75 | -209,592 | excluded |
| 11 | nonsquare | 76 | -154,308 | excluded |
| 12 | square | 76 | 6,020,322 | not excluded |
| 12 | nonsquare | 76 | -303,996 | excluded |

This exactly matches the verified Wave 36 boundary.  The earlier
eigenvalue-density method itself is also standard; see N. Alon and F. R. K.
Chung, “Explicit construction of linear sized tolerant networks,”
*Discrete Mathematics* 72 (1988) 15–19,
[author-hosted PDF](https://web.math.princeton.edu/~nalon/PDFS/Publications/Explicit%20construction%20of%20linear%20sized%20tolerant%20networks.pdf),
[DOI 10.1016/0012-365X(88)90189-6](https://doi.org/10.1016/0012-365X(88)90189-6).

The defensible attribution is therefore:

```text
standard/prior:
  finite orthogonal SRG parameters and spectra;
  spectral induced-density bounds;
  Evans's sharper regular-induced-subgraph polynomial.

not found verbatim:
  the Conway endpoint-to-polar-subgraph bridge;
  the resulting conditional rank_F3(M)>=12 statement;
  the square determinant requirement at rank 12.
```

## 3. Characteristic-seven symmetric cubes

T. Damm and N. Dietrich, “Hadamard powers and kernel perceptrons,”
*Linear Algebra and its Applications* 672 (2023) 93–107,
[arXiv:2207.08853](https://arxiv.org/abs/2207.08853),
[DOI 10.1016/j.laa.2023.04.020](https://doi.org/10.1016/j.laa.2023.04.020),
develop the standard relation between Hadamard powers of Gram matrices and
degree-`d` monomial feature spaces.  Their generic real rank formula has the
same binomial feature-space dimension

```text
binom(r+d-1,d).
```

That paper is not a source for the exact finite-field conclusion: its main
rank results are real and generic.  It does establish that the
Hadamard-power/symmetric-feature-space mechanism is standard background.
Over `F_7`, the particular dimension bound
`dim Sym^3(F_7^r)=binom(r+2,3)` is elementary and field-independent because
the tensor degree 3 is below the characteristic 7.

No source was located for the target-specific chain

```text
entry alphabet {0,+2,-2} and diagonal 1
  -> C^(o3)=4(I+C) mod 7
  -> invertibility from C^2=0
  -> 231 independent pure cubes
  -> rank_F7(M)>=11.
```

The symmetric-tensor rank ceiling is standard; the diagonal-isolating cubic
identity and its conditional Conway endpoint application were not found in
the searched sources.  Novelty remains unassessed.

## 4. Reciprocal Smith pairing

R. P. Stanley, “Smith normal form in combinatorics” (2016),
[author-hosted survey](https://math.mit.edu/~rstan/papers/snf_survey.pdf),
reviews the classical existence and uniqueness of Smith form over the
integers, invariant factors, and their description by minors.  Starting from
`C=441C^{-1}`, reversing the diagonal list
`441/d_1,...,441/d_231` into divisibility order and invoking uniqueness is
therefore an elementary application of standard Smith theory.

There is relevant Conway-specific Smith literature which must not be
conflated with Wave 36.  J. E. Ducey et al., “Critical group structure from
the parameters of a strongly regular graph,”
[arXiv:1910.07686](https://arxiv.org/abs/1910.07686), compute the complete
critical group of a hypothetical Conway graph via the Smith form of its
99-by-99 graph Laplacian

```text
L=14I-A.
```

Wave 36 instead studies the nonsingular 231-by-231 endpoint matrix
`C=2M-21I` arising from the triangle system.  Ducey et al.'s result is genuine
exact-problem prior art for Smith methods, but it is a different matrix and
does not imply

```text
d_i d_(232-i)=441
```

for the Wave 36 `C`.  No exact source for that pairing or for the consequent
two-prime invariant-factor profiles was located.

## 5. Endpoint reflection

Turning a two-eigenvalue or projector identity into a scaled involution is
standard linear algebra.  The searched exact-problem sources did not,
however, contain the specific endpoint normalization

```text
C=2M-21I,  C^2=441I_231,
```

with diagonal `-13`, off-diagonal alphabet `{0,+2,-2}`, and row counts
`(32,36,162)`.  This target-specific identity depends on the verified Wave 35
endpoint bridge.  It is appropriately described as “not located in this
bounded prior-art pass,” not as new.

## Publication wording

A conservative public summary is:

> Conditional on the independently verified prism-free endpoint package, the
> repository derives a 231-point ternary orthogonality configuration and
> obtains `rank_F3(M)>=12`, with only the square determinant class surviving
> at equality.  The ambient orthogonality spectra and regular-induced-subgraph
> bounds are established prior theory; in fact Evans's general polynomial
> reproduces the same cutoff after the repository's target-specific
> substitution.  The audit did not locate the exact Conway endpoint
> application, the characteristic-seven diagonal-isolating cube argument, or
> the reciprocal Smith pairing for the 231-by-231 matrix.  This no-hit does
> not establish novelty or priority.

The mathematical status remains:

```text
conditional Wave 36 results: VERIFIED in their stated scopes
endpoint n3=4158:             survives
global bound:                 n3<=4158
Conway-99:                    UNKNOWN
novelty:                      UNKNOWN
```
