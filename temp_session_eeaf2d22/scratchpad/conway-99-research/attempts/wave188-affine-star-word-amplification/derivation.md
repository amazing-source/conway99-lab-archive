# Affine star-word amplification

## 1. Frozen conditional setting

Assume

```text
n3=4158, P=0, rank_F3(D)=11.
```

Retain the independently verified inputs from Waves 174, 179--181, and
186:

1. the centered ternary dual distance is at least four;
2. every nonedge is cross-realized by a circuit word of weight at most
   nine;
3. a support of weight at most nine cross-realizes at most three vertex
   pairs;
4. multiplicity-two circuit words are the canonical checkerboard conics;
5. multiplicity-three circuit words are the conic/complement pair; and
6. the 693 balanced edge-circuit words are distinct and cross-realize no
   nonedge.

Every object counted below is a projective nonzero dual **word**, not
necessarily a matroid circuit.

## 2. The affine `3 by 3` two-star orbit

Let `xy` be a nonedge and let `c` be a cross circuit word supported in the
two disjoint seven-stars `S_x,S_y`. Let `s_x,s_y` be their full-star
relations.

On the `x`-star, count the coefficients `0,1,2` of `c` as

```text
(a_0,a_1,a_2),  a_0+a_1+a_2=7,
```

and define `(b_0,b_1,b_2)` similarly on `S_y`. The nine words

```text
c+alpha*s_x+beta*s_y,  alpha,beta in F_3,        (1)
```

have weights

```text
14-a_i-b_j,  0<=i,j<=2.                          (2)
```

Because `c` is a cross circuit, `a_0,b_0>=1`: otherwise its support would
contain a full seven-star circuit as a proper dependent subset.

The class of `c` modulo `span(s_x,s_y)` is nonzero. Hence no word in (1)
vanishes and no two are projectively equal: a scalar equality, reduced
modulo the star span, first forces the scalar to be one and then forces the
two star coefficients to agree.

Dual distance four makes every weight in (2) at least four. Since each
coefficient-frequency triple sums to seven and one cell has weight at most
nine, at least three cells have weight at most nine. An elementary proof is
obtained by taking `A=max a_i`.

- If `A>=5`, its row already has three cells with `a_i+b_j>=5`.
- If `A=4`, either at least two `b_j` are positive and a second entry
  `a_i>=2` pairs with `max b_j>=3`, or `b` has one nonzero entry and its
  column has three cells.
- If `A=3`, all `a_i` are positive. If `max b_j>=4`, its column has three
  cells. Otherwise both triples are permutations of `(3,2,2)`; the
  `(3,3)` cell and the four `(3,2)` or `(2,3)` cells give five short cells.

Thus every selected short cross circuit has at least two other projectively
distinct words of weights four through nine in its affine orbit.

## 3. Cross-realization capacity of the alternatives

Consider any nonzero word of weight at most nine supported in `S_x union
S_y` and cross-realizing `xy`.

If it has at least two support blocks on each side, then:

- a second realizing pair sharing `x` would force at least two distinct
  `y`-star triangles to contain the same edge `yz`;
- the case sharing `y` is symmetric; and
- a disjoint second realizing pair forces exactly the four endpoint-pair
  patterns and hence support size four, as in Wave 179.

Consequently such a support cross-realizes exactly one pair when its weight
is greater than four, and at most two pairs when its weight is four. This is
a statement about the support of the word; no circuit extraction is used.

It remains to understand a word having a one-block side. Suppose that side
is the block

```text
T={y,u,v} in S_y.
```

Its relation expresses `z_T in E_x`. Since `xy` is a nonedge, `x` is
adjacent to at most one of `u,v`: adjacency to both would give the edge
`uv` two common neighbors, `x` and `y`.

If `x` is adjacent to exactly one point of `T`, the seven pairings of
`z_T` with the `x`-star have profile

```text
five 1s and two 2s.
```

The two extra common neighbors occupy different outer star blocks; equality
would form a forbidden triangular prism. Projector singularity would then
give

```text
0=<z_T,P_x z_T>=-(5+2)=-7 != 0 in F_3,
```

