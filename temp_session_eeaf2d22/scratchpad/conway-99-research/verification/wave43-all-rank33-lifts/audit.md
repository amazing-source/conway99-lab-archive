# Independent audit

The verifier hash-binds the frozen Wave 41 source and package manifest but
does not execute or import Wave 41 or Wave 43 discovery code.

Completeness checks:

- direct enumeration of all `3 * 15 * 15 * 6 = 4,050` normalized quotients;
- exact quotient-rank distribution, including all eight rank-eleven forms;
- recovery of canonical normalized index `1446`;
- direct evaluation of all `2^18=262,144` pairing masks and all sixteen
  quotient-triangle forbidden assignments;
- dense modular ranks for all 37,378 triangle-free masks;
- exact ordered 264-mask stream, SHA-256
  `167ba5c0a4b40fb3711fbc861a03a853a125651f4c569dfd5688dd0cca90b130`;
- for each mask, direct forced-Gram reconstruction and all 216,000
  three-fibre pair triples;
- exact equality of all 264 full discovery records.

For every mask, the forced Gram matrix has two components of sizes `12+24`,
fibre balances `(4,4,4)+(8,8,8)`, minimum entry zero, and rank 33 modulo
`1,000,003`. The two fibre-difference vectors and the small/large component
contrast are independently checked integer-kernel vectors of independent
rank three. Therefore they span the rational kernel of each rank-33 Gram
matrix.

The verifier explicitly rejects these inferences:

- the five numerical census classes are not proved isomorphism classes;
- survival of necessary filters is not a complete `B` or compatible `H`;
- local labelled completeness does not assume or produce an automorphism of
  a completed graph;
- there is no endpoint exclusion, strict upper bound, graph, or Conway-99
  solution.

Metadata note: the discovery `exact-results.json` currently has SHA-256
`31e2e5d767c02f9e520f33a980584e2ae24df8a4fc1bbd7b381797209b97e198`,
while its discovery run report lists an older hash. This does not affect the
exact mathematical comparison, but central integration should bind the
actual file hash.
