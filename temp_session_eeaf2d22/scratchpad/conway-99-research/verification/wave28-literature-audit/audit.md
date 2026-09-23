# Wave 28 proof-separated literature and status audit

Audit date: `2026-07-24` UTC
Frozen public base: `d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b`
Role: `literature`
Overall claim label: `UNKNOWN`

## Verdict

The current source record does **not** change the project status:

```text
srg(99,14,1,2) existence: UNKNOWN
n3=708 endpoint: UNKNOWN
Wave 28 novelty: UNKNOWN
```

The strongest current source located is Cesarz and Woldar's 2025
refereed article, whose abstract explicitly says that existence of a
strongly regular graph with parameters `(99,14,1,2)` remains an open
problem.  A 2026 SAT preprint continues to pose the existence problem
and reports unsuccessful bounded experiments, not a complete search.
No direct resolution was found in the sources searched as of
`2026-07-24`.

The audit located authoritative sources for many **standard
ingredients**: discriminant forms and isotropic gluing, Milgram's
signature phase, catalogue facts for `K12` and `Lambda(F)`, the
definition of modular lattices, ordinary Kneser neighbors, and nearby
tight-frame/spherical-design theory.  It did not locate a source stating
any of the exact Wave 28 combinations as one prior result.  Non-hits do
not establish novelty.

## Frozen search and evidence accounting

The query plan was frozen before live searching at
`2026-07-24T02:33:38Z`.  Its 35 candidate-independent query strings are
preserved in [`query-ledger.json`](query-ledger.json).  The one-to-one
execution record is in [`query-results.json`](query-results.json).

```text
frozen queries:                                35
executed query outcomes:                       35
direct current-status outcomes:                 5
standard/catalogue ingredient outcomes:         8
nearby-only or no-direct-match outcomes:        22
retained bibliographic/source records:          17
recorded access/service limitations:             2
exact target-resolution sources found:           0
exact combined Wave 28 prior-art results found:  0
```

Only URLs, bibliographic metadata, page/theorem notes, access dates, and
read-only response hashes are retained.  No raw HTML or paper copies are
part of this audit package.  See
[`sources/bibliography.json`](sources/bibliography.json).

## Lane-by-lane findings

| Lane | What was located | Exact combined result? | Status consequence |
|---|---|---:|---|
| Conway 99 status | A 2025 refereed paper explicitly saying existence remains open; 2024 and 2026 primary preprints with partial structural/SAT work | No construction or nonexistence located | `UNKNOWN` retained |
| Rank-44 scaled dual | Definition/table for modular lattices and general lattice classification material | No classification for even rank 44 with `21L* subset L` and the eight determinant rows | no determinant row removed |
| Discriminant/root glue | Nikulin's standard discriminant-form and overlattice machinery; modern Milgram and finite-module sources | No source for the full rank-44, 3/7-primary, scaled-dual, rootless-complement package | standard ingredients `CITED`; exact application stays repository-derived |
| Theta controls | Author-maintained catalogue entries and primary provenance for `K12` and `Lambda(F)` | No source for `K12 orthogonal_sum Lambda(F)` versus `E6^6 orthogonal_sum E8` with the asserted discriminant/theta comparison | catalogue facts only are `CITED` |
| Simultaneous neighbor | Standard one-lattice Kneser neighbor definitions, construction, and connectivity results | No source for one basis change preserving the frozen paired-form/scaled-dual tuple | exact simultaneous package not promoted to `CITED` |
| Marked frame/Schur/cubic | Nearby projector/Hadamard/tight-frame and complete-shell spherical-design results | No source for the exact 231-vector rank-44 marked package | exact package remains repository arithmetic |
| Root-image patterns | No direct match to the exact numerical or structural searches | No source for the `46 -> 32` reduction | no novelty inference |

## 1. Current status of Conway's 99-graph

