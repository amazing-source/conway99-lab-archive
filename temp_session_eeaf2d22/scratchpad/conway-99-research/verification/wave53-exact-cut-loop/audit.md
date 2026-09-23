# Wave 53 exact-cut-loop independent audit

## Verdict

`REFUTED_IN_PART`.

Two claims must be separated.

1. The fixed rational relaxation with 174 baseline catalog entries and the
   three retained Wave49 cuts is **VERIFIED EXACTLY FEASIBLE**.  The four
   rational witnesses satisfy every one of the 170 Wave44 equations, every
   cumulative cut in its original sealed scaling, all 208 nonnegative bounds,
   and `2079 <= h11/4 <= 4158`.
2. The claim that all 32 matrices at all four witnesses are indefinite is
   **REFUTED**.  The correct census is 120 indefinite and 8 PSD.  All 12
   reported Wave45 direction quadratics are wrong; the eight edge/nonedge
   matrices are PSD and the four vertex matrices remain indefinite by
   different independently derived negative directions.

No endpoint, integrality, graph, strict-upper-bound, Conway-99, or novelty
status is promoted.  Endpoint `n3=4158` and Conway-99 remain `UNKNOWN`.

## Separation and freeze

The clean-room protocol was frozen before discovery source inspection:

- `protocol-freeze.md`:
  `b52386ccdeb8025ece745e2a83b19549b47cb1e0e707fd84cba5043e9b7bad0a`;
- independent checker:
  `4101c11f3faf3536c9d11632592e9caf2ee4706893353bfb9199600d0f03f7e2`;
- preinspection independent result:
  `a81c158f85f5aa0b18be6c72404c3b4877c0acccf9a185ef5aa44672c1cd3591`;
- complete preinspection ledger: `preinspection-freeze.sha256`.

The checker uses standard-library integers and `Fraction` for every equality,
sign, cut, normalization, and matrix conclusion.  It independently
canonicalizes induced subgraphs, rebuilds all lower decks, and never imports a
Wave53 discovery module.

## Exact witness and LP replay

The Wave51 support-136 witness is exactly Wave53 iteration 0.  Original sealed
cut scaling--not merely primitive-equivalent scaling--was replayed after source
inspection.

| iteration | witness SHA-256 | support | cuts | tight | minimum positive slack |
|---:|---|---:|---:|---:|---:|
| 0 | `dea6f733ee8c5a39b6906a702048965927a1598a3072c248c67ea70b701a8660` | 136 | 174 | 66 | 133056 |
| 1 | `da0f9ce866da5b7ac744c15d641253523583a37a05f55379175a7d251b2acb74` | 132 | 175 | 68 | 133056 |
| 2 | `f290045326df9e98b5532da6ec72b692f57ad61f52e577fc123b29f40ac0b672` | 136 | 176 | 70 | 133056 |
| 3 | `49f19b30fffd4136252615e94541fca6eac40990231a819b8004cd2d8be113a2` | 138 | 177 | 70 | 133056 |

For every row:

- all 170 exact residuals are zero;
- all 208 coordinates are nonnegative;
- `h11/4 = 4158`, within the declared bounds;
- all cumulative cut slacks are nonnegative; and
- all order-4/5/6/7 deck totals equal `binom(99,k)`.

The baseline ID catalog hash independently recomputes to
`7f355f81e9c1c94cd251e360872f1d14f45b1aa2555186cde805a96183c9d28c`.
It contains 174 catalog entries (`17 + 136 + 21`), but only 106 distinct
primitive normalized inequality rows: 34 duplicate groups account for 68
excess entries.  This does not invalidate feasibility, but "174-cut" must be
understood as a ledger count, not 174 distinct halfspaces.

## Retained Wave49 cuts

All three retained cuts survive independent reconstruction from the Wave49
coefficient tensors, primitive directions, and exact deletion identity.

| iteration | root | primitive direction | cut ID | result |
|---:|---:|---|---|---|
| 0 | 220 | `[4,-3,-3,0,-3,0,0,0,-3,0,0,0,0,-3,0,0,0,0,0,0,0]` | `33050a2dedb7b7a9c59a8e6778029f8477c5fe09def8af4ac8631b1e7a851d19` | exact source rejection; exact successor |
| 1 | 62 | `[4,-3,-2,-3,0,0,-3,0,0,-2,0,-1,0,0,0,0]` | `efcd988d6b89ea6873b5a81281d41b6f6b938ac4df94368f73ed8f48b1cb9eca` | exact source rejection; exact successor |
| 2 | 221 | `[4,-2,-2,-2,0,-2,0,0,-3,0,0,0]` | `7923bfc7be97e5acf144316fb110f8e40b96d128334f961c328e7a8ad872c2bc` | exact source rejection; exact successor |

