# Wave 25 source-first literature and novelty audit

Date: 2026-07-23

## Verdict

No exact literature match was found for the supplied Wave 25 refinement in 30
queries frozen before proof inspection.  In particular, the search found no
source that combines the Conway-99 / `srg(99,14,1,2)` context with the
`n3 = 708` equality case, an integral self-adjoint idempotent splitting, the
even-unimodular rank-36 obstruction, `det(B) <= 6525`, or the exact surviving
index list

`{9,21,49,81,189,441,729,1029}`.

This is a **bounded non-discovery**, not a novelty proof.  The exact refinement's
novelty remains `UNKNOWN`.

The target existence status also remains `UNKNOWN`.  The strongest current
status evidence inspected here still records the parameter set as unresolved:

- Cesarz and Woldar's peer-reviewed 2025 paper calls existence an elusive open
  problem and studies only restrictions on a putative graph's automorphism
  group ([article and publication record](https://alco.centre-mersenne.org/articles/10.5802/alco.418/)).
- Brouwer's current strongly-regular-graph table marks the row
  `(99,14,1,2)` with `?`
  ([orders 51--100 table](https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html)).
- A 2025 Australasian Journal of Combinatorics article independently states
  that existence is unknown
  ([journal PDF](https://ajc.maths.uq.edu.au/pdf/93/ajc_v93_p060.pdf)).

Those sources support keeping the repository status unresolved; they do not
prove that no later or unindexed resolution exists.

## Proof separation

The preinspection plan was frozen at `2026-07-23T21:49:09Z` before opening any
Wave 25 discovery, verifier, certificate, or test artifact.  The audit was given
only a claim synopsis.  It did not evaluate the proof and does not promote the
refinement to `VERIFIED`.  Its remit is attribution, chronology, status, and
novelty risk.

## Closest exact-target literature

### The `n3` precursor is published, but 708 is not

Reimbayev's 2024 paper derives the number of hexagons in an
`srg(n,k,1,2)` as a parameter-only baseline plus `n3` and obtains its published
lower bound from `n3 >= 0`.  It discusses `srg(99,14,1,2)` explicitly, but does
not contain the Wave 25 boundary, determinant, idempotent, or rank-36 argument
([journal PDF](https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf)).

The author's later six-vertex-subgraph manuscript treats `n3` as a free variable.
Direct full-text checks found no occurrence of `708`, `idempotent`,
`unimodular`, or `determinant`
([arXiv v2 PDF](https://arxiv.org/pdf/2508.03377)).  Thus these works are
important direct precursors to the quantity being bounded, but are not an exact
match for the refinement.

### Other target-specific arithmetic and spectral work

Ducey et al. compute the critical group forced by the putative graph's
parameters.  This is target-specific integral arithmetic and should be cited
when positioning lattice methods, but it does not give the `n3 = 708`
equality-case obstruction or the determinant ceiling
([arXiv record for the JCTA paper](https://arxiv.org/abs/1910.07686)).

Petro and Phillips apply clique-graph spectral tools to Conway's problem and
still describe the existence question as longstanding.  Their result is
structurally relevant but has no matching Wave 25 numerical or lattice
fingerprint
([arXiv paper](https://arxiv.org/abs/2502.17845)).

## Conceptual prior art that must not be claimed as new

The exact target application was not found, but each broad ingredient has older
context:

1. **Idempotents and lattice Gram matrices.** Bacher and Venkov construct
   integral Gram matrices and lattices from rational minimal idempotents in
   association schemes.  Their Section 2 is clear prior art for the general
   projector-to-lattice viewpoint
   ([1995 peer-reviewed paper](https://www.numdam.org/item/10.5802/aif.1490.pdf)).

2. **Orthogonal rational graph lattices.** Berget, Manion, Maxwell, Potechin,
   and Reiner develop rational orthogonal decompositions, their orthogonal
   projections, determinant groups, and integral Gram presentations in graph
   settings
   ([manuscript](https://www-users.cse.umn.edu/~reiner/REU/line_crit.pdf)).

3. **Even-unimodular rank obstruction.** The fact that the rank of an even
   unimodular positive-definite lattice is divisible by eight is standard;
   Shimada states it explicitly in the introduction to an author-hosted lattice
   paper
   ([manuscript PDF](https://home.hiroshima-u.ac.jp/ichiro-shimada/preprints/Extremal64/PaperGQR/shimadaLat64.pdf)).
   Consequently, once an argument really produces an even unimodular
   positive-definite lattice of rank 36, the contradiction is established
   prior theory, not a new theorem.

4. **Integral idempotent splitting.** For an idempotent endomorphism
   `e^2 = e`, the decomposition into `im(e)` and `ker(e)` is elementary module
   algebra; self-adjointness makes the two summands orthogonal.  The novelty
   question is therefore the exact derivation of such an integral idempotent
   from the Conway-99 equality case, not the splitting lemma itself.

Accordingly, any future public claim should distinguish a potentially new exact
Conway-99 synthesis from these established ingredients.

## Fingerprint results

The exact-value searches were deliberately redundant:

- Both `"6525"` queries tied to Conway-99 and both determinant-form queries
  returned no relevant mathematical source.
- The quoted eight-value list returned no source; the shortened
  `1029 / 729 / 441 / strongly regular` query also returned no target match.
- All six target-plus-idempotent/even-unimodular/orthogonal-split queries
  returned no exact match.
- Both `n3=708` spelling variants returned no relevant source.
- Current target queries recovered recent papers and the authoritative parameter
  table, but none of the Wave 25 fingerprints.

All nulls, irrelevant returns, source URLs, and access failures are retained in
`source-query-ledger.json`.

## Limitations

- Web and bibliographic indexing can lag, omit theses or preprints, and rank
  exact mathematical notation poorly.
- Search-result counts were not exposed and were not guessed.
- No MathSciNet or zbMATH subscription search was available in this run.
- The literature audit did not contact authors, inspect private manuscripts, or
  search non-indexed conference proceedings exhaustively.
- Full text at ScienceDirect was access-blocked; the author/arXiv version and
  journal metadata were used for the critical-group paper.
- This audit does not check any mathematical step of Wave 25.  A verifier must
  independently reproduce the idempotent, parity, determinant, and index-list
  deductions.

Therefore the only defensible novelty statement is:

> No exact match was found in this frozen 30-query audit and its inspected
> primary sources; novelty remains `UNKNOWN`.
