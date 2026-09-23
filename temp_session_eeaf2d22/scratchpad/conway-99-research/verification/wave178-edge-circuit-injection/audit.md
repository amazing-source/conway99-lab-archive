# Independent audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Conditional on the independently verified Waves 174, 176, and 177, the
edge-to-circuit injection and balanced-profile consequence are correct.
The result does not exclude the endpoint.

## Minimal subrelations meet both stars

For an edge `xy`, Wave 177 supplies a true relation of weight `4..8` on the
12 outer columns, avoiding the common triangle.  Choose an
inclusion-minimal dependent subset of its support.

Each complete seven-column point-star has exactly its full-support circuit.
Consequently every six-column outer star is independent.  The minimal
dependent subset cannot lie in either outer star alone, so it meets both.
Wave 174 dual distance and containment in the original support give circuit
size `4..8`.

## Support multiplicity

Suppose the same circuit support serves two edges.

If the edges share endpoint `x`, write them `xy,xz`.  Because the circuit
meets the `y` side for `xy`, it contains a triangle `T` through `y` but not
`x`.  Relative to `xz`, that triangle must lie on the `z` side, hence
contains `z`.  Thus `yz` is an edge whose common neighbors include both the
third point of `T` and `x`.  They are distinct because `x` is not in `T`,
contradicting `lambda=1`.

If the edges `x_0x_1,y_0y_1` are endpoint-disjoint, every support triangle
contains exactly one `x_i` and one `y_j`.  There are four endpoint-pair
patterns.  Each fixed pair occurs in at most one triangle: if adjacent, its
unique common neighbor follows from `lambda=1`; if nonadjacent, it occurs in
none.  Hence the support has size at most four.  Dual distance forces size
four and all four patterns.  Then `y_0,y_1` are two distinct common
neighbors of the edge `x_0x_1`, again contradicting `lambda=1`.

Therefore a circuit support serves at most one edge.

## Projective classes and the factor two

A matroid circuit has a one-dimensional coefficient-relation space:
otherwise a linear combination of two independent relations could cancel
one supported coordinate and produce a smaller dependent set.  Thus its
support determines one projective dual-word class.

Choosing one minimal circuit for each of the 693 edges is injective on
projective classes.  Each ternary projective class contains exactly the two
nonzero scalar representatives `c` and `2c`, of equal weight.  Therefore

```text
B_4+B_6+B_8 >= 2*693 = 1386.
```

## Independent local-kernel reconstruction

For a cycle biadjacency matrix `A`, a common-coordinate-zero Gram-kernel
word has outer coefficients

```text
(x,y)=(Ay,y),  (I-A^T A)y=0.
```

On a half-length-`m` cycle, the latter is the periodic second-difference
equation.  Its solutions are `y_i=c+d*i`, with `d*m=0` in `F_3`.
Enumerating only these derived solution spaces gives:

```text
type 6:
  6 words  (8;4,4;4,4)

type 4+2:
  2 words  (4;2,2;2,2)
  2 words  (8;4,4;4,4)

type 3+3:
  12 words (4;2,2;2,2)
  4 words  (6;3,3;3,3)
  36 words (8;4,4;4,4)

type 2+2+2:
  6 words  (4;2,2;2,2)
  12 words (8;4,4;4,4)
```

The profile records total weight, left/right support, and counts of
coefficients `1/2`.  Thus every eligible word has weight 4, 6, or 8, equal
support on both stars, and equal numbers of `1` and `2`.

For the rank-8 and rank-9 local types the Gram kernel can strictly exceed
the true coefficient kernel.  This causes no promotion error: the
classification is used only as a superset, so every true short relation
must have one of the displayed profiles; the displayed Gram-word counts are
not claimed as counts of true relations.

## Integrity and execution

- all six frozen discovery inputs matched;
- all nine discovery package entries matched;
- discovery replay and all five discovery tests passed;
- the independent recurrence checker reproduced every profile;
- all six independent tests passed;
- all eight verification-package manifest entries matched.

No graph or code construction is enumerated.

## Status wall

```text
693 distinct projective short circuits: VERIFIED conditionally
B_4+B_6+B_8 >= 1386:                  VERIFIED conditionally
balanced 4/6/8 local profiles:         VERIFIED
endpoint contradiction:               NO
strict n3 improvement:                 UNKNOWN
Conway-99 / external novelty:          UNKNOWN
```

