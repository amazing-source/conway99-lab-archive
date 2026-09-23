# Wave 41 multiedge rank packing: verifier protocol freeze

Date frozen: 2026-07-27 UTC

Role: independent verifier.

The discovery package under
`attempts/wave41-multiedge-rank-packing/` was treated as opaque while this
protocol was prepared.  Before this freeze the verifier listed file names and
metadata and computed byte hashes, but did not open, import, or execute any
discovery file.

## Exact target

For a hypothetical `srg(99,14,1,2)`, fix a graph triangle `T` and its three
twelve-point neighbour fibres.  For each of the four edge-local cycle
partitions

```text
1+1+1+1+1+1, 3+1+1+1, 5+1, 3+3,
```

independently check the claim that every admissible completion by the third
fibre has

```text
rank_F7((J-I-2A)[T union N(T)]) >= 26.
```

The verification must cover:

1. construction and audit of the complete 39-vertex block;
2. exact arithmetic over `F_7`;
3. the Schur/rank-equality obstruction to rank 25;
4. completeness of every perfect-matching enumeration or compressed
   matching argument;
5. the previously verified transport
   `rank_F7(N M N^T)=rank_F7(M)`;
6. the three-dimensional fibre-constant kernel common to every admissible
   39-block;
7. genuine examples of ranks 28 and 29 as positive controls;
8. hostile mutations of matrices, matchings, arithmetic, status, and
   completeness records.

The seven remaining positive partitions of six,

```text
6, 4+2, 4+1+1, 3+2+1, 2+2+2, 2+2+1+1, 2+1+1+1+1,
```

are outside the claimed strengthening and must remain `UNKNOWN` here.
Because those seven types are not eliminated in a general hypothetical
graph, the universal characteristic-seven floor must remain the already
verified value 25.  No conclusion about existence, the prism-free endpoint,
`n3<4158`, or literature novelty is in scope.

## Independent method fixed before comparison

- Reconstruct each 39-vertex graph from six perfect matchings: one within
  each fibre and one between each pair of fibres.
- Normalize the first fibre matching and the first cross matching.  Generate
  all labelled perfect matchings recursively and verify the count
  `(12-1)!!=10,395`.
- For an all-odd `X-Y` type, build the 27-block `S`, compute a basis `H` of
  `ker(S)`, and enumerate exactly the `X-Z`/`Y-Z` perfect matchings for which
  `H^T U=0` by a bipartite perfect-matching recursion.
- For each equality-border completion, derive the exact residual Schur
  matrix on `Z`.  A full rank of 25 would require this residual to vanish.
  Enumerate every labelled perfect matching internal to `Z` and prove that
  none equals the required residual pattern.  Direct 39-by-39 elimination
  will cross-check witnesses and boundary examples.
- Independently derive the fibre-constant kernel from the six-variable
  quotient equations and check its three explicit vectors against every
  constructed full block.
- Re-derive the incidence rank transport algebraically and test the finite
  linear-algebra steps over `F_7`.

No discovery output, implementation detail, or expected census value beyond
the target statement above is used to design this method.

## Frozen verified premises

```text
4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3  AGENTS.md
7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58  CONJECTURE.md
a136b971ba4e675a5edfe62780e7754b7c716ff1753507be0201eadf3042dfbf  verification/2026-07-27-wave40-orchestrator.md
33201f7cac66df7c65f254d0c3b054cd17cfa67ae54b67cbc5032bee299b924e  verification/wave40-exact-coupling-model/README.md
128bea1e5f7ff347f13e435888d62a6272ebe0968a5f8dc6a0eb2ba22fb99177  verification/wave40-exact-coupling-model/run-report.yaml
d87c7a5eb9377cc3095fff21eec7ff17d94445bef911e4adb092f2db6228bc6e  verification/wave40-exact-coupling-model/independent_check.py
ff7916d0f5c74c47c8d7787c5cbcc84785cbccd3644d8d03d73e47b73908c0f5  verification/wave40-exact-coupling-model/independent-results.json
3ec16bfdb7275ddfde95cf352660ec2440a029f07796f7397ba92d63859a1c79  verification/wave40-edge-type-coupling/audit.md
```

## Opaque discovery package at freeze time

```text
787cd80f79517fa455221c0222dfc709b10f15b8524804019e5cc72d1c5b76de  attempts/wave41-multiedge-rank-packing/exact_check.py
0c20f53b056e0b94f14094d46d957b1b4c5ccd5c6c1920de80ea8ce4e49fdac1  attempts/wave41-multiedge-rank-packing/exact-results.json
074ecd2c65ac963c7a9e16d226e013ad382fdf264a8ece0f766c7b7799081a0b  attempts/wave41-multiedge-rank-packing/failed-routes.md
70f51fc83f0c22deaa94feb06c27b43ec0a684797c1e985f9154f4a2b7c607e3  attempts/wave41-multiedge-rank-packing/input-freeze.sha256
98ab286a8215031ff0b0304fb3cd5510816702fe652878716a5936889fe564f8  attempts/wave41-multiedge-rank-packing/package-manifest.sha256
249ae1cfc99b538709c36f5140470e14e79ba6197b62e508b85458593c7cef56  attempts/wave41-multiedge-rank-packing/README.md
4c84212031b2a0a35add50951b4793fa30b7bf8e519356465021a4c0a68c726d  attempts/wave41-multiedge-rank-packing/run-report.yaml
a35fd813d29056f261a70be6cfda0adb3d4d5cd912cc6a4454f46843c0e9fd33  attempts/wave41-multiedge-rank-packing/test_exact_check.py
```