a contradiction.

Therefore `x` is anticomplete to `T`. The verified Wave-180 projector
classification now applies: the local relation space has precisely three
projective cross words, of weights

```text
4, 5, 8,
```

and all three cross-realize the same triple

```text
{x,y}, {x,u}, {x,v}.                              (3)
```

## 4. A minimum circuit cover and private labels

Choose an inclusion-minimal cover of the

```text
C=4158
```

nonedges by short circuit supports. Let `n_i` count selected circuits whose
complete cross-realization set has size `i`, and let `p_i` count private
labels on selected type-`i` circuits.

Every selected circuit has a private label, so

```text
p_1=n_1,  p_2>=n_2,  p_3>=n_3.                   (4)
```

The total selected label incidence is

```text
S=n_1+2*n_2+3*n_3.
```

If `P_priv=n_1+p_2+p_3` labels are covered once, all other labels are
covered at least twice. Therefore

```text
P_priv>=2C-S,
2*n_1+2*n_2+3*n_3+p_2+p_3>=2C.                  (5)
```

Let `O` be the number of nonedge-realizing projective dual words of weights
four through nine outside the selected circuit words.

## 5. Outside words forced by each selected type

### Type one

Fix the private label of a selected type-one circuit. Its affine orbit has
at least two other short words.

If no such alternative has a one-block side, Section 3 gives reuse capacity
at most two, so two assignments per private label force at least `n_1`
outside words globally.

If an alternative has a one-block side, Section 3 supplies all three local
words in (3). The selected type-one circuit is not one of them, and each
outside word can be reused by at most the three labels in (3). Again the
global contribution is at least `n_1`.

The two cases are disjoint by their exact cross-realization multiplicity.

### Type two

A selected type-two checkerboard conic has coefficient profile

```text
(5,1,1) | (5,1,1)
```

relative to either of its two nonedge labels. For each private label,
adding either nonzero scalar multiple of either endpoint-star relation gives
four projectively distinct words, each of profile

```text
6+2
```

and weight eight. Section 3 makes every one an exact-singleton word for
that private label. Hence these contribute `4*p_2` distinct outside words.

### Type three

For every selected triple-serving circuit, the local two-dimensional
relation space has three projective cross words of weights `4,5,8`.
Whichever circuit word is selected, the other two are outside and are
distinct for different triple label sets. This contributes `2*n_3`.

For each private label, translating the weight-four member by the private
leaf star gives the Wave-186 profile

```text
3+6
```

of weight nine. Section 3 makes it an exact-singleton word. These contribute
another `p_3` distinct outside words.

The type-one alternatives, type-two singleton words, type-three singleton
words, and type-three base words cannot collide: a collision would either
change the exact cross-realization multiplicity or make one selected
circuit cover another selected circuit's private label.

Consequently

```text
O>=n_1+4*p_2+p_3+2*n_3.                          (6)
```

## 6. Exact factor-two amplification

Let `M` count all nonedge-realizing projective dual words of weights four
through nine. The selected and outside families are disjoint, so (6) gives

```text
M >= n_1+n_2+n_3+O
  >= 2*n_1+n_2+3*n_3+4*p_2+p_3.                  (7)
```

Subtract the left side of (5) from the last expression in (7):

```text
3*p_2-n_2>=2*n_2>=0,                             (8)
```

using `p_2>=n_2`. Therefore

```text
M>=2C=8316.                                       (9)
```

The 693 verified balanced edge-circuit words cross-realize no nonedge and
are distinct from this family. Thus the total number of projective dual
words of weights four through nine is at least

```text
8316+693=9009.                                    (10)
```

Each projective ternary word has two nonzero scalar representatives:

```text
B_4+B_5+B_6+B_7+B_8+B_9>=2*9009=18018.           (11)
```

## Boundary

Equation (11) is a stronger necessary condition for the conditional
rank-11 endpoint. It does not conflict with any currently classified
complete weight enumerator.

No rank-11 exclusion, endpoint exclusion, strict `n3` improvement, graph
construction, or Conway-99 resolution follows.
