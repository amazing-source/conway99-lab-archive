# Wave 186 proof A: nonedge relation dimension and circuit elimination

## Status

`DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

The proposed dimension-four exclusion is correct, but it is not the
strongest conclusion.  On the Wave 181 equality face, the
three-dimensional code

```text
T=<two star circuits, canonical conic>
```

already forces noncanonical short circuits by ordinary circuit
elimination.  Amplifying those eliminations over an inclusion-minimal
nonedge cover gives

```text
Q>=3696,
projective circuits of weights 4..9 >=4389,
B_4+B_5+B_6+B_7+B_8+B_9>=8778.                   (1)
```

This makes the requested equality-case conclusion
`dim(R_xy)=3` vacuous rather than a live finite-geometric branch.  The
formal orthogonal-space continuation is nevertheless recorded below.  A
trace-field family shows that ordinary partial-spread bounds have enormous
slack and give no additional obstruction.

```yaml
role: proof_a
date_utc: 2026-07-29T00:51:33Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Under the conditional rank-11 endpoint: exact weight enumeration of the
  nonedge three-code T, validation of the proposed dimension-at-least-four
  averaging lemma, a circuit-elimination contradiction to the Wave181
  equality premise Q=2079, and private-label amplification of the global
  nonedge circuit bound from 2079 to 3696. Formal partial-spread
  consequences are separated as a null continuation.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  attempts/wave174-no-weight3-dual/package-manifest.sha256: 4244d369d4cfdd2819a4d377b8328b425d110be2d09c45f3418262cef0bee276
  verification/wave174-no-weight3-dual/package-manifest.sha256: ac34c8a3b045bec70e3a2080cb4365c0ea43cc732b313ecb3cec355a28f23450
  attempts/wave177-relation-averaging-conic/package-manifest.sha256: 9caafa2d424082e52b161bd5850e062ab742bf27eaa9239bea8a184a91c6e834
  verification/wave177-relation-averaging-conic/package-manifest.sha256: 12d07acaee78752692c1537351ba318b4ecaca53d590391b8de54c90c05aca4b
  attempts/wave179-global-transversal-circuits/package-manifest.sha256: cbcd4dc222e1b43f57039573e9d9503141855193c7c58f0ff4c432a8f0d47195
  verification/wave179-global-transversal-circuits/package-manifest.sha256: 0f8dca5c3230861f22f15d7df74d6716623890de2080c5fa5dea29469ce4124c
  attempts/wave180-capacity3-companion/package-manifest.sha256: bb828dc9fc0c2aa7485379f3045b3586f4fdc3d930eb8dd36e59d3c19d7e6d54
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  attempts/wave181-c4-conic-equality/package-manifest.sha256: 8ea0993ecdd2abe3cb82cd4ac05273c7b7992f6739ef99121b9ae3c04fce7be2
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
  attempts/wave182-a6-root-gluing/package-manifest.sha256: 4185d17a5ada56656b5066952413a20ba2f6c15a01ee7d2c6a1d6b5db94b2fac
  verification/wave182-a6-root-gluing-verifier/package-manifest.sha256: 7a4e4074a634996bfe61c66fd5c077dbff14cba510cdff13fda656426ca211ea
  attempts/wave39-cross-base-rank/package-manifest.sha256: 35c6369560e72cc09df9e2d53d359a7a574c44c6be971c3cb3b6e7fe30924368
  verification/2026-07-27-wave39-integration-audit.md: 9d22f5ae2ed1f1ec756975508030f2b6b440580d1215604d4f353256bae1483b
method: >-
  Exact ternary weight averaging, support-minimal circuit elimination,
  private-label charging in an inclusion-minimal set cover, the
  unique-dependence property of each seven-column simplex star,
  dimension-intersection algebra, and an analytic finite-field trace
  construction in a split ten-dimensional orthogonal space. No graph,
  code, SAT, configuration, or isomorphism search.
