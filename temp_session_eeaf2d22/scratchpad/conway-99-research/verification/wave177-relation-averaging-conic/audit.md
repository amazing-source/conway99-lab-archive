# Independent audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Conditional on the independently verified Wave 176 rank-11 endpoint model
and Wave 174 dual-distance bound, the Wave 177 averaging and conic claims
are correct.  No endpoint exclusion follows.

## Adjacent stars

For adjacent vertices, the true relation space on the 13 union columns has
dimension at least three.  Setting the common-triangle coefficient to zero
is one linear condition, so the punctured outer relation code `R_xy` on 12
coordinates has

```text
k=dim(R_xy)>=2.
```

If `c_x,c_y` are the two individual seven-star circuits, then
`s0=c_x-c_y` has common coefficient zero and is nonzero on every outer
coordinate.  Thus `S0=<s0>` is a one-dimensional subcode of `R_xy`, and
`R_xy` has full support.

In a full-support ternary `[12,k]` code, each coordinate is nonzero in
`2*3^(k-1)` codewords.  The total weight is therefore

```text
24*3^(k-1).
```

The three words of `S0` have total weight 24.  Removing them gives exact
outside average

```text
(24*3^(k-1)-24)/(3^k-3)=8.
```

This is valid for every `k>=2`.

The span `<c_x,c_y>` intersects the common-coordinate-zero subspace exactly
in `<c_x-c_y>`.  Hence every word outside `S0` is outside the full
individual-star circuit span and is genuinely cross-star.  The average
therefore supplies a true relation of weight at most eight.  Wave 174 gives
dual distance at least four, so the rigorous range is `4..8`.

The selected word avoids the common triangle.  Every outer column has inner
product one with the common centered column.  Pairing the relation with
that column gives

```text
sum coefficients=0 in F_3.
```

Consequently `sum c_T z_T=0` also gives
`sum c_T(z_T+w)=sum c_T v_T=0`; the relation lifts to the uncentered
factor columns.

## Nonadjacent stars

For nonadjacent vertices, the 14-column true relation code has dimension
`k>=3`.  The two disjoint individual-star circuits span a two-dimensional
subcode `S`, which activates every coordinate.

The total weight of the full relation code is

```text
28*3^(k-1).
```

Within `S`, two words have weight seven on the first star, two have weight
seven on the second, and four have weight 14 on both.  Its total weight is

```text
2*7+2*7+4*14=84.
```

The exact average outside the nine words of `S` is

```text
(28*3^(k-1)-84)/(3^k-9)=28/3.
```

All outside words are genuine cross-star relations.  Since their weights
are integers, at least one has weight at most nine; dual distance four
gives the range `4..9`.

## The type `4+2` conic

The Wave 176 rank-10 result proves equality of the coefficient and Gram
kernels for type `4+2`.  Reconstructing its actual 13-column Gram matrix,
the two weight-four kernel words are nonzero scalar multiples.  One has
support on the four vertices of the half-length-two cycle and coefficients

```text
(2,2 | 1,1).
```

Multiplying each supported centered column by its coefficient switches the
supported Gram matrix to

```text
J_4-I_4.
```

The switched vectors sum to zero.  This Gram has rank three; together with
the displayed relation, the vectors span a nondegenerate three-space.
Their four projective points are distinct and singular.  A nondegenerate
plane conic over `F_3` has exactly four points, so these are the complete
`Q(2,3)`.

For the rank-one self-adjoint maps `u tensor u`, application to each conic
vector gives

```text
sum_(u in Q(2,3)) u tensor u=-I.
```

The 13 projective points of `PG(2,3)` have total frame operator zero:
over all nonzero vectors, diagonal coordinate sums occur 18 times and
mixed coordinate sums vanish; dividing by the two representatives of each
projective point is legitimate in `F_3`.  The nine nonconic points
therefore contribute `+I`.

This is only a null control.  It shows that the local conic contribution can
be canceled in the complete plane frame, so the frame/divisibility equation
alone cannot reject type `4+2`.  It neither embeds those nine complement
points into the 231-column configuration nor constructs an endpoint graph.

## Indexed relations are not distinct relations

There are 693 original graph edges, and the theorem permits choosing at
least one short relation for each edge.  Nothing proves that two different
edges cannot choose the same global dual word.  Accordingly:

```text
edge-indexed choices: 693
distinct dual words forced: UNKNOWN
```

No count of 693 distinct relations is used or claimed.

## Integrity and execution

- all four frozen discovery inputs matched;
- all nine discovery package entries matched;
- the archived discovery result replay passed;
- all seven discovery tests passed;
- an independent checker reproduced both averages, the actual switched
  `4+2` Gram, and all three frame operators;
- all eight independent tests passed.

The only enumeration in the independent control is the 13 points of
`PG(2,3)`.  No graph, code, SAT, or isomorphism search is performed.

## Status wall

```text
adjacent true-relation support 4..8:      VERIFIED
nonadjacent true-relation support 4..9:   VERIFIED
adjacent coefficient-sum lift:            VERIFIED
type 4+2 complete-conic interpretation:   VERIFIED
693 indexed relations are distinct:       NOT PROVED
local conic excludes the endpoint:        NO
endpoint / strict n3 improvement:          UNKNOWN
Conway-99 / external novelty:              UNKNOWN
```

