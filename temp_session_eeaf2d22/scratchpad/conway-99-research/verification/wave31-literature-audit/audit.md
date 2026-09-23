# Wave 31 statement and literature audit: surviving `20+24` endpoint

## Verdict

```text
exact frozen statement:                         FROZEN
Wave 30 conditional 20+24 reduction:            VERIFIED upstream
exact matrix/Schur realization:                 UNKNOWN
exact prior result matching the realization:    NOT FOUND IN SEARCHED SOURCES
actual-graph q!=1 theorem:                       VERIFIED upstream / CITED prior art
forced actual-graph U profile 3^4,2^122:         DERIVED from frozen identities + q-gap
sign-involution constancy lemma:                 UNKNOWN
sign-involution block obstruction:               UNKNOWN
graph lift:                                      UNKNOWN
novelty or priority:                             UNKNOWN
Conway-99:                                       UNKNOWN
literature claim label:                         UNKNOWN
```

The strongest justified literature conclusion is:

> No exact prior result was found in the sources searched as of 2026-07-24.

This is a bounded non-discovery. It is not evidence of novelty,
nonexistence, or global openness.

## 1. Statement freeze

The exact matrix-level question is whether there exist positive-definite even
integral forms

```text
S=A orthogonal_sum U,
rank(A)=20, det(A)=729, min(A)>=4,
rank(U)=24, det(U)=1,   min(U)>=4,
```

and an integral `231 x 44` full-column-rank matrix `X` such that

```text
G=X^T X=21S^(-1),
M=XSX^T,
M^2=21M,
M1=0,
diag(M)=4,
M_ij in {0,1,-1,-2}.
```

Here `A` is a local label, not the ADE lattice `A_20`. The quantifier ranges
over every integral marking of every admissible `A` and `U`; it is not
restricted to the Wave 30 bare candidate `T20 orthogonal_sum LAMBDA24`.

Rootlessness forces the exact row and matrix split

```text
X_A: 105 x 20,       X_U: 126 x 24,
X_A^T X_A=21A^(-1),  X_U^T X_U=21U^(-1),
M=M_A orthogonal_sum M_U,
rank(M_A),rank(M_U)=20,24.
```

The Schur square is active rather than replaceable by free data:

```text
W=M o M,
Q=X^T W X,
B=SQ=I+2C.
```

All four objects split by blocks. The surviving endpoint requires

```text
det(Q_A),det(Q_U)=5,1,
det(B_A),det(B_U)=3645,1,
tr(B_A),tr(B_U)=36,24,
B_U=I_24,
Q_U=U^(-1),
tr(C_A)=8,
tr(C_A^2)>=10.
```

The non-lattice hostile control
`spec(C_A)={2^1,1^6,0^13}` is deliberately **not** an assumption.

The equivalent tensor factorization is also part of the target. With
`u_i=S^(1/2)x_i`,

```text
Phi(v)=sum_i <v,u_i> u_i tensor u_i,
Phi_A^*Phi_A=A^(1/2)Q_AA^(1/2),
Phi_U^*Phi_U=I_24.
```

The integral cubic tensor
`P_abc=sum_i X_ia X_ib X_ic` has no mixed `A/U` entries, is harmonic, and
reconstructs `Q` through the exact contracted Schur identity recorded in
`protocol-freeze.md`.

The row arithmetic is

```text
a=32-c, b=36-3c, z=162+3c, 1<=c<=12,
at most one row has c=1,
sum_A c=1044,
sum_U c=1256.
```

The directed block alphabets are therefore

| block | `+1` | `-1` | `-2` | `0` |
|---|---:|---:|---:|---:|
| `A` | 2316 | 648 | 1044 | 6912 |
| `U` | 2776 | 768 | 1256 | 10950 |

Thus the `-1` unordered pairs split as `324+384=708`. On the `U` block, the
tensor isometry allows exactly

```text
c in {9,10,11},
n9=n11+4,
n10=122-2n11,
0<=n11<=61.
```

These 62 aggregate profiles are necessary conditions only.

## 2. The graph-only `q` theorem is not a projector theorem

For an actual putative `srg(99,14,1,2)`, Wave 7 independently verified

```text
q=0 or q>=2.
```

The proof uses graph-local perfect matchings and a simple, triangle-free,
2-regular auxiliary graph `H_T`; `q=1` would force `H_T` to be a triangle.
Lou and Murin's 2014 MIT PRIMES-USA report gives the equivalent prior-art
statement `gamma!=11`, with `q=12-gamma`.

