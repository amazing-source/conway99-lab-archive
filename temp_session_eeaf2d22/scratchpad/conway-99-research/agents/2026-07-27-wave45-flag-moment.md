# Wave 45 finite flag moments

## Scoped result

`DERIVED`, with endpoint and Conway-99 status `UNKNOWN`.

Wave 45 constructs exact finite positive-semidefinite moment constraints from
products of rooted flags. Unlike the earlier aggregate equalities, each matrix
is a sum over labelled roots of outer products of rooted flag-count vectors,
so it couples overlapping induced subgraphs.

The smallest matrices closing in the verified order-six/seven variables are:

- one labelled vertex with four-vertex flags: `17 x 17`, union orders `4..7`;
- two labelled ordered adjacent vertices: `16 x 16`, union orders `4..6`;
- two labelled ordered nonadjacent vertices: `19 x 19`, union orders `4..6`.

All overlap sizes and labelled-root/free-subset embedding multiplicities were
enumerated exactly. No automorphism of a hypothetical target graph is assumed.

## Exact findings

- The frozen Wave 43 and Wave 44 endpoint witnesses are exactly indefinite in
  the one-vertex matrix.
- Their minimum normalized numerical eigenvalues are approximately
  `-0.00252177` and `-0.00851165`.
- Six numerical negative modes for each witness were rationalized to exact
  integer vectors with strictly negative integer quadratic values.
- The ordered-edge and ordered-nonedge matrices are exact LDL-PSD of rank one.
- Direct Petersen and Clebsch SRG controls equal their unrooted coefficient
  expansions exactly and are PSD.
- Hostile diagonal and embedding-coefficient mutations are rejected.

The seed-0 exact QF_LIA cutting loop then found 15 fresh nonnegative integer
solutions of every one of the 170 Wave 44 equations. Each solution replayed
exactly, but each again violated the vertex moment and generated a primitive
exact linear PSD cut. The next solve timed out.

Thus v1 rejects 17 explicit count witnesses. It does not prove the entire
integer feasible region empty.

## Immutable handoff

The immutable v1 package is documented in
`attempts/wave45-flag-moment/README-v1.md`.

Primary hashes:

- seed-0 checkpoint:
  `96a50f9add4b12b2c86587da29ade8b9da34f88a7b7617c048ffb7139c12b64b`;
- coefficient checkpoint:
  `ffcf9f9942446d66c3559d97954217af3ba17c1978ea9417c6e99920d4a45420`;
- stored-witness result checkpoint:
  `2c55b6ab1af9cac7d8f5800466abadb8c0c2603b5f96013d3fd160b6816c24df`;
- v1 package manifest:
  `57f184e5df79ada19f0f08ea6eb9c6c1040517172a0f5e1e6878d09c8d0dd658`.

The versioned replay independently reconstructs all coefficient tensors, 17
cuts, 15 witnesses, all 170 residuals per witness, and all negative quadratic
directions. Package manifest `9/9`, YAML, and exact replay pass. A separate
clean-room verifier also passed v1.

Mutable live-search files and logs are excluded from the v1 package. The live
search has been upgraded to retain every negative eigendirection from each
integer witness, rather than only its most-negative direction.

## Next mathematical level

If the full one-/two-root PSD region survives, the next available matrix
without first building order-eight variables is a three-labelled-vertex type
with five-vertex flags; its products still unite on at most seven vertices.
After that, ordered-pair five-vertex flags require order-eight variables and
one-root five-vertex flags require order nine.

## Status wall

- finite coefficient construction: exact;
- 17 specific witnesses: exactly refuted;
- all-direction live QF_LIA/PSD feasibility: in progress;
- endpoint `n3=4158`: `UNKNOWN`;
- strict upper bound below `4158`: `NOT_PROVED`;
- graph construction: false;
- Conway-99: `UNKNOWN`.
