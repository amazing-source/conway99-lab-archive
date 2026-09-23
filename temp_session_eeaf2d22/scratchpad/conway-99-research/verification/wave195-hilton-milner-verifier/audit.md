# Independent Wave195 Hilton--Milner audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Under the frozen conditional prism-free rank-11 endpoint assumptions,

```text
Q>=6980,
```

where `Q` counts projective short circuits cross-realizing at least one
graph nonedge.

This is a conditional analytic lower bound. It is not an endpoint
contradiction or an object construction.

## Clean-room separation and integrity

The independent flag theorem, set-family split, oriented-label row,
coefficient identity, and rational null were frozen before either Wave195
package was opened. The frozen file has SHA-256

```text
dccdf05ba920b61df542e3c0795a95a1ef515a58138424ea05cd07bc0a4893e7.
```

The source manifests have the requested hashes:

```text
primary: 1055402dac438ad8f13e9e3fc91ec71a6da0f936306f379fa8f3deedb5b0c45b
proof B: feb5cbd767f8e7f223a012818b6177119a233b3a8bb3cbbb148d52fa7a2706c3
```

All ten direct inputs matched. Every entry in both source manifests, both
source input freezes, and the sealed Wave174, Wave180, Wave186, Wave188,
Wave189, Wave191, and Wave194 premise manifests also matched.

## 1. Canonical exact-three flags

Wave180 canonically represents an exact-three companion pair by

```text
(x,T),  T={y,u,v},  x anticomplete to T.
```

Let `S_x` be the seven graph triangles through `x`. The flag determines
the three-subset

```text
A_x(T)={S in S_x: j(T,S)=2}
```

and the true relation

```text
z_T+2*sum_(S in A_x(T)) z_S=0.                  (1)
```

One flag determines one weight-four/weight-five companion pair. The
selected exact-three pairs and the orbit-closed old raw pairs are distinct:
minimality prevents two selected companions, and the verified Wave189
separation keeps the old raw pool outside the selected pair pool. Wave194
also separates the new residual pairs, although they are not needed for
the Wave195 lower bound.

Fix a center `x`. If two distinct leaf triangles had the same `A` set,
subtracting their instances of (1) would give

```text
z_T-z_T'=0,
```

a nonzero weight-two relation. Dual distance at least four excludes this.
Thus `T -> A_x(T)` is injective and the local `A` family is simple.

## 2. Pairwise intersection from dual distance

Suppose two fixed-center sets `A,A'` were disjoint. They occupy six of the
seven star blocks; let `L` be the last. Adding their two relations (1) and
the full-star relation over `F_3` gives

```text
z_T+z_T'+z_L=0.
```

The blocks `T,T',L` are distinct: the first two avoid `x`, while `L`
contains `x`, and fixed-center flag simplicity makes `T!=T'`. This is a
forbidden weight-three relation. Hence the local family is pairwise
intersecting.

The independent pre-source reconstruction used the equivalent cancellation
of one weight-four relation with the other flag's complementary relation.
It yields the same weight-three word.

## 3. Exact Hilton--Milner specialization

The required theorem applies to a family of distinct `k`-subsets of an
`n`-set that is pairwise intersecting and has empty total intersection,
with `n>2k`:

```text
|F|<=C(n-1,k-1)-C(n-k-1,k-1)+1.
```

For `n=7,k=3`,

```text
C(6,2)-C(3,2)+1=15-3+1=13.                     (2)
```