command: >-
  PowerShell exact 3^3 coefficient check:
  $vals=@(); foreach($a in 0..2){foreach($b in 0..2){foreach($d in 0..2){
  $x0=@($d,((3-$d)%3),0,0,0,0,0); $y0=@(((3-$d)%3),$d,0,0,0,0,0);
  $x=@($x0|%{($_+$a)%3}); $y=@($y0|%{($_+$b)%3});
  $vals+=@(($x+$y|?{$_ -ne 0}).Count)}}};
  $vals|group|sort {[int]$_.Name}; ($vals|measure -Sum).Sum.
  The cover amplification is the displayed exact integer inequality
  9*Q>=8*4158; no construction enumeration is used.
outputs:
  - agents/2026-07-29-wave186-nonedge-relation-dimension-proof-a.md
limitations:
  - Independent verification is required before promotion.
  - The strict circuit lower bound does not by itself exclude rank 11 or
    the prism-free endpoint.
  - The final private-label inequalities can be arithmetically tight at
    (n1,n2,n3,|O|)=(0,0,1848,1848), but no graph, cover, or circuit system
    realizing that row is asserted.
  - The trace-field family controls only ordinary subspace intersections,
    not the simultaneous 99-star incidence and pairing alphabet.
  - Conway-99 and external novelty remain UNKNOWN.
```

## 1. Frozen equality setting

Assume the independently verified conditional rank-11 endpoint model and,
for contradiction, Wave 181 equality:

```text
n3=4158, P=0, rank_F3(D)=11, Q=2079.              (2)
```

Fix a graph nonedge `xy`.  Its two seven-block stars are disjoint.  Let
`R=R_xy` be the true ternary relation code on their 14 centered columns.
After permuting coordinates and choosing the signs used by the Wave 181
checkerboard relation, the two individual-star circuits and the canonical
conic can be written

```text
s_x=(1,1,1,1,1,1,1 | 0,0,0,0,0,0,0),
s_y=(0,0,0,0,0,0,0 | 1,1,1,1,1,1,1),
c  =(1,-1,0,0,0,0,0 | -1,1,0,0,0,0,0).          (3)
```

Each star has exactly one projective relation, supported on all seven
coordinates.  The word `c` has weight four, so it is outside
`S=<s_x,s_y>`.  Therefore

```text
T=<s_x,s_y,c> subset R, dim(T)=3.                 (4)
```

The two star words also show that every one of the 14 coordinates is active
in `R`.

## 2. Exact weight enumerator of `T`

Write a word of `T` as

```text
a*s_x+b*s_y+d*c.
```

If `d=0`, the nine words in the star subcode have distribution

```text
weight 0:   1,
weight 7:   4,
weight 14:  4.                                    (5)
```

Now take `d!=0`.  On either seven-coordinate side, the conic has two
opposite nonzero coefficients.  If the corresponding star coefficient is
zero, that side has weight two.  If it is nonzero, exactly one conic
coordinate cancels and the other five formerly zero coordinates become
nonzero, so that side has weight six.

There are two choices for `d`.  Splitting according to whether zero, one,
or both of `a,b` are nonzero gives

```text
weight 4:   2,
weight 8:   8,
weight 12:  8.                                    (6)
```

Thus the complete enumerator and total weight are

```text
A_0=1, A_4=2, A_7=4, A_8=8, A_12=8, A_14=4,
sum_(t in T) wt(t)=252.                           (7)
```

This checks every word of `T` by a `3 by 3` coefficient split; it is not a
search.

## 3. The proposed dimension-four averaging lemma is valid

Put `k=dim(R)`.  Full support gives the standard exact total-weight identity

```text
sum_(w in R) wt(w)=14*2*3^(k-1)=28*3^(k-1).       (8)
```

If `k>=4`, remove the 27 words of `T`.  By (7), the average weight on
`R minus T` is

```text
[28*3^(k-1)-252]/[3^k-27]
 =28[3^(k-1)-9] / 3[3^(k-1)-9]
 =28/3.                                           (9)