For each cut, coefficients, direction, denominator LCM, primitive divisor,
linearization multiplier, exact matrix value, exact source value, ID, and
successor feasibility match.  The new-cut catalog hash independently
recomputes to
`9ea8d9d57af691f09742868f1d3ba0032227e6c3e9294b728b02c45dbadc736b`.
The same roots remain the exact selection-rule minima after correcting Wave45.

## Matrix correction and root cause

Wave45's independent coefficient input stores full symmetric entries: every
off-diagonal `(i,j,c)` already has `(j,i,c)`.  This was checked over 1,522
edge, 2,322 nonedge, and 11,848 vertex off-diagonal entries with zero missing
reverse entries.

In `exact_cut_loop.py`, `family_models` lines 433-446 relabel this full stream
as `upper_entries`.  The generic `add_upper` at lines 262-275 then mirrors
every off-diagonal again.  Consequently each Wave45 discovery matrix has the
correct diagonal but twice the correct off-diagonal.  The independent
comparison reproduces all 12 reported Wave45 matrix hashes and quadratics
exactly from this defect.

The corrected matrices and exact quadratic strings are machine-readable at
`comparison-result.json` under
`wave45_double_offdiagonal_defect.details`.  The SHA-256 below is the corrected
full-matrix serialization used by the discovery schema; `q SHA-256` hashes the
exact corrected rational string at the same JSON location.

| iteration | family | correct status | correct matrix SHA-256 | corrected q SHA-256 |
|---:|---|---|---|---|
| 0 | edge | PSD | `7e9fb8fcbb802f5569dfd5f344863f9173e063d82a4864bd04b614b9c04e38fc` | `307cb8a787a9062855128b298282913136bc6ce8e37146ee73776d8e28f9ee7a` |
| 0 | nonedge | PSD | `7d063f3d240c5d44e87fab0a31db457f8505ca416e6effcf4ddb283d6feb1c55` | `639e57e1e0e016da90fcc7846740ce9a2e50daa47f661dc84c8e561323e023f8` |
| 0 | vertex | indefinite | `5a86b84567fc70d29b48f7041f16897ff951a86322f0be9282c990c21661ed99` | `c7f51220cb3e4cb068c18509012bd11b74ec4a7db021a5e68feddafa89989a37` |
| 1 | edge | PSD | `7e9fb8fcbb802f5569dfd5f344863f9173e063d82a4864bd04b614b9c04e38fc` | `307cb8a787a9062855128b298282913136bc6ce8e37146ee73776d8e28f9ee7a` |
| 1 | nonedge | PSD | `7d063f3d240c5d44e87fab0a31db457f8505ca416e6effcf4ddb283d6feb1c55` | `639e57e1e0e016da90fcc7846740ce9a2e50daa47f661dc84c8e561323e023f8` |
| 1 | vertex | indefinite | `cc3673dff03e3f5ead4cc696ede779616dbe1017e1aa7137defe5402b0e13e6f` | `e319f2198fc85b92249b9c69386fee03d740b818b1262cf5bf7f1a6970c80501` |
| 2 | edge | PSD | `7e9fb8fcbb802f5569dfd5f344863f9173e063d82a4864bd04b614b9c04e38fc` | `307cb8a787a9062855128b298282913136bc6ce8e37146ee73776d8e28f9ee7a` |
| 2 | nonedge | PSD | `7d063f3d240c5d44e87fab0a31db457f8505ca416e6effcf4ddb283d6feb1c55` | `639e57e1e0e016da90fcc7846740ce9a2e50daa47f661dc84c8e561323e023f8` |
| 2 | vertex | indefinite | `8dcd8fef1e8bd7b95644d8b616f5dc9ecae0733fc38de947276b4ae8f34875b5` | `38dee6fbbabc834e4906e25cf612fe6e336fd58ab2bf903d97f1a6bcf1eafb18` |
| 3 | edge | PSD | `7e9fb8fcbb802f5569dfd5f344863f9173e063d82a4864bd04b614b9c04e38fc` | `307cb8a787a9062855128b298282913136bc6ce8e37146ee73776d8e28f9ee7a` |
| 3 | nonedge | PSD | `7d063f3d240c5d44e87fab0a31db457f8505ca416e6effcf4ddb283d6feb1c55` | `639e57e1e0e016da90fcc7846740ce9a2e50daa47f661dc84c8e561323e023f8` |
| 3 | vertex | indefinite | `52ed54b440c1e509af15523ca718cfc184bf022d29f447a355aacd4093dd40f4` | `f1d23b13b62960abaf6bf8770c524a2a8d4101131c889211c97df762df5637a6` |