The original article metadata and DOI were checked at the
[Oxford publisher page](https://academic.oup.com/qjmath/article-abstract/18/1/369/1584607).
The exact formula and hypotheses were also checked in Peter Frankl's
primary paper,
[A simple proof of the Hilton--Milner theorem](https://msp.org/cnt/2019/8-2/moscow-v8-n2-p01-s.pdf).

If the fixed-center `A` family has empty total intersection, write its size
as `c_x`. Equation (2) gives

```text
c_x<=13,
j_x<=3c_x<=39,                                  (3)
```

where `j_x` is the number of distinct leaf vertices, equivalently oriented
labels `x->y`, in the flag union.

## 4. Common-star branch

Suppose instead every member contains one common block

```text
S={x,p,q}.
```

For each leaf triangle `T`, membership `S in A_x(T)` says exactly two cross
edges join `S` to `T`. Since `x` is anticomplete to `T`, these start at
`p,q`.

Neither `p` nor `q` can meet two leaves of `T`: if `p` met two vertices of
the triangle, their graph edge would have both `p` and the third leaf as
common neighbors, contradicting `lambda=1`. Thus `p` and `q` each meet one
leaf. Those leaves are distinct, because a shared leaf together with `x`
would give the edge `pq` two common neighbors.

There are at most

```text
deg(p)-2=12
```

possible `p`-leaves after excluding the known neighbors `x,q`, and
similarly at most 12 possible `q`-leaves. Fixed-center injectivity bounds
the number of flags through a common star block by

```text
c_x<=C(6,2)=15.
```

Each flag contributes at most one remaining leaf. The complete union
therefore satisfies

```text
j_x<=12+12+c_x<=39.                             (4)
```

Equations (3)--(4), including the empty-family case, establish the universal
local cap `j_x<=39`.

## 5. Oriented-label lower bound

Let

```text
J=sum_x j_x.
```

Summing the local cap over 99 graph vertices gives

```text
J<=99*39=3861.                                  (5)
```

Let `U` be the undirected label union of the selected exact-three circuits.
Every label outside `U` is covered by a selected type-one or type-two
incidence, so

```text
|U|>=C-n1-2n2.                                  (6)
```

Each distinct label in `U` supplies at least one oriented label to `J`.
The old exact-three raw assignments counted by `a3+b3` supply additional
oriented private labels outside `U`:

- a type-one source supplies one orientation of its distinct private
  nonedge;
- the two endpoint translations for one type-two private nonedge, when
  both exact three, have opposite centers and therefore give the two
  opposite oriented labels;
- different private source labels have different underlying undirected
  nonedges, even if their raw circuits occupy the same exact-three pair.

Thus the assignment-to-oriented-label map is injective:

```text
J>=|U|+a3+b3
 >=C-n1-2n2+a3+b3.                              (7)
```

Combining (5)--(7) gives the new slack

```text
SG=3861-C+n1+2n2-a3-b3>=0.                     (8)
```

### Wording correction with no mathematical effect

The primary proof's sentence saying every label outside `U` is private is
too strong. Such a label may be shared by selected type-two circuits.
Only coverage by a selected low incidence is required for (6). The
`a3+b3` labels used in (7) are separately known to be private, so this
wording correction does not change `SG` or the theorem.

## 6. Exact certificate

Retain the verified Wave194 slacks

```text
SI =I-2C,
S2 =p2-n2,
SE2=2r2-a2-c2,
RA =3h+y+3g-a2-a3-2b3-c2,
SL =n1+2n2+c1+2r2+y+2W-C.
```

The disjoint circuit inventory is

```text
Q>=Q0,
Q0=n1+n2+2n3+r1+r2+2h+y+2g+W.
```

After the four raw substitutions, independent exact rational expansion
gives

```text
Q0-(11C-3861)/6

 =(2/3)SI
  +(4/3)S2
  +(1/6)SE2
  +(2/3)RA
  +(1/3)SL
  +(1/6)SG
  +a1/6
  +b3/2
  +c2/6
  +W/3.                                         (9)
```

All terms are nonnegative. At the fixed endpoint,

```text
3861=13C/14,
(11C-3861)/6=47C/28=13959/2.
```

Since `Q` is integral,

```text
Q>=6980.
```

Adding the 693 verified edge-isolated projective circuits gives 7,673
projective short circuits and 15,346 nonzero scalar circuit words.
Wave188's 18,018 all-short-word lower bound remains numerically stronger
because it includes nonminimal words.

## 7. Rational null boundary

The independently frozen arithmetic control has

```text
a2=n1=297,
c1=p3=r1=3564,
n3=1386,
r2=297/2,
h=99,
all other split and new-pool variables zero.
```

It makes `SI,S2,SE2,RA,SL,SG` zero and has `Q0=13959/2`. The two source
packages use two different rational controls; both were independently
replayed and also make all six slacks zero.

All three controls are fractional accounting rows only. None constructs a
flag family, circuit system, cover, code, endpoint, or graph.

## 8. Failed route quarantine

The abandoned mixed type-one route tried to force canonical all-equal
leaf owners by two successive circuit eliminations. The second subtraction
can return the already selected owner, and it can reintroduce a coordinate
omitted by the first translation. Therefore it does not prove a new
circuit or a second endpoint orientation.

The successful theorem uses each `a3` assignment exactly once in (7). No
factor two and no canonical type-one leaf-support claim enters (8) or (9).
Both source packages preserve this failed route explicitly.

## Reproducibility and boundary

```text
independent math replay:       PASS
independent full replay:       PASS
independent tests:             12/12 PASS
primary source replay:         PASS
primary source tests:          9/9 PASS
proof-B source replay:         PASS
proof-B source tests:          6/6 PASS
all frozen hashes:             PASS
```

No graph, code, cover, SAT, LP, configuration, enumeration, isomorphism,
or brute-force search was used in the sealed proof or verifier. Rank 11,
endpoint existence, strict original `n3` improvement, external novelty,
and Conway-99 remain `UNKNOWN`.
