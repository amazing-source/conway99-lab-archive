# Wave 26 `A2` frame-obstruction literature audit

## Executive verdict

**Literature/novelty status: `UNKNOWN`.** No source matching the exact
parameter-specific claim was found in the scoped search through 2026-07-23.
That is a non-discovery result, not evidence that the claim is novel.

The search did find substantial prior art for each broad ingredient:

- tight-frame Gram matrices and orthogonal projectors;
- integer/rational frames whose integral spans are lattices;
- eutaxy and spherical-design moment identities;
- tight-frame embeddings of strongly regular graphs; and
- Hadamard (Schur) products and powers of Gram matrices.

All of those findings are class M machinery. No inspected source was class D
(direct) or N (near-direct) for the assertion that a required 231-row
projector/Hadamard-square structure excludes every orthogonal `A2` summand,
let alone for the hypothetical `srg(99,14,1,2)`, `n3 = 708`, and
`E8^5 orthogonal-sum A2^2` endpoint.

This audit did not assess the discovery proof. Its mathematical validity also
remains `UNKNOWN` here.

## Frozen statement and separation

The preinspection statement, source rules, exact Q01–Q28 strings, and status
rules were frozen at `2026-07-23T22:50:16.910Z` in
`protocol-freeze.md`. No Wave 26 proof artifact had been inspected at that
time. Repository artifacts were inspected only afterward and only to sharpen
terminology. This literature agent has no authority to promote a discovery to
`VERIFIED`.

The post-freeze terminology pass encountered two proof-side formulations:

1. a 231-by-44 integral frame with a tight-frame identity and restricted row
   norms/inner products; and
2. a matrix denoted `W = M Hadamard-product M`, used as a cubic-tensor or
   moment bridge.

Those are discovery-side assertions, not findings of this audit.

## Important terminology correction

The frozen request used “Schur-origin” and also requested Schur-complement
searches. The Wave 26 usage is an entrywise **Schur/Hadamard product** (in
particular, a Hadamard square), not the block-matrix **Schur complement**.

The frozen Q23–Q25 searches therefore mostly returned unrelated numerical
linear algebra, operator, and block-matrix literature. The post-freeze
S01–S04 terminology correction found the genuinely relevant general lane:
Peng–Waldron on Hadamard products of Gram matrices, outer-product-frame
machinery, and recent Gramian formulations of spherical-design moments. None
of those sources states the target `A2` obstruction.

## Findings by question

### 1. Direct or near-direct `A2` summand obstruction

No inspected source states that an orthogonal `A2` lattice summand is
incompatible with a 231-row integral tight-frame/projector representation, a
specified row alphabet, or the reported Hadamard-square trace/moment data.
Exact phrase and notation variants Q07–Q11, Q27–Q28, S07–S10 produced no
relevant direct match on the inspected surfaces.

Result: **no match in the scoped search; global prior-art status `UNKNOWN`.**

### 2. Parameter-specific match

No relevant source was identified for any of:

- `srg(99,14,1,2)` combined with a lattice or projector;
- `n3 = 708`;
- a 231-row lattice projector/Gram representation; or
- `E8^5 orthogonal-sum A2^2` in this setting.

Crossref and arXiv often returned 20 records for the exact strings, but title
inspection showed lexical collisions and query-parser broadening rather than
parameter matches. Returned-record count is not relevance.

Result: **no match in the scoped search; not a novelty certificate.**

### 3. Tight frames, projectors, and lattice generation

The following general facts are `CITED`:

- Gram matrices of Parseval/tight frames are naturally treated as fixed-rank
  projector data in the frame literature (Tropp et al.; Bodmann–Haas).
- Integer frames are a developed subject (Casazza et al.).
- A real tight frame that generates a lattice must be rational; irreducible
  group-frame lattices are strongly eutactic (Fukshansky et al.).
- Rationality/eutaxy/perfection of lattices generated from tight frames have
  also been treated in the Böttcher–Fukshansky addendum.

These sources establish that the broad setup is not new. They do not visibly
subsume the target row restrictions or an orthogonal-`A2` exclusion.

