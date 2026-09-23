# Wave147 independent pair-root/order-eight verification

Verdict: `PASS_WITH_SCOPE`.

The sealed discovery manifest has SHA-256
`0c7585f996374246918948eb1537e61e2e165474f815a66eff24bf82e7c8e690`.
All eleven entries pass their recorded hashes. The verifier does not import
or execute any Wave147 discovery module.

## Independent reconstruction

The verifier rebuilt every locally admissible rooted order-five flag while
fixing roots `0,1` pointwise and quotienting only the three free vertices.
The bases exactly match the stored ordered lists:

```text
ordered edge:       66 flags
ordered nonedge:    87 flags
```

Starting from the frozen 208-class Wave45 order-seven stream, it independently
tested all `208*128` new-vertex neighborhoods. There were 10,472 locally
admissible labelled extensions. Complete degree-cell canonicalization reduced
these to exactly 916 unlabelled classes, with stream SHA-256

```text
c2cf3604abc76a537eca21f1a8ef041697ca40d8ad41668d25eb412b9cd67337
```

and an exact element-by-element match to the stored mask list. This extension
is complete because deleting any vertex of a locally admissible order-eight
graph leaves a locally admissible order-seven graph, and graph isomorphisms
preserve degree cells.

## Artifact and deletion layer

The GZip artifact is canonical JSON after decompression. Independent checks
give:

```text
uncompressed bytes:                  2,851,753
payload SHA-256:                     a7402e77048090ea492c435190aadc1d32bd1df99276e612f6d199aec9e14b08
gzip bytes:                            583,493
gzip SHA-256:                        a46d8a8b6fd3ae339cdf7c9b633a661d917e3481bed762ae6aa70f1b4886cf1e
class-matrix records:                    2,414
nonzero upper-triangular entries:      272,054
deletion rows / nonzero terms:       208 / 5,333
```

Every record key follows the exact `21+62+208+916=1,207` class stream in
each family. Every coefficient is a positive integer at a valid
upper-triangular matrix position.

The verifier independently deleted all eight vertices of all 916 order-eight
classes, canonically translated every deletion to the frozen order-seven
labels, and reproduced the complete stored equations

```text
92*x_H7 = sum_K d(H7,K)*x_K.
```

Every order-eight column has total deletion multiplicity eight.

## Coefficient semantics and target carrier

For each root family, the verifier reconstructed three deterministic class
matrices at each union order 5, 6, 7, and 8: 24 representative matrices in
total. Every upper-triangular entry matches the artifact.

It separately rebuilt the complete order-six matrices for `N3` and the
triangular prism. The selected entries are confirmed exactly:

| family | flag masks | matrix position | `N3` | prism |
|---|---|---:|---:|---:|
| ordered edge | `185,199` | `(29,32)` | **4** | **0** |
| ordered nonedge | `186,206` | `(36,42)` | **4** | **0** |

The full matrix checks also reproduce:

```text
edge:       N3 rank/sum 13/192, prism rank/sum 6/216
nonedge:    N3 rank/sum 10/168, prism rank/sum 4/144
```

Thus both moment entries genuinely contain `4*n3` and no prism term. Other
class counts still contribute, so this is not an isolated `n3` equation.

## Rook-graph positive control

The independently constructed `3 x 3` rook graph has degree four, one common
neighbor for adjacent pairs, and two for nonadjacent pairs. It has 36 ordered
roots of either relation and 35 free triples per root.

For both flag families all 36 root count vectors are identical. Their direct
integer outer-product sums therefore have rank one and are positive
semidefinite, with

```text
sum of all entries = 36*35^2 = 44,100
trace = 2,412.
```

Independent six-subset enumeration gives zero induced `N3` copies and six
triangular prisms.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave147-pair-root-order8\independent_verify.py

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave147-pair-root-order8 -p "test_*.py" -v
```

The rebuild completes without an SDP or any other solver. Seven focused tests
pass. Free physical memory stayed near 39%, above the verifier's 20% floor.

## Scope wall

This verifies the flag bases, complete locally admissible order-eight stream,
artifact integrity/counts, full ordinary deletion layer, representative
coefficient semantics, complete target/prism matrices, and the rook control.
It does not independently recompute all 272,054 coefficient values.

The stronger marked-vertex and marked-pair order-eight SRG extension rows
remain unbuilt. No SDP was run, no rational dual certificate exists, and no
strict `n3` upper bound follows. Conway-99 and external novelty remain
`UNKNOWN`.
