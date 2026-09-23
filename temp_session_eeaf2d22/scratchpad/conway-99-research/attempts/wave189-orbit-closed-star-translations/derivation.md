# Orbit-closed star translations and the strict circuit bound

## 1. Frozen conditional setting

Assume the independently verified conditional endpoint

```text
n3=4158, P=0, rank_F3(D)=11.
```

Let

```text
C=4158
```

be the number of graph nonedges, and let `Q` count projective short
circuits that cross-realize at least one nonedge.

Use the verified Waves 176, 179--181, 186, and 188 facts:

1. every point-star is a seven-column circuit and every proper star subset
   is independent;
2. every nonedge is cross-realized by a circuit of weight at most nine;
3. a short circuit cross-realizes at most three nonedges;
4. exact-three circuits occur in canonical Wave 180 companion pairs;
5. exact-two circuits are the unique checkerboard conics on the 2,079
   canonical quadrilaterals; and
6. the Wave 186 type-two and type-three star translations extract the
   stated short cross circuits.

All counts below are of projective circuit classes.

## 2. Minimal cover and private labels

Choose an inclusion-minimal cover of the `C` nonedges by short circuit
label sets.  Let `n_i` count selected circuits with complete
cross-realization multiplicity `i`, and let `p_i` count their private
labels.  Then

```text
p_1=n_1,  p_2>=n_2,  p_3>=n_3,
p_2<=2*n_2,  p_3<=3*n_3.                         (1)
```

Put

```text
S=n_1+2*n_2+3*n_3.
```

Every nonprivate label is covered at least twice, so

```text
I:=2*n_1+2*n_2+3*n_3+p_2+p_3>=2*C.              (2)
```

Also `S>=C` because the selected label sets cover all `C` labels.

## 3. The missing type-one extraction lemma

Let a selected exact-one circuit `c` cross-realize its private nonedge
`xy`.  Write its support sizes in the two disjoint stars as

```text
a+b<=9,  1<=a,b<=6.                              (3)
```

The upper bound six follows because a circuit meeting both stars cannot
contain a full seven-star circuit as a proper dependent subset.

On the `x` side let the two nonzero coefficient multiplicities be `p,q`,
with `p+q=a`, and put `M_x=max(p,q)`.  Adding the nonzero scalar multiple
of the full `x`-star relation that cancels the majority sign gives a
relation of weight

```text
w_x=7-M_x+b.
```

Define `M_y` and `w_y=a+7-M_y` symmetrically.  If both translated weights
were at least ten, integrality would give

```text
M_x<=b-3,  M_y<=a-3.
```

Since `M_x>=a/2` and `M_y>=b/2`, adding the resulting inequalities gives
`a+b>=12`, contrary to (3).  Therefore

```text
min(w_x,w_y)<=9.                                 (4)
```

The chosen translated support has a proper subset on each star and omits
at least one coordinate of `c`.  Any circuit inside it must meet both
stars, has weight `4..9`, cross-realizes `xy`, and differs from `c`.
Privacy puts it outside the selected cover.

Thus every type-one private label supplies one outside extraction
assignment.

## 4. Companion pool and raw extraction assignments

Wave 180 supplies one distinct outside companion for each selected
type-three circuit.  Let `H_0` be this pool:

```text
|H_0|=n_3.                                        (5)
```

Keep the other forced circuits as raw extraction assignments:

```text
type 1: one per private label,
type 2: two distinct circuits per private label,
type 3: one leaf-translate circuit per private label.
```

Their total assignment incidence is

```text
A=n_1+2*p_2+p_3.                                 (6)
```

Every assigned circuit crosses its source private label and is outside the
cover.  No assigned circuit belongs to `H_0`.  Indeed, if an extraction
for private label `e` equalled the companion of a selected type-three
circuit `R`, then the selected mate of that companion would cover `e`.
Privacy forces `R` to be the source selected circuit.  This is impossible
for types one and two, and in type three the leaf extraction omits the
leaf block while its own companion contains it.

## 5. Close the extraction set under exact-three companionship

Start from the distinct raw extraction circuits and add the Wave 180 mate
of every exact-three member.  Call the resulting set `X`.

The added mate is outside both the selected cover and `H_0`.  It has the
same three labels as the raw circuit, including its source private label,
so equality with a selected circuit or a selected-type-three companion
would violate the same privacy argument as in Section 4.

Let

```text
r = number of multiplicity-at-most-two circuits in X,
h = number of complete exact-three companion pairs in X.
```

Then

```text
|X|=r+2*h.                                        (7)
```

A circuit in the first class receives at most two assignment incidences.
An exact-three pair receives at most one assignment for each of its three
labels.  The only possible obstruction is a type-two private label, which
has two raw extractions.  Relative to that label `xy`, their parent
supports have profiles

```text
6+2 and 2+6                                       (8)
```

in `S_x union S_y`.

An exact-three circuit crossing `xy` has a common center.  If centered at
`x`, its profile relative to `xy` is `(3 or 4)+1`; if centered at `y`, it
is `1+(3 or 4)`.  Hence an exact-three subcircuit of the `6+2` support must
be centered at `x`, while one in the `2+6` support must be centered at
`y`.  They cannot be the two members of one companion pair, because such
members have the same label triple and center.

Types one and three have only one raw assignment per source label.
Consequently

```text
A<=2*r+3*h<=2*(r+2*h)=2*|X|,
|X|>=A/2.                                         (9)
```

This is the orbit-closure gain.  Counting raw circuits alone loses the
second member of every exact-three orbit.

## 6. The exact `7/6` circuit certificate

The selected cover, `H_0`, and `X` are pairwise disjoint.  Therefore

```text
Q>=n_1+n_2+2*n_3+|X|.
```

