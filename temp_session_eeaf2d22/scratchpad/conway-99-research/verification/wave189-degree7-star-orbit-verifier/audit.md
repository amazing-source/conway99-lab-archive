# Independent Wave 189 audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Two separate conclusions survive clean-room verification:

1. `VERIFIED_RELAXATION_FEASIBILITY`: the displayed rational degree-seven
   complete-enumerator control satisfies every frozen linear, local, ordinary,
   complete, and typed-moment constraint tested here.
2. `VERIFIED_CONDITIONAL_THEOREM`: under the frozen prism-free rank-11 endpoint
   assumptions, the number `Q` of projective short circuits cross-realizing a
   nonedge satisfies `Q>=4852`.

The first conclusion is not code existence. The second does not exclude the
endpoint. Neither resolves Conway-99.

## Integrity and separation

The degree-seven source manifest has SHA-256
`dce4157a05fc20f9b3965ec9830a08f893eeefacdb347b084af13807fa417c90`;
all ten entries match. The primary orbit source manifest has SHA-256
`d62ce505ebbaa7bd3799c05a6f0ac50ed920fdd519044e287bada2cb582e39d2`;
all nine entries match. Sixteen direct verifier inputs also match.

The verifier imported and executed neither discovery checker. It reconstructed
the result first and froze independent result SHA-256
`d2933fbe3836431f17971ff10807d0a968a8ef85376ea11dce7fda81740e8bdf`.
Only afterward were the source checkers replayed for comparison.

## A. Exact rational degree-seven control

### Masses and one-star polygon

All 16 typed projective scalar-pair masses are strictly positive. Their exact
type totals are

```text
singular:   29524
norm plus:  29646
norm minus: 29403
total:      88573=(3^11-1)/2.
```

The singular `(36,162)` cell has mass 231.

The independently derived local patterns are exactly

```text
(0,0), (0,3), (0,6), (1,1), (1,4), (2,2),
(2,5), (3,0), (3,3), (4,1), (5,2), (6,0).
```

Their convex hull has vertices

```text
(0,0), (6,0), (5,2), (2,5), (0,6)
```

and facets `r+s<=7`, `2r+s<=12`, `r+2s<=12`. Every oriented witness cell
satisfies the scaled facets and receives an explicit nonnegative rational
barycentric lift with exact total and first moments.

### Complete and ordinary MacWilliams rows

An independent exact expansion in
`Z[omega]/(omega^2+omega+1)` gives zero complete rows in degrees one through
three, the degree-four shape

```text
(B04,B13,B22,B31,B40)
=(0,0,1133506211803506205652542142416870583
     /1288254800187180330519157577595,0,0),
```

and nonnegative rows in degrees five through seven. The degree-seven
endpoints are exactly

```text
B70=B07=99.
```

The six star-pair rows also satisfy their geometric lower bounds:

```text
B12,1>=693, B1,12>=693, B6,6>=1386,
B14,0>=4158, B0,14>=4158, B7,7>=8316.
```

These live in total degrees 12--14 and do not create another total-degree
seven constraint.

All 232 ordinary ternary rows satisfy `B_j>=A_j>=0`, with
`B1=B2=B3=0`. The exact short sum is

```text
B4+...+B9
=303955951136016513013761953327276372487328891
 /2147091333645300550865262629325
>18018.
```

### Typed moments and Gram census

Direct enumeration of only the five canonical complements of

```text
Q(x)=x0^2+x1*y1+...+x5*y5
```

reproduces the class sizes `(29524,29646,29403)` and the required
singular/norm-plus/norm-minus complement counts. The witness has the frozen
typed factorial moments through order two, and its rational five-class triple
census is nonnegative, totals `binom(231,3)=2027795`, satisfies both
orthogonal-incidence equations, and reproduces all three exact order-three
moments.

The census is nonintegral. This is a feasible rational moment point, not a
231-point configuration, ternary code, graph, or endpoint construction.

## B. Conditional analytic circuit theorem