Patrick G. Cesarz and Andrew J. Woldar,
[*On the automorphism group of a putative Conway 99-graph*](https://alco.centre-mersenne.org/articles/10.5802/alco.418/),
Algebraic Combinatorics 8(2) (2025), 379-398, DOI
`10.5802/alco.418`, is the strongest refereed chronology point located.
Its abstract identifies the exact parameters and explicitly says
existence remains an open problem.  Its theorems constrain the
automorphism group of a putative graph; conditional structure is not a
construction or global nonexistence proof.

Ali Keramatipour,
[*Approaching the Conway-99 problem using SAT solvers*](https://arxiv.org/abs/2604.23037),
arXiv:2604.23037v2 (2026), reports that the tested SAT approach does not
solve the instances in reasonable time.  The paper is evidence of
continued work after the 2025 status statement, not a complete-search
certificate.  Reimbay Reimbayev's 2024
[*Lower Bound for Number of Hexagons...*](https://arxiv.org/abs/2409.10620)
likewise derives structural bounds while treating existence as a
question.

An official Brouwer strongly regular graph table URL was attempted, but
the web safe-open service failed for that page during this run.  It is
recorded as a service failure and not used as evidence.  The conclusion
above therefore rests on sources successfully inspected.

## 2. Rank-44 scaled-dual hypothesis wall

The Nebe-Sloane
[*Modular Lattices*](https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/modular.html)
page defines an `N`-modular integral lattice as one **similar to its
dual** and gives matrix conditions for the similarity to carry the dual
to the lattice.  This is stronger than

```text
21L* subset L.
```

Consequently, an upper bound or classification for modular or strongly
modular lattices cannot be applied to the frozen endpoint lattice
without first proving the missing similarity and genus hypotheses.  The
rank-44 row in the modular table is not a classification of all even
positive-definite lattices satisfying the weaker containment.

The searches did not locate a publication classifying exactly the
rank-44 weak scaled-dual package with determinant in

```text
{9,21,49,81,189,441,729,1029}.
```

This leaves every determinant row open.

## 3. Discriminant forms and root glue

V. V. Nikulin,
[*Integral symmetric bilinear forms and some of their applications*](https://www.mathnet.ru/eng/im1677),
Math. USSR-Izvestiya 14(1) (1980), 103-167, DOI
`10.1070/IM1980v014n01ABEH001060`, supports the standard
discriminant-form framework.  Exact modern restatements confirm the
relevant numbered attributions:

- Propositions 1.4.1-1.4.2: even overlattices correspond to isotropic
  subgroups, with the residual discriminant form on the appropriate
  quotient.
- Proposition 1.6.1: primitive orthogonal complements in an even
  unimodular lattice have opposite discriminant forms.
- Corollary 1.9.4: signature and discriminant form determine the
  **genus**, not necessarily one positive-definite isometry class.

Laurence Taylor's
[*Gauss Sums in Algebra and Topology*](https://arxiv.org/abs/2208.06319)
supplies a modern proof route for the Milgram signature formula.
Xiao-Jie Zhu's
[*Finite quadratic modules and lattices*](https://arxiv.org/abs/2110.06783)
supports standard finite-module decomposition and explicit realization
machinery.  Neither states the exact twelve-form Wave 28 census or
realizes those formal modules inside the frozen endpoint package.

The independent Wave 28 verifier found one mandatory prose correction:

```text
Correct:
  the 3-primary and 7-primary components are elementary;
  no p-primary cyclic factor has order p^2 or higher;
  invariant factors divide 21 and may have order 21.

Incorrect:
  "there can be no cyclic factor of order 21."
```

Indeed, `Z/21` is isomorphic to `Z/3 direct_sum Z/7`.  The error does
not affect the primary decomposition, level table, Milgram census, or
local calculations, but publication prose must use the corrected
statement.

No source was found that combines the standard ingredients with all the
frozen rank-44, scaled-dual, determinant, primitive-root, rootless
complement, and 231-coordinate hypotheses.  The repository may label
standard imports `CITED`, while its exact application remains subject to
the independent arithmetic verifier.

## 4. `K12` and `Lambda(F)` attribution wall

The Nebe-Sloane
[*K12 catalogue entry*](https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/K12.html)
explicitly states dimension 12, determinant 729, minimum 4, kissing
number 756, `INTEGRAL=1`, `MODULAR=3`, and supplies Gram and similarity
matrices.  It cites Conway and Sloane's 1983 primary paper.

The
[*LAMBDA(F) catalogue entry*](https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/KV32F.html)
explicitly states dimension 32, determinant 1, minimum 4, kissing number
146880, `Unimodular=1`, and supplies a Gram matrix.  It cites the
Koch-Venkov rank-32 work.  The catalogue property field does not
separately state evenness; that is either a paper-level attribution or
an exact check of the matrix.

The catalogue sources do not assert:

- the orthogonal sum `K12 orthogonal_sum Lambda(F)`;
- a minimum for a 21-scaled dual of that sum;
- an isometry of its discriminant form with that of
  `E6^6 orthogonal_sum E8`;
- matching Weil representations;
- the claimed theta/root coefficient comparison; or
- any projector, Schur, marked-frame, graph, or endpoint consequence.

Exact searches for the two orthogonal sums and the discriminant-form
comparison found no direct match.  Their arithmetic therefore belongs
to the exact and independent verifier artifacts, not catalogue
attribution.  Novelty remains `UNKNOWN`.

## 5. Ordinary versus simultaneous neighbors

John Voight's
[*Kneser's method of neighbors*](https://jvoight.github.io/articles/kneser-033024.pdf)
(2024), Gabriele Nebe's
[*Quadratic Forms*](https://www.math.rwth-aachen.de/~Gabriele.Nebe/SummerSchool2023/QFVorl.pdf),
and Jacques Martinet's
[*On Parity Classes*](https://jamartin.perso.math.cnrs.fr/Othertexts/paritylat.pdf)
support ordinary one-lattice neighbor definitions, explicit
constructions, and connectivity results under stated hypotheses.

Searches for `simultaneous`, `paired quadratic forms`,
`contragredient`, and `scaled-dual endomorphism` did not locate a source
stating the exact Wave 28 transformation of the full tuple.  Some
results concern a neighbor operator on a space of lattice classes;
“dual” in that setting is not automatically the lattice dual in the
frozen matrix package.

Applying the same rational basis change to several matrices gives
elementary congruence identities.  However, the exact integrality,
evenness, positive-definiteness, scaled-dual, and auxiliary-matrix
claims still require the repository's independent verifier.  They are
not established merely by citing Kneser theory.

## 6. Marked frames and the exact root-image count

Appleby, Bengtsson, Flammia, and Goyeneche's
[*Tight Frames, Hadamard Matrices and Zauner's Conjecture*](https://arxiv.org/abs/1903.06721)
gives nearby projector/Hadamard/tight-frame relations in a
SIC-specific setting.  Claude Pache's
[*Shells of selfdual lattices viewed as spherical designs*](https://arxiv.org/abs/math/0502313)
uses theta series for **complete** lattice shells.

Neither treats the exact real integral system of 231 selected norm-four
vectors in rank 44 with the frozen Gram alphabet, tight-frame projector,
Schur-square equation, and oriented cubic tensor.  A complete
antipodal shell has automatic cancellation of odd moments; a selected
orientation of 231 antipodal pairs does not inherit that cancellation
without proof.

Exact searches for the 231-coordinate root image, squared norm 42,
and 46-to-32 pattern reduction found no direct source.  The finite
reduction may be reported as a repository computation after independent
verification, but the literature search neither promotes it to `CITED`
nor proves it novel.

## Publication-safe conclusion

The strongest defensible public wording is:

> As of the recorded primary-source search through 2026-07-24, the
> existence of `srg(99,14,1,2)` remains `UNKNOWN`; a 2025 refereed
> article explicitly describes it as open, and the later 2026 SAT
> preprint reports no resolution.  Standard constituent lattice,
> discriminant-form, theta, neighbor, and frame results are cited
> individually.  No direct source was found for the exact combined
> Wave 28 package, but this does not establish novelty.  No determinant
> row, `n3=708`, endpoint lattice, projector frame, graph, or Conway
> configuration is constructed or excluded by this audit.

## Limitations

- Web and bibliographic discovery is not a complete proof of the
  literature universe.
- One official graph-table page could not be opened by the web service.
- No direct authenticated zbMATH connector was available.
- The audit checks source attribution and theorem hypotheses; it does
  not rerun or certify the Wave 28 arithmetic.
- Catalogue fields are not extended beyond what the pages explicitly
  state.
- A non-hit is never used as evidence of novelty or nonexistence.
