# Wave 59 incidence spectral-excess protocol

Status at freeze: discovery only. All graph claims are conditional on a
prism-free hypothetical `srg(99,14,1,2)`.

## Frozen objects

Let `N` be the 99-by-231 point--triangle incidence matrix. Define:

```text
L = [[0,N],[N^T,0]]
K = N^T N - 3I.
```

Thus `L` is the point--triangle incidence graph and `K` is the graph on the
231 triangles in which two triangles are adjacent exactly when they share a
point.

Triangle relations are:

```text
I: equal
K: share one point
B: disjoint with two cross edges
C: disjoint with one cross edge
D: disjoint with no cross edge.
```

The symbol `K` for the triangle graph and the relation `K` are the same
adjacency relation; context will distinguish the matrix from the label.

## Tasks

1. Derive `NN^T=A+7I`, the exact spectra of `L` and `K`, connectivity,
   girth, diameters, and all distance-layer sizes without a graph
   automorphism assumption.
2. Reconstruct the rooted relation counts `K=18`, `B=36`, `C=144`,
   `D=32` and the point--line distance layers.
3. Check whether the incidence graph can be distance-biregular. Record
   nonconstant predecessor counts rather than treating their presence as a
   contradiction to mere graph existence.
4. Apply the ordinary spectral-excess theorem only to the connected regular
   triangle graph `K`. Check the semiregular hypotheses separately before
   mentioning a distance-biregular theorem for `L`.
5. Derive the predistance polynomial of degree three for `K`, its spectral
   excess, and the exact defect from the distance-three matrix.
6. Derive the Ihara--Bass determinant and exact nonbacktracking moments. Only
   convert a moment to a simple-cycle count when the girth makes that
   conversion valid.
7. Explore PSD, rank, coherent-algebra, generalized-polygon, and cage
   consequences. Retain null routes and exact boundaries.

## Independence and safety

- No target vertex-, edge-, triangle-, or relation-transitivity is assumed.
- Uniform counts must follow from the strongly regular parameters and a
  fixed root, not from automorphisms.
- Formal matrix identities are checked over exact integers or rationals.
- A spectrum, integral walk count, or strict spectral-excess inequality is
  not a graph construction or nonexistence proof.
- Discovery cannot promote itself to `VERIFIED`.
- Every computation aborts if free physical memory falls below 15 percent.

## Success conditions

A contradiction must be an exact violation of a necessary condition under
checked hypotheses. Otherwise the result is a `DERIVED` smaller obstruction
or a retained null route, with Conway-99 and the prism-free endpoint left
`UNKNOWN`.