The edge and nonedge corrected quadratics on every reported direction are,
respectively, exactly `8927841384` and `116010071100`, both positive.  The
four corrected vertex reported-direction quadratics are also positive, even
though independent congruence witnesses prove those four matrices
indefinite.  Thus 116 Wave47/Wave49 evaluations are correct, while all 12
Wave45 reported direction evaluations are wrong.

## Cut deduplication and selection attack

At every witness the 32 candidate records reduce to 28 distinct primitive
normalized order-seven rows.  The two duplicate groups are the Wave47 root
permutation triples:

- `root_001`, `root_010`, `root_100`;
- `root_011`, `root_101`, `root_110`.

After correcting Wave45, 29 candidate records reject their source, representing
25 distinct normalized rows.  The discovery's reported
`eligible_nonduplicate_candidates: 32` therefore does not mean distinct
mathematical cuts.  This metadata is refuted, but the retained roots
`220,62,221` still minimize the stated exact score and are not duplicates of
the cumulative ledger.

## Excluded fourth dense Wave45 route

The excluded fourth direction is the terminal Wave45 vertex direction.  Under
the duplicated-offdiagonal source matrix it produces a 208-nonzero row with a
strictly negative source value.  Under the correct Wave45 matrix and
linearization, the same direction also produces 208 nonzeros but has a
strictly positive terminal value.  Exact values for both rows are recorded in
`comparison-result.json` under `excluded_fourth_dense_wave45_cut`.

The reported `7.431e-10` residual is not zero and therefore is not exact
coefficient cancellation.  The package contains no exact nonnegative
multiplier vector or exact constant identity; the discovery reconstruction
explicitly rejected it.  It cannot support infeasibility.  Moreover, its
input "cut" came from the incorrect duplicated-offdiagonal matrix, so it is
not the claimed Wave45 rank-one moment cut.

## Manifests, parsing, tests, and resources

- All Wave53 input-freeze entries, package-manifest entries, and 13 result
  input records matched before verifier output was added.
- Rational parsing attacks reject floats, exponent notation, noncanonical
  integers, signed denominators, zero denominators, booleans, and nonfinite
  values on exact paths.
- Independent test suite: 11/11 passed.
- Discovery validation replay passed and discovery stored-result tests passed
  6/6, but these are self-consistent with the defect: validation loads the
  same full Wave45 stream through the same double-mirroring path, while the
  stored-result test checks reported negativity without reconstructing the
  correct matrices.
- Independent physical memory was 52.817132% free at start and 51.638869% at
  finish, both above the required 15% reserve.  The discovery's historical
  `>20%` samples are not embedded, so that historical telemetry is not
  independently certifiable; no contradiction was observed.

## Claims that change

Changed:

- `128/128 exactly indefinite` -> **refuted**; correct census `120/128`
  indefinite and `8/128` PSD.
- all 12 Wave45 displayed directions are negative -> **refuted**; their
  correct quadratics are positive.
- terminal `32` indefinite -> **refuted**; terminal census is `30`
  indefinite and `2` PSD.
- `32 eligible nonduplicate candidates` -> **refuted as semantic
  deduplication**; there are 28 unique normalized rows, and 25 unique
  source-rejecting rows after matrix correction.
- the excluded fourth dense candidate is a valid Wave45 separating cut ->
  **refuted**.

Unchanged and independently verified:

- exact rational feasibility of the fixed cumulative systems through 177
  catalog cuts;
- support sequence `136,132,136,138`;
- exact validity, primitive normalization, source rejection, ordering, IDs,
  and successor feasibility of Wave49 roots `220,62,221`;
- all 116 Wave47/Wave49 displayed matrix quadratics;
- continued failure to find a full-PSD witness, because 30 correct terminal
  matrices remain indefinite.

Unchanged and unresolved:

- integer feasibility, graph construction, full PSD feasibility, full cut
  ledger feasibility, endpoint `n3=4158`, strict upper bound, Conway-99, and
  novelty.