```

Hence some `w in R minus T` has integer weight at most nine.

The support-minimization step must be performed outside `T`.  Among the
relations outside `T` whose supports lie in `supp(w)`, choose `u` with
minimal support.  Suppose a nonzero relation `v` has proper support inside
`supp(u)`.

- If `v` is outside `T`, it contradicts the choice of `u`.
- If `v` is in `T`, choose a scalar so that `u-lambda*v` cancels one
  coordinate of `v`.  It remains outside `T`, because `u` is outside `T`
  and `lambda*v` is in `T`; it is nonzero and has strictly smaller support,
  again a contradiction.

Therefore `supp(u)` is a circuit.  A one-sided circuit in the 14-coordinate
union would have to be one of the full seven-star circuits, hence would lie
in `T`.  Thus `u` uses both stars.  Since `xy` is a nonedge, every support
block contains exactly one of `x,y`; using both sides means that `u`
cross-realizes `xy`.

Finally, `u` is outside `T`, so it is not the canonical conic.  Its weight
is at most nine and at least four by the verified dual distance.  It is
therefore a noncanonical short circuit cross-realizing a nonedge,
contrary to the Wave 181 equality clause.  Consequently the proposed
implication is correct:

```text
Wave181 equality would force dim(R_xy)<=3.         (10)
```

Together with (4), this would give `dim(R_xy)=3`.

## 4. Stronger obstruction: `T` itself violates equality

The preceding argument overlooks that `T` already contains weight-eight
eliminations.  From (3), take

```text
w_x=c+s_x.
```

Exactly one of the two `x`-side conic coordinates cancels.  Therefore

```text
wt(w_x)=8,
|supp(w_x) intersect star(x)|=6,
|supp(w_x) intersect star(y)|=2.                  (11)
```

The dependent support `supp(w_x)` contains a circuit `C_x`.  It cannot be
one-sided: the `x` side omits one coordinate of its unique seven-star
circuit, and the `y` side contains only two coordinates.  Hence `C_x`
uses both sides and cross-realizes `xy`.

Moreover, `C_x` is not the canonical conic `c`, because the conic coordinate
canceled in (11) does not belong to `supp(w_x)`.  The canonical
quadrilateral attached to `xy` is unique, so a different circuit
cross-realizing `xy` cannot be a canonical conic attached to another
nonedge pair.

The symmetric elimination

```text
w_y=c+s_y
```

gives a second noncanonical cross circuit `C_y` of weight at most eight.
Indeed `supp(w_x) intersect supp(w_y)` consists of only one conic
coordinate on each side, hence has size two.  The verified dual distance
at least four shows that `C_x` and `C_y` are distinct.

Thus one canonical conic together with the two compulsory star circuits
already forces at least two further projective short circuits
cross-realizing its diagonal nonedge.  But Wave 181 equality says that all
nonedge-realizing short circuits are exactly the 2,079 canonical conics.
This is a direct contradiction.

Therefore the equality face is not viable:

```text
Q!=2079.
```

Combining this with the verified Wave 180 integer lower bound `Q>=2079`
already proves the preliminary strict improvement `Q>=2080`.  The next
section amplifies the same elimination before imposing equality.

## 5. Minimal-cover amplification

Drop the temporary assumption `Q=2079`, but retain the conditional rank-11
endpoint and all verified Wave 179--181 structural results preceding the
equality analysis.

Choose an inclusion-minimal family of projective short-circuit supports
whose cross-realization sets cover all 4,158 nonedges.  If `n_i` is the
number of selected supports cross-realizing exactly `i` nonedges, then
Wave 179's capacity-three theorem gives

```text
n_1+2*n_2+3*n_3>=4158.                            (12)
```

Every selected support has a private nonedge label: otherwise all labels
it covers would remain covered after deleting it.  To avoid collision with
the endpoint notation `P=0`, let `P_priv` be the total
number of nonedges having cover multiplicity one.  The other
`4158-P_priv` labels have cover multiplicity at least two, so, with

```text
S=n_1+2*n_2+3*n_3,
P_priv+2*(4158-P_priv)<=S,
P_priv>=8316-S.                                   (13)
```

Every label of a selected multiplicity-one support is private.  These
labels are distinct, so if `P_23` counts the private labels carried by
multiplicity-two or multiplicity-three supports, then

```text
P_23=P_priv-n_1
 >=8316-2*n_1-2*n_2-3*n_3.                       (14)
