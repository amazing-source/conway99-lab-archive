# Independent audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Every claimed step survives independently under the frozen conditional
rank-11 endpoint assumptions.

## Multiplicity-three shape

Wave 179 proves that a circuit with three cross-realizing pairs cannot be
in the disjoint-pair case.  The three pairs are pairwise intersecting, and
the triangle alternative is impossible, so they have the form

```text
{x,y_0}, {x,y_1}, {x,y_2}.
```

A support triangle avoiding `x` must contain all three leaves and is
therefore the unique block `T={y_0,y_1,y_2}`.  Every other support block
contains `x` and avoids all leaves.  Because the full seven-star is already
dependent, the circuit cannot contain it as a proper subset.  Its relation
therefore expresses `z_T` in the nondegenerate star space `E_x`.  All three
labels are nonedges, so `x` is anticomplete to `T`.

## The `j` profile and projector

Each nonedge `xy_i` has two common neighbors, giving six incidences.  They
are six distinct vertices: a vertex adjacent to two leaves would be a
second common neighbor of their edge in addition to the third leaf,
contradicting `lambda=1`.

The seven star triangles partition these vertices into cells of capacity
two.  If `t` cells contain two, then

```text
(m_0,m_1,m_2)=(1+t,6-2t,t), 0<=t<=3.
```

At the endpoint the centered pairings are `h_i=j_i`.  Since `z_T` lies in
`E_x`, the star projector fixes it.  Singularity gives

```text
0=<z_T,P_x z_T>=-sum h_i^2=-(6-t) mod 3,
```

so only `t=0` or `t=3` remains.

For `t=0`, the six-one/one-zero pairing vector equals the pairing vector of
the star column at the zero position.  Both vectors lie in nondegenerate
`E_x`; equality of all star pairings forces equality of the vectors.  Since
the triangle blocks are distinct, this is a forbidden weight-two dual
relation.  Hence `t=3`.

## Companion circuits and conic

Let `A` be the three `j=2` star blocks and `B` the four `j=0` blocks.
Pairing with the spanning star and using nondegeneracy gives

```text
z_T+2*sum_A z_S=0,
z_T+sum_B z_S=0.
```

All eight columns lie in and span the six-space `E_x`, so the true
coefficient relation space has dimension two.  Its four projective
directions have weights `4,5,7,8`.  The weight-seven direction is the full
star; the weight-eight direction contains that star and is not a circuit.

The weight-four relation is a circuit by dual distance four.  The four
`B`-columns are independent, and the weight-five representation uses all
four nonzero coefficients, so the weight-five support is also a circuit.

After scaling the three `A` columns by two, the weight-four Gram is
`J_4-I_4`.  The vectors span a nondegenerate plane and are its four singular
points, the complete conic `Q(2,3)`.

Both supports exact-hit the same three pairs: `T` contains every leaf,
while every `A` or `B` block contains `x` and no leaf.  Wave 179's
multiplicity ceiling shows these are their complete label sets.  The center
and leaf triangle are recovered from those labels, so the companion is
canonical.  The two weights differ, making the pairing fixed-point-free;
applying it twice returns the original support.

## Minimal-cover amplification

Choose an inclusion-minimal family covering all 4,158 nonedges.  Let `N` be
its size and `a` the number of selected supports covering three labels.
All others cover at most two, so

```text
4158<=2N+a.
```

Every triple-serving selected support has a distinct companion with the
same labels.  Minimality prevents both companions from appearing in the
cover, because either would then be redundant.  The involution makes the
`a` outside companions distinct, hence the total number `Q` of
nonedge-realizing projective circuits satisfies `Q>=N+a`.  Therefore

```text
2Q>=2N+2a>=2N+a>=4158,
Q>=2079.
```

The 693 globally isolated edge circuits are disjoint from these classes,
giving at least `2772` projective circuits.  Each has two nonzero ternary
representatives:

```text
B_4+B_5+B_6+B_7+B_8+B_9>=5544.
```

## Integrity and boundary

- all six frozen inputs and all nine discovery entries matched;
- discovery replay and all six discovery tests passed;
- the independent checker reproduced the local relation directions,
  conic Gram, and cover arithmetic;
- all seven independent tests passed;
- all eight verification entries matched.

No graph or code construction search was performed.

```text
capacity-three companion theorem: VERIFIED conditionally
projective lower bound 2772:       VERIFIED conditionally
dual short-word lower bound 5544:  VERIFIED conditionally
endpoint contradiction:           NO
strict n3 improvement:             UNKNOWN
Conway-99 / external novelty:      UNKNOWN
```

