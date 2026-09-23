# Wave 3 primary-source and novelty audit

```yaml
role: literature
date_utc: 2026-07-22T21:33:06Z
git_commit: 98ee7b3dac89d57f09c583f83a356b3ef9541b3e
base_commit: d1b6d3d237bac44d10123b7d190c46f092d74eee
claim_label: DERIVED
scope: target-specific prior art and consequences for srg(99,14,1,2)
inputs:
  taylor_adjacent_neighborhood: https://maths.straylight.co.uk/archives/1330
  makhnev_1988_pdf:
    url: https://www.mathnet.ru/php/getFT.phtml?jrnid=mzm&paperid=4220&what=fullt&option_lang=eng
    sha256: ca870226aae6a00af8b878d68bc64ca42c987dff40c4df39caefdab186e20431
  reimbayev_2024_pdf:
    url: https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf
    sha256: 484ff4bbcf13ea26d478baa4c24b97f6996ac3fc35ef8459c15fb61b61b98521
  ibrahim_lafayette_mccall_2025_pdf:
    url: https://ajc.maths.uq.edu.au/pdf/93/ajc_v93_p060.pdf
    sha256: 3bcbb35f6bac46bf943970fa53918fa2b126684375a325efff308371e785fb0f
  verification/literature-audit/verify_reimbayev_six.py: 64a517cf6701b8cec68d57eaad30362e4873307f875745ab75ea731d30687fa2
method: primary-source reading, clean-room finite graph enumeration, exact arithmetic, and targeted search through 2026-07-22
command: python verification/literature-audit/verify_reimbayev_six.py
outputs:
  persistent_output: not_applicable_stdout_only
  expected_terminal_line: PASS Reimbayev six-vertex clean-room checks
limitations: the search is targeted rather than exhaustive; Makhnev's theorem is cited, not independently reproved; later preprint formulas are not promoted here
```

The strongest search consequence found in this audit is that every putative
Conway 99-graph contains an induced six-vertex graph `N3`: two disjoint
triangles joined by exactly two independent cross-edges. Each of the two
central diagonal nonedges of its four-cycle 2-percolates the entire graph. These are
derived consequences of cited results, not claims made verbatim by one source.

## The adjacent-neighborhood classification is prior art

Taylor's 2020 [blog post](https://maths.straylight.co.uk/archives/1330) reports
11 possibilities for the induced neighborhood of two adjacent vertices. This
is the same classification as the project's 10,395 matchings and 11 orbits:
after identifying the two exclusive 12-vertex sides by their cross matching,
the second side carries one of `11!!=10,395` perfect matchings. Quotienting by
`Aut(6K2)=C2 wreath S6` leaves the 11 partitions of six.

Taylor's [repository](https://github.com/GrayTaylor/conway99) has no detected
license. This project therefore cites and independently reproduces the result;
it does not copy Taylor's code or notebook prose. The classification itself is
not new.

## Six-vertex counts and a forced `N3`

Reimbayev's 2024 paper proves, with `n3` denoting induced copies of `N3`,

```text
p6 = (1/12) n k (k-2) (2k^2-21k+53) + n3,
3 n1 + n3 = 4,158                         for (n,k)=(99,14).
```

Thus for the target

```text
p6 = 209,286 + n3,
n3 = 0 (mod 3).
```

A clean-room enumeration of all 156 unlabeled six-vertex graphs reproduced the
paper's 14 relevant types and the final target substitution. It also found two
typographical defects that do not change the theorem: the prose says 12 types
where the figure and calculation use 14, and one displayed pentagon average
omits a factor of five while its final value uses the corrected factor.

Makhnev's 1988 Theorem 2 states that no target graph can satisfy condition
`(*)`: whenever two triangles have at least two cross-edges, they have exactly
three. When `lambda=1`, cross-edges between disjoint triangles form a matching,
so failure of `(*)` forces exactly two independent cross-edges. Intersecting
triangles cannot witness the failure. Therefore every putative graph contains
an induced `N3`, and

```text
n3 >= 3,
n3 = 0 (mod 3),
p6 >= 209,289.
```

The strict `+3` improvement is a project derivation combining the two cited
papers.

## A two-vertex percolating set

Label the forced `N3` triangles `{a0,a1,a2}` and `{b0,b1,b2}`, with cross-edges
`a0-b0` and `a1-b1`. Seed 2-bootstrap percolation with the nonedge
`{a0,b1}`. Its common neighbors `a1,b0` infect, followed by `a2,b2`, so the
closure contains all six vertices.

Ibrahim--LaFayette--McCall's closure classification implies that this closure
is an induced `srg(n',k',1,2)`: it is not `K3`, and their irregular cases
require `mu` zero or one. The parameter equation

```text
n' = (k'^2+2)/2
```

and integral spectral multiplicities leave only `(n',k')=(9,4)` for a proper
closure below the target. The unique graph is `K3 square K3`, whose triangles
are rows and columns; two disjoint rows or columns have three matching
cross-edges, never two. It cannot contain `N3`. The closure is therefore the
whole graph, and

```text
m(G,2) = 2.
```

The same argument works for each of the two central diagonal nonedges of any
induced `N3`. Fixing one
labeled occurrence is symmetry-safe because existence guarantees at least one
occurrence that can be globally relabeled. It does not assert that all `N3`
occurrences are equivalent under `Aut(G)`, and it assumes no nontrivial
automorphism of the completed graph.

## Other provenance corrections

Ducey et al.'s critical group concerns the Laplacian `14I-A`, not the adjacency
Smith form recorded in Wave 2. Brouwer--van Eijl's general parameter machinery
already implies the full adjacency ranks modulo 2, 3, and 7; those ranks should
not be presented as novel. No checked source was found for the residual
84-by-84 Jordan data or top determinantal divisor, but this targeted audit is
not a publication-level novelty certification.

The full bibliographic records are in [SOURCES.bib](../SOURCES.bib). Conway-99
remains unresolved in this project.