```

### Multiplicity two

Wave 181's classification of exact multiplicity two is proved before its
equality hypothesis is imposed.  Every selected multiplicity-two circuit is
therefore the checkerboard conic on the canonical quadrilateral of its two
diagonal nonedges.

Let `xy` be any private label of such a selected conic.  Section 4 applies
verbatim.  Translating the conic relation by the full `x`-star and by the
full `y`-star gives dependent supports of shapes `6+2` and `2+6`.  Circuits
inside them:

1. cross-realize `xy`;
2. are noncanonical and distinct from the selected conic;
3. are distinct from one another because the two translated supports meet
   in only two coordinates; and
4. lie outside the selected cover, because any second selected circuit
   serving `xy` would contradict privacy.

Thus every private label carried by a selected multiplicity-two support
has two distinct outside circuits serving it.

### Multiplicity three

Wave 180 proves, again without assuming `Q=2079`, that every exact
multiplicity-three support belongs to a unique conic/complement pair:

```text
c_4: z_T+2*sum_(S in A) z_S=0,   |A|=3,
c_5: z_T+  sum_(S in B) z_S=0,   |B|=4.           (15)
```

Both members serve the same three nonedges.  An inclusion-minimal cover
cannot contain both, so the companion of a selected member lies outside
the cover.  Companions belonging to distinct selected multiplicity-three
supports are distinct by Wave 180's exact three-label classification.

Now let `xy` be any private label of the selected support, with `x` the
common center and `y` the corresponding leaf of the triangle `T`.  The
full `y`-star circuit is

```text
z_T+sum_(U in star(y) minus {T}) z_U=0.
```

Add twice this star relation to the weight-four relation in (15).  The
`T` coordinate cancels, leaving a true relation with support

```text
three x-star blocks + six outer y-star blocks,
weight 3+6=9.                                     (16)
```

Neither side contains its full seven-star circuit.  A circuit inside (16)
therefore uses both sides and cross-realizes `xy`.  It is distinct from
both `c_4` and `c_5`, since its support omits `T` while both canonical-pair
supports contain `T`.  Privacy again puts it outside the cover.  It is
also distinct from the outside companion, for the same `T`-coordinate
reason.

Thus every private label carried by a selected multiplicity-three support
also has two distinct outside circuits serving it: the canonical companion
and the corresponding private-leaf translate.  If one selected triple has
several private labels, the same companion is used once for each such
label.  This is legitimate incidence counting: the companion really serves
all three labels, and Wave 179's capacity bound will charge all of those
uses.

### Outside-pool accounting

Let `O` be the set of all nonedge-realizing projective short circuits
outside the selected cover.  The preceding two subsections give two distinct
`(private label, outside circuit)` incidences for every one of the `P_23`
private labels.  One outside circuit serves at most three nonedges, so it
occurs in at most three of these incidences.  Therefore

```text
3*|O|>=2*P_23
 >=16632-4*n_1-4*n_2-6*n_3.                      (17)
```

The distinct Wave 180 companions separately give

```text
|O|>=n_3.                                         (18)
```

### Exact optimization

Double (17) and rearrange:

```text
6*|O|+8*n_1+8*n_2+12*n_3>=8*4158.                (19)
```

Equation (18) gives the nonnegative remainder

```text
3*|O|+n_1+n_2-3*n_3>=n_1+n_2>=0.                 (20)
```

Add (19)--(20).  Since the selected cover and `O` are disjoint subsets of
the `Q` nonedge-realizing projective short circuits,

```text
9*Q
 >=9*(n_1+n_2+n_3+|O|)
 >=8*4158,