### Singleton translation and pool separation

For a type-one circuit with side sizes `a,b`, coefficient majority
translation gives

```text
w_x=7-M_x+b,  w_y=a+7-M_y.
```

If both were at least ten, `M_x>=a/2` and `M_y>=b/2` would force
`a+b>=12`, contradicting `a+b<=9`. A short translated relation therefore
exists. Both sides are proper star subsets, so a minimal subcircuit crosses
the private label and privacy puts it outside the selected cover.

The selected cover, selected type-three companions, and orbit-closed
extraction pool are pairwise disjoint. The delicate closure step is valid:
an added exact-three mate cannot be selected or a selected companion without
making the raw extraction respectively a selected companion or a selected
circuit.

### Center orientation and scalar identity

Let

```text
A=n1+2*p2+p3,
|X|=r+2*h.
```

Low-multiplicity circuits receive at most two assignments. For a type-two
private label, the two extraction supports have profiles `6+2` and `2+6`.
Any exact-three circuit in the first is centered at the first endpoint; one
in the second is centered at the other. They cannot be companion mates,
because mates share their center. Hence

```text
A<=2*r+3*h,
2*|X|>=A.
```

With

```text
I=2*n1+2*n2+3*n3+p2+p3>=2*C,
```

the exact coefficient identity is

```text
12Q
>=7I+4*n1+2*(p2-n2)+(3*n3-p3)+3*p2
>=14*C.
```

For `C=4158`, this gives `Q>=4851`.

### Equality saturation and weight-seven exclusion

Equality forces

```text
n1=n2=p2=0, n3=1386, p3=4158, r=2079, h=0.
```

The selected triples partition all nonedges. Every extraction-pool circuit
has exact multiplicity two and exactly two assignments, so the pool is all
2,079 canonical checkerboard conics.

For a private label `e`, its `3+6` leaf word has all occupied coefficients
two and contains the canonical conic

```text
r_e=(1,2 | 2,1).
```

Both `w_e-r_e` and `w_e-2r_e` are true weight-seven relations with profile
`2+5`. A circuit in either residual crosses `e`. It is not the conic because
the residual omits conic coordinates; it is not the selected owner or its
companion because both contain the omitted leaf triangle; and equality
saturation makes the conic the unique extraction-pool circuit serving `e`.
Thus it is a fourth circuit through `e`, contradicting `Q=4851`.

Therefore

```text
Q>=4852.
```

Adding 693 edge-isolated projective circuits gives 5,545 projective short
circuit classes and the circuit-specific scalar consequence `B4+...+B9>=11090`.
Wave 188's `18018` all-short-word bound remains numerically stronger because
it also counts nonminimal words.

## Hoffman/design null boundary

There are `231*60=13860` candidate anticomplete triangle flags. Their
nonedge-incidence matrix has row degree 10 and column degree 3. Since two
flags share at most one nonedge, the conflict graph is 27-regular with

```text
A=H^T H-3I.
```

Positive semidefiniteness and the nontrivial kernel of the
`4158 x 13860` matrix give least eigenvalue exactly `-3`. Hoffman's bound is

```text
alpha<=13860*3/(27+3)=1386.
```

It is tight exactly on a hypothetical integral flag partition `Hb=1`.
The uniform rational row `b=1/10`, center count 14, and triangle replication
6 satisfies the linear design identities. Consequently this spectral row is
a sharp null boundary, not evidence that an integral partition exists.

## Reproducibility

After the independent result was frozen:

```text
independent verifier replay: PASS
independent tests:           10/10 PASS
degree-seven source tests:    6/6 PASS
orbit source tests:           8/8 PASS
```

No graph, cover, code, SAT, configuration, or isomorphism search was used.

## Boundary

```text
rational degree-seven relaxation: feasible
linear code / point set / graph:   not constructed
conditional circuit theorem:      Q>=4852 verified
rank 11 excluded:                  no
endpoint excluded:                 no
Conway-99 resolved:                no
external novelty:                  UNKNOWN
```