### 4. Strongly regular graphs and frame embeddings

Barg–Glazyrin–Okoudjou–Yu prove a general correspondence between real
two-distance tight frames and spherical embeddings of strongly regular
graphs, subject to their stated non-antipodal-value condition. Bacher–Venkov
provide older prior art on constructing lattices from association schemes.

This is relevant machinery, but no inspected source connects those results to
the claimed 231-row frame, its larger reported inner-product alphabet, or
`E8^5 orthogonal-sum A2^2`.

### 5. Eutaxy and spherical 2/3-design moments

Nebe’s survey records that indecomposable root lattices are strongly eutactic,
that strong eutaxy is the scalar second-moment identity
`sum_x x x^T = c I`, and that it is equivalent to the normalized minimal
vectors forming a spherical 2-design. Sunada treats irreducible root systems
as crystallographic tight frames. Thus `A2` itself is compatible with these
generic tight-frame/second-moment conditions.

Moreover, a lattice minimal-vector set is antipodal, so every odd homogeneous
moment sum vanishes by pairing `x` with `-x`. A generic degree-three vanishing
condition therefore does not, by itself, exclude `A2`.

This does **not** refute a target-specific obstruction. It shows that any valid
exclusion must use extra information beyond generic tightness, strong eutaxy,
or antipodal degree-three cancellation—for example, the claimed discrete row
alphabet, multiplicities/fibres, integrality, and exact Hadamard-square trace
data.

### 6. Hadamard-square/Gram moment machinery

Peng–Waldron directly study Hadamard products of Gram matrices in frame
theory. Casazza–Pinkham–Tuomanen relate outer-product-frame Gram data to
Hadamard products of the original Gram. Waldron’s 2025 preprint gives general
Gramian potential characterizations of spherical designs. These sources make
the broad `M Hadamard-product M` and Gram-moment lane established prior art.

No inspected source derives the specific Wave 26 count/trace identity or its
reported `A2` consequence.

## Closest collision found

Bodmann–Haas discuss potential-based conditions that can exclude
orthodecomposable Parseval-frame configurations. This is conceptually closer
than generic frame definitions, but it remains class M:

- its hypotheses are potential/critical-point conditions, not the reported
  integral row-alphabet and multiplicity constraints;
- “orthodecomposable frame” is not automatically the same as an orthogonal
  `A2` summand of the associated lattice; and
- the paper supplies no 231-row, SRG-parameter, or `A2` application.

It therefore cannot be cited as the target theorem.

## Status table

| Proposition | Label in this audit | Basis |
|---|---|---|
| Tight-frame/projector Gram machinery exists | `CITED` | S01–S03 |
| Integer/rational lattice-generating frame machinery exists | `CITED` | S04–S06 |
| SRG/two-distance frame and association-scheme lattice machinery exists | `CITED` | S11–S12 |
| Strong eutaxy is a spherical 2-design/second-moment condition | `CITED` | S09–S10 |
| `A2` is compatible with generic root-system tightness/strong eutaxy | `CITED` | S07, S09 |
| Odd moments vanish on antipodal minimal-vector shells | `CITED` | S09 |
| Hadamard products/powers of frame Gram matrices are established machinery | `CITED` | S13–S15 |
| The Wave 26 231-row rules exclude every orthogonal `A2` summand | `UNKNOWN` | Proof not audited; no direct literature match |
| The exclusion theorem is novel | `UNKNOWN` | Scoped non-discovery cannot establish novelty |
| The hypothetical endpoint is impossible | `UNKNOWN` in this audit | Outside literature role and not independently verified here |

Source IDs refer to `sources.md`.

## Publication-safe language

The strongest supported wording is:

> No matching source was found in the scoped literature search through
> 2026-07-23 for the parameter-specific 231-row projector/Hadamard-square
> exclusion of an orthogonal `A2` summand. General frame, lattice-eutaxy,
> spherical-design, strongly-regular-graph, and Hadamard-Gram machinery is
> established prior art. The discovery’s proof status and global novelty both
> remain unknown.

Do not replace this with “novel,” “first,” “new theorem,” “verified,” or
“literature proves the obstruction.”