That graph structure is not encoded by the narrower displayed
`X/M/W/Q/B` package. The scope wall is therefore:

```text
projector/Schur realization: c=11 (q=1) remains permitted;
actual-graph endpoint:       c=11 (q=1) is forbidden.
```

Only at the actual-graph layer do the 62 `U` profiles collapse to

```text
4 rows with c=9  (q=3),
122 rows with c=10 (q=2).
```

The corresponding `A` block has

```text
sum_A q=216,
q in {0,2,3,...,11},
at most one q=11.
```

Even a matrix realization satisfying this sharpening would still need a
separate triangle-incidence and 99-vertex adjacency lift.

## 3. Search coverage

The query ledger retains 80 exact web-search strings in 20 batches. The
lanes covered:

- the full `231,44,21,105,126` projector/frame fingerprint;
- the Leech-side 126-row norm-four scale-21 frame and cubic isometry;
- the rank-20 105-row determinant-729 frame coupled to determinant-five
  `Q_A`, trace 36, and determinant 3645;
- Schur/Hadamard-square Gram identities, harmonic cubic tensors, cubature,
  lattice designs, eutactic stars, and s-integrability;
- exact row and pair numbers, including `324+384`, `708`, and the forced
  `4+122` graph profile; and
- Conway-99 Euclidean representations and current status sources;
- diagonal sign matrices commuting with primitive idempotents or orthogonal
  projectors, projector support reducibility, and decomposable frames; and
- triangle-constant signings, signed net-regularity, invariant eigenspaces,
  strongly regular signed graphs, and the exact divisibility-33 signature.

Four direct authoritative metadata or abstract opens were attempted. The
arXiv record for `2606.13771` opened successfully. Three DOI-resolver opens
were rejected by the interactive opener and are recorded as access failures,
not no-hits. Niemeier's publisher metadata and the MIT institutional paper
index were subsequently located through search.

No raw PDF, HTML page, API response, or search payload is retained.

## 4. Closest lattice and frame prior art

### Rank-24 classification

Niemeier's 1973 primary paper classifies the 24 positive-definite even
unimodular rank-24 isometry classes. With the frozen minimum-four/rootless
hypothesis, `U` is therefore isometric to the Leech lattice.

This simplifies the abstract isometry class but does not fix an integral
marking and does not provide a selected 126-row frame. In particular it does
not establish

```text
X_U^T X_U=21U^(-1),
M_U o M_U,
Q_U=X_U^T(M_U o M_U)X_U=U^(-1),
Phi_U^*Phi_U=I_24.
```

### Eutactic stars and tight frames

Conway and Sloane's 1989 paper is the strongest terminology match. It
defines `s`-integrability and its equivalence with a scale-`s` eutactic star
in the dual, and discusses the Leech lattice. Searches under this language
found no exact scale-21, 126-vector, norm-four, third-moment-isometric
configuration.

Delsarte-Goethals-Seidel and Benedetto-Fickus supply foundational design and
tight-frame theory. Neither contains the integral endpoint alphabet, block
split, determinant-five Schur coupling, or cubic isometry.

Bertucci and Bonifacio's current preprint
*Bootstrapping Euclidean Lattices* (arXiv:2606.13771v1, submitted
2026-06-11) is a noteworthy conceptual near hit. It uses spectral identities
and triple products and proves a bound saturated in dimension 24 by the
Leech lattice. The inspected abstract and metadata do not state a selected
126-vector subset or any of the exact scale-21, `Phi`, `Q`, `B`, or block
identities here.

### Conway/frame near hit

Greaves, Iverson, Jasper, and Mixon connect a hypothetical Conway graph to a
finite-field equiangular tight frame. Their object has 100 vectors in
`F_5^45`. It is categorically and numerically different from the real
integral `231 x 44` projector and the `105+126` lattice split.

No inspected primary or authoritative source matched the exact frozen
signature or an equivalent substantial identifying combination.

## 5. Graph prior art and current status

Lou-Murin is an exact prior-art overlap for the graph-local fixed-triangle
profile and the `q!=1` gap. This must be credited and is not project novelty.
The source does not state the projector/Schur realization or the derived
forced `U` profile.

Reimbayev's 2024 article supplies nearby structural counting work for the
`lambda=1,mu=2` family. Cesarz-Woldar's refereed 2025 article describes
Conway-99 existence as an elusive open problem while deriving conditional
automorphism restrictions. Keramatipour's current 2026 SAT preprint reports
an unresolved computational attempt. None supplies a graph construction,
nonexistence certificate, or the frozen endpoint realization.

