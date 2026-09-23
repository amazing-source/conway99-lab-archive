# Independent Wave194 five-thirds audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Under the frozen conditional prism-free rank-11 endpoint assumptions,

```text
3Q>=5C,
Q>=6930 for C=4158.
```

This is a conditional lower bound for projective short circuits realizing
nonedges. It is not an endpoint contradiction or an object construction.

## Integrity and clean-room separation

The independent theorem, collision audit, coefficient certificate, and
equality face were generated and frozen before either Wave194 package was
opened. The frozen mathematical file has SHA-256

```text
de84e57eb8c2cafa8d8d0621c54ddcb1dd64b0f78886d9ed4656e02a5764c0d0.
```

The two later-inspected source manifests have the requested SHA-256 values:

```text
primary: 0ba610983dff7365f7debd42b8155c07edcc5e64e5afb4e4d6529e6d1c0ad5a4
audit:   0e77b279efec786e3abab371b614061ea1624499c32549861c68fe9daba17918
```

All eight direct inputs matched. The verifier also checked all entries in
both source manifests, both source input freezes, and the sealed Wave181,
Wave188, Wave189, Wave191, and Wave193 premise manifests. No source checker
was imported or executed before the independent result freeze.

## 1. Raw split

Split the raw assignment incidence by selected source type and exact
cross-multiplicity:

```text
a1+a2+a3=n1,
b1+b3=2p2,
c1+c2=p3,
r1=a1+b1+c1.                                    (1)
```

There is no `b2`: the selected type-two checkerboard conic is already the
unique exact-two circuit through either private label, while the two
translated raws differ from it. There is no `c3`: the privacy-free Wave191
local theorem excludes exact-three type-three leaf extraction.

For the orbit-closed old raw pool,

```text
a2+c2<=2r2,
a3+b3<=3h.                                      (2)
```

Here `h` counts complete exact-three companion pairs. Such a pair has only
three label slots because its two circuit members realize the same three
labels.

## 2. Exact-three type-two raw residual

Fix a private label `e={x,y}` of a selected checkerboard conic. Its endpoint
translations have profiles

```text
W_x: 6+2,
W_y: 2+6.
```

The independent canonical support calculation gives

```text
|supp(W_x) intersect supp(W_y)|=2,
```

strictly below dual distance four.

Suppose a raw circuit `D_x` contained in `W_x` has exact multiplicity three.
Its three labels share a unique center. Since one label is `{x,y}`, the
center is `x` or `y`; the two-coordinate `y` side cannot contain the three
or four center-star blocks required for center `y`. Thus its center is `x`
and it has one leaf coordinate on the `y` side.

Subtract the unique scalar multiple of `D_x` that cancels this leaf
coordinate. The difference is nonzero:

- the other `y`-side coordinate remains;
- at least two of the six `x`-side coordinates remain because `D_x` uses
  only three or four of them.

Both sides are nonempty proper star subsets. A support-minimal circuit in
the difference therefore crosses `e`. It is distinct from:

- `D_x`, because the leaf coordinate was canceled;
- the opposite exact-three companion, because both companions contain that
  same leaf coordinate;
- the selected checkerboard conic, because `W_x` already omitted one conic
  coordinate.

Wave181 uniqueness consequently excludes exact multiplicity two. The
residual is exact one or exact three. The `W_y` case is symmetric.

## 3. Same-label double residuals and collision audit

Both type-two raws for one private label may be exact three, so their two
residual assignments must be genuinely distinct.

- If the two residuals were one exact-one circuit, its support would lie in
  `supp(W_x) intersect supp(W_y)`, of size two, contradicting dual distance
  at least four.
- If both were exact three, containment orients one at center `x` and the
  other at center `y`. They are neither equal nor companions because a
  companion pair has one common center.

The same observations exclude collision with the opposite raw extraction.
If that raw is exact one, equality again forces support into the
two-coordinate parent intersection. If it is exact three, it and its
companion have the opposite center.

The remaining pool collisions are also excluded:

- An exact-one residual cannot equal an old exact-one raw assigned to a
  different private label, because it would then realize two labels.
- For type one and type three there is only one raw assignment for the
  source private label. For type two the only other same-label raw was
  excluded above.
- An exact-two collision would be the unique selected conic, whose omitted
  coordinate is absent from the residual support.
