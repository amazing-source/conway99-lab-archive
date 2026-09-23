# Theta-control source notes

Access date: `2026-07-24` UTC. Query IDs: `T01-T07`.

## `K12`

The Nebe-Sloane
[K12 catalogue entry](https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/K12.html)
explicitly supplies:

```text
name: K12 (the Coxeter-Todd lattice)
dimension: 12
determinant: 729
minimum: 4
kissing number: 756
properties: INTEGRAL=1, MODULAR=3
Gram matrix: supplied
similarity matrix: supplied
```

It cites J. H. Conway and N. J. A. Sloane, *The Coxeter-Todd
lattice, the Mitchell group, and related sphere packings*, Math. Proc.
Cambridge Philos. Soc. 93 (1983), 421-440, DOI
[10.1017/S0305004100060746](https://doi.org/10.1017/S0305004100060746).

These sources establish catalogue identity and provenance.  They do not
by themselves establish the Wave 28 orthogonal sum, a 21-scaled-dual
minimum, or a discriminant-form comparison with a rooted rank-44
control.

## `Lambda(F)` / `KV32F`

The Nebe-Sloane
[LAMBDA(F) catalogue entry](https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/KV32F.html)
explicitly supplies:

```text
name: LAMBDA(F)
dimension: 32
Gram matrix: supplied
determinant: 1
minimum: 4
kissing number: 146880
property: Unimodular=1
```

It cites H. Koch and B. B. Venkov, *Uber ganzzahlige unimodulare
euklidische Gitter*, J. Reine Angew. Math. 398 (1989), 144-168, and a
1991 sequel.  The institutional record for H. Koch and G. Nebe,
[Extremal even unimodular lattices of rank 32 and related codes](https://archive.mpim-bonn.mpg.de/id/eprint/2004),
MPIM Preprint Series 1992 (35), supports the surrounding rank-32
extremal-even-unimodular context.

The catalogue field itself says `Unimodular=1`; it does not separately
print `Even=1`.  Evenness of the supplied Gram matrix is an arithmetic
check, and its use in the frozen control belongs to the exact and
independent verifiers.

## Exact comparison search

The frozen exact searches included:

```text
"K12" "Lambda(F)" lattice
"E6^6" "E8" theta lattice
"K12" "E6^6" discriminant form
```

No direct source was found for the precise comparison

```text
K12 orthogonal_sum Lambda(F)
versus
E6^6 orthogonal_sum E8
```

with the claimed same discriminant form/Weil representation and
different root coefficients.  The catalogue records also do not state
that comparison.  This non-hit does not establish novelty.

Classical theta-transformation and Sturm-bound results are standard
ingredients, but applying them requires their exact level, character,
and representation hypotheses.  In particular, the 3-modularity of
`K12` cannot be promoted into 21-modularity of the rank-44 sum merely
from `21L* subset L`.

## Attribution boundary

```text
catalogue names, matrices, dimensions, determinants, minima, and stated
properties: CITED

orthogonal-sum arithmetic, evenness where not explicitly catalogued,
scaled-dual minima, discriminant-form isometry, theta coefficients,
and hostile-control conclusions: exact verifier territory

exact comparison in prior literature: not located
novelty: UNKNOWN
```