Q>=8*4158/9=3696.                                 (21)
```

All inequalities can be arithmetically tight at

```text
(n_1,n_2,n_3,|O|)=(0,0,1848,1848),
S=5544, P_priv=P_23=2772, Q=3696.
```

No cover or graph realizing this row is asserted.

Finally, Wave 180's 693 edge-specific circuits are mutually distinct and
disjoint from every nonedge-realizing circuit.  Therefore

```text
projective circuits of weights 4..9 >=3696+693=4389,
B_4+B_5+B_6+B_7+B_8+B_9>=2*4389=8778.            (22)
```

## 6. Why `dim(R_xy)=3` is no longer a live equality geometry

If one used only Section 3, the rank-nullity calculation would be

```text
dim(E_x+E_y)=14-dim(R_xy)=11,
dim(E_x intersect E_y)=6+6-11=1.                 (23)
```

The canonical root line `<rho_xy>` already lies in the intersection, so
(23) would identify

```text
E_x intersect E_y=<rho_xy>.                       (24)
```

However, Section 4 contradicts the same equality premise before (24) can
be interpreted as the geometry of an existing equality configuration.
Accordingly (24) must not be promoted as a new live conditional branch.
It remains a valid formal consequence of the inconsistent equality
hypotheses.

## 7. Formal orthogonal partial-spread shadow

For completeness, temporarily retain the formal relation (24).  Fix a
norm-one global root `r`, and for every `x` in its support put

```text
F_x=E_x intersect r^perp.
```

Because `r` is nonsingular and `E_x` is a nondegenerate six-space,

```text
E_x=<r> orthogonal_sum F_x,
dim(F_x)=5,
F_x is nondegenerate.                             (25)
```

Inside the ten-space `H=r^perp`, any nonedge `xy` of color `r` would have

```text
F_x intersect F_y=0                               (26)
```

by (24).  Thus the color graph gives a constant-dimension subspace code
whose color edges have maximum subspace distance ten.  In the previously
derived support shapes, the largest pairwise-disjoint subfamily required
this way has size only five.

The determinant lane identifies the centered eleven-space as nonsquare.
Since `r` has norm one, `H` is a nonsquare ten-space, hence the split
orthogonal space `O^+(10,3)`.  The local simplex six-space has square
determinant; (25) then makes every `F_x` a square-determinant five-space.

These conditions do not approach an orthogonal partial-spread obstruction.
There is an analytic family with 121 pairwise-disjoint five-spaces of the
required determinant class.

Let `K=F_(3^5)` and let

```text
tau(u,v)=Tr_(K/F_3)(u*v).
```

On `K direct_sum K`, use the hyperbolic form

```text
B((x,y),(x',y'))=tau(x,y')+tau(x',y).
```

For every `a in K^*`, define the graph

```text
L_a={(x,a*x):x in K}.
```

Then:

1. `L_a intersect L_b=0` for `a!=b`, because multiplication by `a-b` is
   invertible.
2. The restricted form is

   ```text
   B((x,a*x),(x',a*x'))=2*Tr(a*x*x'),
   ```

   so `L_a` is nondegenerate.
3. Its determinant square class is

   ```text
   2*disc(tau)*Norm_(K/F_3)(a),
   ```

   because the dimension is five and the determinant of multiplication by
   `a` is its norm.
4. The norm map has two fibers on `K^*`, each of size

   ```text
   (3^5-1)/(3-1)=121.
   ```

   Exactly one fiber gives the desired square determinant class.

Hence 121 pairwise-disjoint nondegenerate five-spaces of the local type
coexist in the correct split ten-space.  This is a hostile positive control
for ordinary partial-spread or constant-dimension-code bounds.  It does not
model the required positive intersections on original graph edges, the
local simplex embeddings, or simultaneous compatibility across all roots.

## 8. Boundary

The main conclusion is the private-label amplification

```text
Q>=3696,
B_4+B_5+B_6+B_7+B_8+B_9>=8778.
```

It rests on the circuit eliminations in Sections 4--5 and requires
independent verification before promotion.  In particular, Section 4
already invalidates the `Q=2079` premise under which the downstream
Wave 182--185 equality geometry was developed.

The formal subspace-code continuation supplies no additional obstruction:
its basic pairwise-disjointness requirement is far below an explicit
121-space analytic family.

No rank-11 exclusion, strict improvement to `n3<=4158`, graph construction,
or Conway-99 resolution follows.  External novelty is `UNKNOWN`.
