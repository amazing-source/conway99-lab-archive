# Star-translation amplification of the nonedge cover

## 1. Frozen conditional setting

Assume the independently verified conditional endpoint model

```text
n3=4158, P=0, rank_F3(D)=11.
```

Retain these verified facts.

1. Each point-star has seven columns, exactly one relation, and that relation
   has full support.
2. Every nonedge is cross-realized by a circuit of weight at most nine.
3. A short circuit cross-realizes at most three vertex pairs.
4. A circuit cross-realizing exactly three nonedges is one member of the
   Wave 180 conic/complement pair.
5. A circuit cross-realizing exactly two nonedges is the checkerboard conic
   on their unique canonical induced quadrilateral.
6. The 693 edge circuits are distinct and cross-realize no nonedge.

All circuits below are projective circuit classes.

## 2. Two forced translates for multiplicity two

Let a selected circuit cross-realize exactly two nonedges.  Wave 181 puts it
on two disjoint seven-stars `S_x,S_y`, with side profile `2+2`.  Normalize
its relation as

```text
c=(1,-1,0^5 | -1,1,0^5).                         (1)
```

Let `s_x,s_y` be the full-star relations.  Add a scalar multiple of `s_x`
that cancels either one of the two nonzero `x`-coordinates in (1).  The
result is a true relation with side profile

```text
6+2
```

and weight eight.  A circuit inside its support cannot be one-sided, because
each side is a proper star subset.  It therefore cross-realizes `xy`.  It
cannot be the original conic because one conic coordinate was cancelled.

Doing the same at `y` gives a relation of profile `2+6`.  The two translated
supports intersect in only two coordinates.  Since dual distance is at least
four, circuits chosen inside them cannot coincide.

Thus a multiplicity-two conic and one of its labels force two distinct other
short circuits cross-realizing that label.                         (2)

## 3. Two forced circuits for multiplicity three

Let a selected circuit cross-realize the three nonedges

```text
{x,y_0},{x,y_1},{x,y_2}.
```

Wave 180 writes the pair of true circuit relations as

```text
c_4=z_T+2*sum_(S in A) z_S=0, |A|=3,
c_5=z_T+  sum_(S in B) z_S=0, |B|=4,              (3)
```

where `T={y_0,y_1,y_2}` and `A,B` partition the seven-star at `x`.
Whichever member is selected, its companion is a distinct circuit with the
same three labels.  Inclusion-minimality of a cover prevents both from being
selected.

Now fix one label `{x,y_i}`.  Add twice the full `y_i`-star relation to
`c_4`.  The `T` coordinate cancels, leaving a true relation supported on

```text
three A-blocks at x and six outer blocks at y_i,
```

of weight nine.  A circuit inside is cross-star and short.  It differs from
both members of (3): its support omits `T`, and it uses the `A` side rather
than the `B` side of the weight-five companion.

Thus a multiplicity-three circuit and any one of its labels force two
distinct other short circuits cross-realizing that label: its companion and
the private-leaf translate.                                      (4)

## 4. Private labels and outside circuits

Choose an inclusion-minimal family of short circuit supports covering all

```text
C=4158
```

nonedges.  Let `n_i` be the number of selected supports whose complete
cross-realization set has size `i`, for `i=1,2,3`, and put

```text
N=n_1+n_2+n_3,
S=n_1+2*n_2+3*n_3.                                (5)
```

Every selected set has a private label.  Let `P_priv` be the total number of
labels covered exactly once.  Every other label is counted at least twice in
`S`, so

```text
S>=P_priv+2(C-P_priv)=2C-P_priv,
P_priv>=2C-S.                                     (6)
```

Every size-one selected set contributes its sole label to `P_priv`.  Hence the
number `p` of private labels belonging to size-two or size-three selected
sets satisfies

```text
p=P_priv-n_1
 >=2C-2*n_1-2*n_2-3*n_3.                         (7)
```

Let `O` be the number of nonedge-realizing short circuits outside the
selected cover.  For each of the `p` private labels, Sections 2--3 give two
distinct outside circuits.  The same outside circuit can be assigned to at
most three distinct private labels, by the verified cross-realization
ceiling.  Therefore

```text
3O>=2p.                                           (8)
```

Wave 180's companions for the `n_3` selected triple-serving circuits are
distinct from one another and lie outside the minimal cover, so also

```text
O>=n_3.                                           (9)
```

Assignments in (8) may reuse a triple companion for several of its labels;
the capacity-three denominator explicitly allows that overlap.

## 5. Exact `8/9` bound

From twice (8) and (7),

```text
6O+8*n_1+8*n_2+12*n_3>=8C.                       (10)
```

From (9),

```text
3O+n_1+n_2-3*n_3>=0.                             (11)
```

Adding (10)--(11),

```text
9(N+O)>=8C.
```

The cover and its outside circuits are disjoint subsets of the `Q`
nonedge-realizing projective circuits.  Since `C=4158` and
`8*4158/9=3696`,

```text
Q>=N+O>=3696.                                     (12)
```

The scalar arithmetic is sharp at the level of these inequalities, for
example at

```text
n_1=n_2=0, n_3=1848, P_priv=2772, O=1848.
```

This is only a hostile arithmetic control, not a circuit cover.

## 6. Enumerator consequence

The 693 verified edge-isolated projective circuits are disjoint from the
family counted by `Q`.  Hence

```text
projective circuits of weights 4..9
 >=3696+693
 =4389.
```

Each projective ternary circuit has two nonzero scalar representatives:

```text
B_4+B_5+B_6+B_7+B_8+B_9>=8778.                   (13)
```

In particular `Q=2079` is impossible, so the Wave 181 equality face and its
Wave 182--185 root-gluing continuation are closed.

## Boundary

Equation (13) is a stronger necessary condition for the conditional rank-11
endpoint.  There is still no incompatible complete-weight upper bound.

No strict `n3` improvement, rank-11 exclusion, graph construction, or
Conway-99 resolution follows.
