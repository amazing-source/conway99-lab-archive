# Wave 49 five-root moment audit

## Verdict

`VERIFIED_SCOPED`.

The exact coefficient, relabelling, control, and finite-witness claims match a
clean-room reconstruction. There are zero comparison mismatches. The
numerical combined SDP is not part of this verdict.

## Precomparison separation

The verifier first read only the supplied verifier protocol and frozen input
list. It then independently implemented:

- exhaustive labelled graph enumeration under the common-neighbor caps;
- complete `S_n` orbit removal by minimum relabelled edge mask;
- five-root attachment coordinates;
- raw ordered root-injection tensors at orders six and seven;
- all `S5` coordinate congruences;
- Petersen and Clebsch direct outer-product controls;
- exact deletion decks and 357 witness matrices; and
- independent exact negative integer directions.

Before opening `coefficients.json`, `results.json`, or the discovery code, the
implementation, coefficient document, and result were sealed in
`precomparison-freeze.sha256`. The independent result SHA-256 is
`77fc1e5d6b7d5ca417cdfd61cfef14cdb6d777d85b43cc17f2bad10af2a45930`.

## Class and tensor reconstruction

| order | labelled admissible | unlabelled classes | canonical stream SHA-256 |
|---:|---:|---:|---|
| 5 | 683 | 21 | `f9bd6d5818a81c1b026ac46e467609435576a54f933e6d5beac5c13b20259686` |
| 6 | 13,174 | 62 | `5cd10b0861dfba894731a89a269255a7c0a495f8ee7420552aebb13bafb8b75f` |
| 7 | 394,020 | 208 | `89c646b6cae3018cad44b2f73cd1ef2569f4e108132002f0bcc7653d7229314a` |

Every order-six class receives exactly `6P5 = 720` raw root-injection
contributions. Every order-seven class receives
`2 * 7P5 = 5,040` ordered-distinct contributions. These totals are checked
before selecting a root family, so a hidden stabilizer or automorphism
division cannot pass.

All 683 labelled root masks were populated. Their sparse tensor commitment is
`c239f2b4f31a26dc331f5ad28d664cd48e69417384279f78119978469ec30f80`,
covering 67,054 nonempty root/class records and 407,194 nonzero ordered
attachment entries.

For each of the 21 canonical roots and all 120 permutations, the verifier
explicitly permuted each five-bit attachment coordinate and compared every
order-six and order-seven class tensor. This gives 2,520 attachment
bijections and 680,400 coefficientwise class checks. All pass. This is root
coordinate relabelling, not a target-graph symmetry.

The independently reconstructed discovery-schema coefficient document equals
`attempts/wave49-five-root-moment/coefficients.json` exactly. Its canonical
payload SHA-256 is
`940ed2820a3501e1b5017a5a3dafce55789ce189a754ef94af01954f28a79511`.

## Exact controls

Petersen was rebuilt as a five-cycle, five spokes, and inner five-star.
Clebsch was rebuilt on four-bit strings, adjacent at XOR difference
`1,2,4,8,15`. Their strongly regular parameters independently evaluate to
`(10,3,0,1)` and `(16,5,0,2)`.

For every one of the 42 graph/root pairs:

1. each ordered five-root embedding was enumerated;
2. its remaining-vertex attachment-count vector was formed;
3. the direct matrix was summed from integer outer products;
4. the coefficient expansion over induced order-six/seven classes was
   evaluated;
5. both matrices were compared entrywise; and
6. the all-ones identity
   `sum(M) = root_embeddings * (graph_order - 5)^2` was checked.

All direct and expanded matrices and discovery hashes agree. Positive
semidefiniteness is exact by the displayed integer Gram construction, not by
a numerical eigenvalue test.

## Supports, decks, matrices, and directions

All 17 support lists are sorted, unique, use canonical order-seven classes,
match their frozen support hashes, and total `binom(99,7)`.

Deleting vertices and canonicalizing every card gives a common lower deck:

- order five:
  `2401552a01692a2ac65b6c0df65c29b3ca5bb9f5d4cf67951cdb0e2fbb7b9032`;
- order six:
  `0050a1de6446a5b64af4c98c985b1812cf7241f3c30b71f0ae0f598537228861`.

Every derived count is nonnegative and integral after division by the exact
deck multiplicity, and every deck totals `binom(99,k)`.

For each support and each canonical root, the verifier rebuilt the exact
integer matrix from the order-six same-free and order-seven
ordered-distinct tensors. All 357 matrix hashes and all-ones normalizations
match discovery. The independent lane found an exact negative integer
direction for every matrix before comparison.

After comparison, all 357 supplied discovery vectors were independently
parsed and reevaluated against the reconstructed matrices. Every dimension,
matrix hash, stored numerator, and strict inequality `v^T M v < 0` agrees.
Floating minimum eigenvalues were not used.

## Hostile tests

Eight focused tests cover:

- a graph violating the common-neighbor cap;
- edge-bit-order and relabel-map mutation;
- a nonbijective attachment map;
- swapping the same-free and distinct-free conventions;
- automorphism division of raw totals;
- tensor-coefficient and support-count mutations;
- matrix/direction-coordinate mutation; and
- accidental use of numerical SDP fields as evidence.

All pass.

## Packaging note

The discovery directory had no `package-manifest.sha256` when compared.
Therefore the verifier records the exact current hashes:

- `coefficients.json`:
  `66aeb26175643030770c8060a0550d202c56b6a9636e245ef19866a4a9cf308d`;
- `results.json`:
  `f8604031259a92776b29cda161344fd9b2bdf3ea395c3d8ce53facb82981f8c5`;
- `combined-sdp-result.json`:
  `1e41b1fd961714b24f69d1c31474f48b91dca88d938f5c97d5aa2424b8aac152`.

This is a publication-integrity limitation, not a mathematical mismatch.

## Scope wall

The 17 recorded aggregate witnesses are all exactly refuted by the five-root
PSD necessity. This is a finite witness ledger, not a complete search of the
PSD-constrained count region. No branch is closed, no endpoint is excluded,
no strict upper bound is improved, no graph is constructed, and no novelty or
Conway-99 conclusion is established.