- The source exact-three raw and its companion contain the canceled leaf.
- Privacy and owner-coordinate omission exclude selected circuits.
- The fixed-point-free companion involution excludes selected companions.
- Closing the old exact-three pool under companionship prevents a newly
  added mate from returning to an old exact-three orbit.

Thus the raw and forced-residual demand on exact-three label slots and new
exact-one circuits is

```text
a2+a3+2b3+c2.                                   (3)
```

The coefficient two on `b3` is one raw assignment plus its additional
residual assignment.

## 4. Split residual capacity

Let the genuinely new closed residual pool contain

```text
y exact-one circuits,
g complete exact-three companion pairs.
```

It contains `y+2g` projective circuits but has label capacity only `y+3g`.
Together with the `3h` old-pair slots, (3) gives

```text
RA=3h+y+3g-(a2+a3+2b3+c2)>=0.                  (4)
```

The split is essential. The low-target row below can use the `y` exact-one
circuits, but none of the exact-three members counted by `g`.

## 5. The `k`-cancelled type-three union row

Let `U` be the union of labels realized by selected type-three circuits.
Let `k` be the number of selected type-two label incidences lying in `U`.
A selected type-one label is private and hence outside `U`. Counting
selected low incidences outside the union gives

```text
C-|U|<=n1+2n2-k.                                (5)
```

For each distinct `e` in `U`, choose one selected type-three leaf relation
for `e`. Its proper two-star support contains a circuit crossing `e`, and
the privacy-free Wave191 exclusion makes the target exact one or two.

The exhaustive already-counted low-target capacity is

```text
selected type-two incidences in U: k,
old raw exact-one circuits:         c1,
old raw exact-two circuits:       2r2,
new residual exact-one circuits:    y,
additional low circuits:          2W.
```

Only `c1` appears among old exact-one raws. An `a1` or `b1` circuit realizes
its type-one or type-two private source label, which lies outside `U`.
Exact-three circuits from either the old or new pool cannot be low targets.
Consequently

```text
|U|<=k+c1+2r2+y+2W.                              (6)
```

Adding (5) and (6) cancels the same `k`:

```text
SL=n1+2n2+c1+2r2+y+2W-C>=0.                    (7)
```

This avoids charging a selected type-two incidence once outside `U` and
again inside it.

## 6. Exact five-thirds certificate

The disjoint circuit inventory is

```text
Q>=Q0,
Q0=n1+n2+2n3+r1+r2+2h+y+2g+W.
```

Put

```text
SI=I-2C,
S2=p2-n2.
```

After substituting (1), independent exact rational expansion gives

```text
Q0-5C/3

 =(2/3)SI
  +S2
  +(2/3)RA
  +(1/3)SL
  +a1/3
  +b1/6
  +b3/2
  +r2/3
  +W/3.                                         (8)
```

Every term is nonnegative. Hence

```text
3Q>=5C.
```

For `C=4158`, this is `Q>=6930`. Adding the 693 verified edge-isolated
projective circuits yields at least 7,623 projective short circuits and
15,246 associated nonzero scalar circuit words. Wave188's 18,018 bound on
all short words remains numerically stronger because it also counts
nonminimal words.

## 7. Equality conditions

Equality in (8), together with the unused raw capacities in (2), forces

```text
a1=a2=b1=b3=c2=n2=p2=r2=y=g=W=0,
a3=n1=3h,
c1=p3=r1=3n3,
h+n3=C/3.                                       (9)
```

Equivalently, with the independent parameter `m=n3`,

```text
0<=m<=1386,
a3=n1=4158-3m,
c1=p3=r1=3m,
h=1386-m,
Q0=6930.
```

The primary source uses `t=h`, so its parameterization is the reversal
`m=1386-t`. The two faces and the three checked rows are identical after
this change of variable.

Equation (9) is an arithmetic/accounting face only. It does not establish
compatible circuit supports, a global packet gluing, a cover, a code, an
endpoint, or a graph.

## Reproducibility and boundary

```text
independent math replay:       PASS
independent full replay:       PASS
independent tests:             9/9 PASS
primary source replay:         PASS
primary source tests:          7/7 PASS
hostile-audit source replay:   PASS
hostile-audit source tests:    5/5 PASS
all frozen hashes:             PASS
```

No graph, cover, code, SAT, LP, configuration, enumeration, isomorphism, or
brute-force search was used. Rank 11, endpoint existence, strict original
`n3` improvement, external novelty, and Conway-99 remain `UNKNOWN`.
