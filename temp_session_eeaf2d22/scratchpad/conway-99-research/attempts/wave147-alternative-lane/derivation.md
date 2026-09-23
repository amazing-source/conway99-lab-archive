# Exact two-root order-eight derivation

## 1. Why this is a new layer

Wave 45 uses two roots with order-four flags, so its two free sets have size
two and their products stop at order six.  Wave 47 uses three roots and two
free vertices, so its products stop at order seven.  The present family uses
two roots and three free vertices:

```text
2 roots + 3 free vertices = order-five flag,
2 roots + 3 + 3 free vertices = maximum union order eight.
```

It is therefore the smallest existing pair-root PSD lift that sees
order-eight overlap compatibility.

## 2. Finite Gram identity

Let `sigma` be an ordered edge or ordered nonedge.  For an embedding `theta`
of `sigma` in a graph `G`, and a rooted order-five flag `F`, define

```text
c_F(theta)
```

to be the number of unordered three-subsets outside the roots that induce
`F`.  Put `c(theta)=(c_F(theta))_F`.  Then

```text
M_sigma
  = sum_theta c(theta)c(theta)^T
```

is positive semidefinite because for every rational vector `z`,

```text
z^T M_sigma z
  = sum_theta (z^T c(theta))^2
  >= 0.
```

This is a finite exact identity.  It does not use a limiting density or
symmetry of `G`.

## 3. Unrooted expansion

Let `x_H` count induced copies of an unrooted graph class `H`.  For a class
of order `h`, enumerate every ordered root embedding and every ordered pair
of free triples whose union is the `h-2` vertices outside the roots.  The
free triples intersect in exactly

```text
8-h
```

vertices.  The resulting symmetric integer matrix is `C_H^sigma`, and

```text
M_sigma
 = sum_(h=5)^8 sum_(H in H_h) x_H C_H^sigma.        (1)
```

The exact class counts are

```text
|H_5|=21, |H_6|=62, |H_7|=208, |H_8|=916.
```

The two flag bases have sizes

```text
66 and 87.
```

The compressed artifact contains every matrix in (1): 1,207 class matrices
per family, 2,414 total, with 272,054 nonzero upper-triangular entries.

## 4. The `n3` coefficient

Let `N3` be two disjoint triangles joined by two independent matching
edges, and let `P6` be the triangular prism obtained by adding the third
matching edge.  Their exact order-six coefficient matrices are distinct.

For the ordered-edge family, flags with canonical masks `185` and `199`
give matrix entry `(29,32)`:

```text
coefficient of x_N3 = 4,
coefficient of x_P6 = 0.
```

For the ordered-nonedge family, masks `186` and `206` give entry `(36,42)`
with the same coefficients.  Since `x_N3=n3`, both entries contain the term

```text
4*n3.                                               (2)
```

Other order-five-through-eight class counts occur in the complete moment
entry, so (2) is not by itself an inequality.

The full `N3` coefficient matrices have exact rational ranks `13` and `10`;
their sums of all entries are `192` and `168`.  The prism matrices have
ranks `6` and `4` and sums `216` and `144`.

## 5. Complete order-eight class stream

Every locally admissible order-eight graph has a locally admissible
seven-vertex deletion.  Starting from each of the frozen 208 order-seven
classes, the checker adds a new vertex with all 128 possible neighborhoods.
It filters the adjacent-common-neighbor cap one and nonadjacent cap two.

To quotient isomorphism exactly, vertices are first partitioned by degree.
Every isomorphism preserves these cells, so enumerating all permutations
inside the degree cells is complete.  The resulting stream has 916 classes
and SHA-256

```text
c2cf3604abc76a537eca21f1a8ef041697ca40d8ad41668d25eb412b9cd67337.
```

For every order-seven class `H`, double-counting a copy of `H` together with
one outside vertex gives

```text
92*x_H = sum_K d(H,K)*x_K.                          (3)
```

The package emits all 208 equations (3), with 5,333 nonzero class terms.
Each order-eight column has deletion multiplicity eight, providing an
independent global consistency check.

## 6. Exact positive control

The `3 x 3` rook graph is `srg(9,4,1,2)`.  It has 36 ordered edge roots and
36 ordered nonedge roots; each root has `binom(7,3)=35` free triples.  Direct
enumeration gives both moment sums

```text
sum_(F,F') M_sigma(F,F') = 36*35^2 = 44100.
```

Both matrices are stored as the direct sum of 36 integer outer products.
The same checker counts zero induced `N3` copies and six triangular prisms,
as expected for the rook graph.

## 7. Exact upper-bound program

The intended general relaxation is:

```text
maximize n3
subject to
  verified order-five and order-six count identities,
  verified order-six-to-seven equations,
  order-seven-to-eight extension equations,
  x_H >= 0,
  M_edge >= 0,
  M_nonedge >= 0.
```

The ordinary deletion rows (3) are present.  The next implementation step is
to add all order-eight rows obtained by counting extensions adjacent to a
marked vertex and common neighbors of a marked pair; these encode the exact
`k=14`, `lambda=1`, and `mu=2` values more strongly than deletion alone.

If the rational relaxation has optimum `U<4158`, an exact certificate can
take the form

```text
U-n3
 = sum_i alpha_i*(exact linear identity i)
   + <Q_edge,M_edge>
   + <Q_nonedge,M_nonedge>
   + sum_H beta_H*x_H,
```

with rational PSD `Q_edge,Q_nonedge` and rational `beta_H>=0`.  Rational LDL
factorizations of the `Q` blocks make the certificate independently
replayable.

The likely technical obstacle is degeneracy: earlier moment systems sit on
large rank-deficient faces, so numerical duals may require facial reduction
before rationalization.  That is a certificate-engineering problem, not
permission to promote a floating status.

## 8. Boundary

The complete coefficient model is exact discovery work.  No SDP optimum,
rational dual, strict upper bound, endpoint exclusion, construction, or
external novelty result is claimed.  The rigorous global interval remains

```text
708 <= n3 <= 4158.
```