The current-source conclusion is only:

```text
no Conway-99 resolution was found in this bounded search.
```

Global status remains `UNKNOWN`.

## 6. Post-freeze sign-involution candidate

The orchestrator supplied a new possible obstruction after the original
statement and literature protocol had been frozen. It is recorded separately
in `protocol-addendum-sign-involution.md`; the original freeze was not
retroactively changed.

For a putative graph, let `N` be its `99 x 231` vertex/triangle incidence
matrix, `P_-4` the graph `-4` spectral projector, and `E=M/21`. The exact
incidence factorization is

```text
E=(1/3)N^T P_-4 N.
```

A coordinate block `I` of `E` with size `m` and rank `r` yields the diagonal
involution

```text
D_TT=+1 on I and -1 off I,
DE=ED,
m=21r/4.
```

The symmetric integer matrix `K=NDN^T` then preserves the graph `-4`
eigenspace, hence commutes with `P_-4`. If
`delta=diag(D)` and

```text
s_v=(N delta)_v=sum_(T containing v) delta_T,
```

then `K_vv=s_v`; an edge entry is the sign of its unique graph-triangle; and
the signed off-diagonal adjacency has net-degree `2s_v`.

The missing claim is:

```text
[K,P_-4]=0 plus this triangle-constant support
    => s_v is constant over the 99 vertices.
```

This implication is a **candidate lemma**, not a verified theorem. If it
holds, double counting gives

```text
99s=3(2m-231),
m=33(7+s)/2,
33|m.
```

Together with `m=21r/4`, this forces `44|r`; a nonempty coordinate block has
`r=44,m=231`, so no proper block exists. Thus the lemma would exclude the
rootless `20+24` endpoint, but only after independent proof and verification.

Twenty-four additional exact queries searched diagonal sign commutants,
primitive-idempotent reducibility, signed triangle incidence, signed
net-regularity, invariant eigenspaces, and the exact Conway numbers.
Stanić's strongly regular signed-graph theory,
Kharaghani-Pender-Suda's association-scheme signings, and the
Brouwer-Van Maldeghem monograph are relevant general sources. None of the
inspected records states the candidate constancy lemma, its `33|m`
consequence, or the exact endpoint obstruction.

The sign-involution route, its novelty, and its decisive lemma remain
`UNKNOWN`.

## 7. Exact-match conclusion

The search found no paper or authoritative catalogue record containing all,
or a plausibly equivalent substantial combination, of

```text
231 integral rows in rank 44 with scale 21;
off-diagonal alphabet {0,1,-1,-2};
rank split 20+24 and row split 105+126;
det(A),det(U)=729,1;
Schur-defined det(Q_A),det(Q_U)=5,1;
tr(B_A),tr(B_U)=36,24 and B_U=I_24;
Leech-side cubic isometry Phi_U^*Phi_U=I_24;
pair split 324+384;
actual-graph U profile q=3^4,2^122.
```

The post-freeze search also found no source matching

```text
D diagonal with signs on 231 graph-triangles;
D commuting with E=M/21;
K=NDN^T commuting with P_-4;
triangle-constant signed adjacency forcing N delta constant;
33 dividing the coordinate-block size.
```

The exact-match field is therefore

```text
NO_EXACT_PRIOR_RESULT_FOUND_IN_SEARCHED_SOURCES
```

and nothing stronger.

## 8. Provenance and limitations

The statement freeze is SHA-256
`97660bf039223f55d51f498f5743e2ca1779743bbc058f9c5b7e511957e06621`.
It incorporates the upstream independently verified q-gap and the repaired
Wave 30 scoped conditional theorem. Those mathematical verdicts are
provenance, not literature evidence.

This audit did not comprehensively search Google Scholar, MathSciNet,
zbMATH, every language, all books, all citation networks, paywalled
full-text, newly posted work, or unpublished manuscripts. Search ranking and
terminology can hide relevant material. It performed no exhaustive matrix,
lattice, or graph enumeration. A no-hit from any lane cannot establish
novelty or nonexistence.

Final wall:

```text
conditional decomposable-rootless 20+24 reduction: VERIFIED upstream
surviving matrix/Schur realization:                UNKNOWN
actual-graph incidence/adjacency lift:              UNKNOWN
sign-involution constancy lemma and obstruction:    UNKNOWN
n3=708:                                             UNKNOWN
Conway-99:                                          UNKNOWN
novelty and priority:                               UNKNOWN
```
