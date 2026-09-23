# Independent audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Conditional on verified Waves 174, 177, and 178, the strengthened Wave 179
transversal bound is correct.  No endpoint contradiction follows.

## Extracting a nonedge cross circuit

For a nonedge pair, Wave 177 supplies a true relation outside the
two-dimensional span `S` of the two full-star circuits, with support at
most nine.  Among relations outside `S` contained in that support, choose
one with minimal support.

If a proper supported relation also lies outside `S`, minimality is
contradicted.  Hence any proper dependent sub-support can carry only a
relation in `S`.  Because the ambient support has size at most nine, it
cannot contain both full seven-stars; such a relation must be a scalar
multiple of one full-star circuit.  Subtract a scalar multiple chosen to
cancel one coordinate.  No new coordinate is introduced, the support
shrinks, and the result remains outside `S`, again contradicting
minimality.

Thus the chosen support is itself a circuit.  Since its relation is outside
`S`, it meets both stars.  Wave 174 gives size at least four, so every
nonedge has a cross circuit of size `4..9`.

## Exact two-transversals

A pair `{x,y}` realizes a circuit support exactly when every support
triangle contains exactly one of `x,y`, and both endpoints occur in at
least one support triangle.  The second condition is essential: it ensures
the circuit is genuinely cross for the realizing pair.

If all realizing pairs intersect pairwise, a family of two-subsets is
either a common-center star or the three edges of a triangle.  The triangle
case would require, in every support block,

```text
chi_a+chi_b=chi_a+chi_c=chi_b+chi_c=1,
```

which has no binary solution.  In the star case, a support triangle avoiding
the center must contain every leaf, so there are at most three realizing
pairs.

## Disjoint realizations

For disjoint realizations `X={x_0,x_1}` and `Y={y_0,y_1}`, each support
triangle contains one endpoint from each pair.  Triangle uniqueness gives
at most one block for each of the four patterns.  Dual distance four forces
exactly

```text
T_ij={x_i,y_j,t_ij}, i,j in {0,1}.
```

Both `X` and `Y` are nonedges: otherwise the two endpoints of the other
pair are distinct common neighbors of an edge.

Adjacent cells cannot share a third vertex because their triangles would
share an edge.  A diagonal repeat is also impossible.  For example, if
`t_00=t_11=p` and `t_01=q`, then the edge `x_0y_1` has common neighbors
`q` and `p`: `p` is adjacent to `x_0` through `T_00` and to `y_1` through
`T_11`.  Adjacent-cell uniqueness ensures `p!=q`.  The other diagonal is
symmetric.  Therefore all four `t_ij` are distinct.

A third realization meeting one of the four endpoints collapses to `X` or
`Y`, because its other endpoint would need to lie in two distinct triangles
already sharing the opposite endpoint.  A third realization avoiding all
four endpoints would need two vertices to cover the four distinct third
vertices, impossible.  Hence the disjoint case has exactly two
realizations.

Globally, a circuit support has at most three realizing pairs.

## Edge circuits have multiplicity one

Wave 178 proves an edge-selected circuit is balanced between its two outer
stars and has weight at least four.  It therefore contains at least two
blocks on each side.

If an edge circuit for `xy` were also realized by `{x,z}`, every one of the
at least two `y`-side triangles would contain both `y,z`, placing the edge
`yz` in two triangles and contradicting `lambda=1`.  The same applies to
any shared endpoint.  A disjoint second realization is impossible because
the disjoint-realization argument proves both realizing pairs are
nonedges, whereas `xy` is an edge.

Thus each of the 693 edge circuits realizes only its indexing pair, and no
nonedge-selected circuit can equal an edge circuit.

## Count and scalar factor

There are 693 edges and 4,158 nonedges.  The edge circuits give 693
distinct projective classes.  Nonedge assignments have multiplicity at
most three and are disjoint from those classes, so they give at least

```text
4158/3=1386
```

additional classes.  Therefore there are at least

```text
693+1386=2079
```

projective circuit classes of weights 4 through 9.

A circuit relation is unique up to scalar.  Over `F_3`, every projective
class has exactly two nonzero representatives of the same weight.  Hence

```text
B_4+B_5+B_6+B_7+B_8+B_9 >= 2*2079 = 4158.
```

The Wave 178 even balanced subcount `B_4+B_6+B_8>=1386` remains valid.

## Integrity and boundary

All discovery inputs and manifests matched, the discovery replay passed,
and both the independent and discovery test suites passed.  The independent
checker records only exact arithmetic and the finite binary consistency
conditions used above; it performs no graph or code search.

```text
projective circuit lower bound: 2079 VERIFIED conditionally
dual short-word lower bound:     4158 VERIFIED conditionally
endpoint contradiction:         NO
strict n3 improvement:           UNKNOWN
Conway-99 / external novelty:    UNKNOWN
```