Using (6) and (9),

```text
12*Q
 >=12*(n_1+n_2+2*n_3)+6*(n_1+2*p_2+p_3)
 =7*I
   +4*n_1
   +2*(p_2-n_2)
   +(3*n_3-p_3)
   +3*p_2.                                       (10)
```

Every term after `7I` is nonnegative by (1).  Equation (2) now gives

```text
12*Q>=14*C,
Q>=7*C/6=4851.                                   (11)
```

No graph, cover, code, SAT, configuration, or isomorphism search enters
this certificate.

## 7. Complete equality face of (11)

Suppose `Q=4851`.  Every slack in (9)--(10) must vanish.  In particular,

```text
n_1=n_2=p_2=0,
p_3=3*n_3,
I=2*C.
```

It follows that

```text
n_3=C/3=1386,
p_3=C=4158.                                      (12)
```

Thus the selected triple label sets partition all nonedges.  Each selected
member has the form

```text
(x,T),  T a graph triangle anticomplete to x,
```

and covers the three complement edges from `x` to `T`.

Equality in (9) also forces

```text
h=0, r=2079.
```

Every member of `X` is exact multiplicity two and receives two leaf
assignments.  Wave 181 therefore identifies `X` with all 2,079 canonical
checkerboard quadrilateral circuits.

### 7.1 Design and spectral null control

There are 231 graph triangles.  Every triangle has 60 anticomplete
vertices, so there are

```text
231*60=13860
```

candidate flags `(x,T)`.  A nonedge `xy` belongs to five candidate flags
centered at `x` and five centered at `y`, hence to ten candidates.

Let `H` be the nonedge-versus-flag incidence matrix.  It has row degree ten
and column degree three.  The equality face (12) asks for a zero-one vector
`b` satisfying

```text
H*b=1.                                           (13)
```

Equivalently, orient each complement edge toward the selected block center;
the outgoing neighborhood at every vertex is partitioned into graph
triangles.  The constant vector `b=(1/10)*1` is only a rational solution.

Two candidate flags share at most one complement edge.  Their conflict
graph is therefore 27-regular, and its adjacency matrix is

```text
H^T*H-3*I.
```

Its least eigenvalue is `-3`, because `H^T H` is positive semidefinite and
has a nontrivial kernel.  Hoffman's bound is exactly

```text
alpha<=13860*3/(27+3)=1386.                      (14)
```

Equality in (14) is precisely (13).  Thus the elementary spectral bound is
tight and cannot distinguish the rational null control from an integral
decomposition.

If `c_x` is the number of selected flags centered at `x`, and `r_T` is the
number of selected centers for triangle `T`, then the vertex-triangle
incidence matrix `N` gives the further necessary identities

```text
sum_x c_x=sum_T r_T=1386,
N*r=3*(28*1-c),
N*r=0 mod 3.                                     (15)
```

The uniform rational row `c_x=14,r_T=6` satisfies (15).  Hence (13)--(15)
are exact integer/design obstructions, not exclusions.

## 8. Strict exclusion of the `Q=4851` face

Fix a selected flag `(x,T)` from (12), with

```text
T={y,u,v}.
```

Wave 180 gives the weight-four relation

```text
c_4=z_T+2*sum_(S in A) z_S=0,  |A|=3,
```

and the full `y`-star relation is `s_y=sum_(R in S_y)z_R=0`.
For the private label `e=xy`, the leaf translation

```text
w_e=c_4+2*s_y
```

omits `T`, has profile `3+6`, weight nine, and has coefficient two on
every occupied coordinate.

Let `a,b` be the two common neighbors of the nonedge `xy`.  The two
`x`-star blocks through `a,b` lie in `A`: Wave 180's `t=3` profile puts
all six leaf/common-neighbor incidences in the three `j=2` cells.  They are
distinct, since putting `a,b` in one star triangle would give their edge
the two common neighbors `x,y`.  The two `y`-star blocks through `a,b` are
outer because `x` is anticomplete to `T`.

Thus the canonical four-block support for `e` lies inside `supp(w_e)`.
Under the equality face, its checkerboard relation `r_e` is a true circuit.
Scale it so that on its two coordinates on each side its coefficients are

```text
(1,2 | 2,1).
```

The two true relations

```text
w_e-r_e,  w_e-2*r_e                              (16)
```

each cancel one canonical coordinate on each side.  Both are nonzero,
have profile `2+5`, and have weight seven.  Their two sides are proper
star subsets, so any circuit contained in either support is cross-star and
cross-realizes `e`.

Such a circuit is not `r_e`, because (16) omits two coordinates of its
support.  It is not the selected weight-four circuit or its weight-five
companion, because both contain `T` while (16) omits `T`.

But under `Q=4851`, those are exactly the three short circuits that
cross-realize `e`: the selected triple member, its companion, and the
canonical exact-two circuit.  This contradiction excludes equality in
(11).  Therefore

```text
Q>=4852.                                          (17)
```

Adding the 693 verified edge-isolated projective circuits gives at least

```text
4852+693=5545
```

projective circuit classes of weights four through nine, hence

```text
B_4+B_5+B_6+B_7+B_8+B_9>=2*5545=11090.           (18)
```

Wave 188's `18018` bound on all short dual words remains numerically
stronger.  Equation (18) is specifically a circuit-support improvement.

## Boundary

The new result is conditional and `DERIVED_PENDING_INDEPENDENT_VERIFICATION`.
It excludes the Wave 186 arithmetic equality row and the sharper
`Q=4851` orbit-closed equality face, but it supplies no incompatible
upper bound for `Q`.

No rank-11 exclusion, endpoint exclusion, strict `n3` improvement, graph
construction, or Conway-99 resolution follows.  External novelty is
`UNKNOWN`.
