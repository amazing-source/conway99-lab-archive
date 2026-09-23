# Wave 197 proof A: degree-ten flag incidence

## Verdict

`DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

Under the frozen conditional prism-free rank-11 endpoint assumptions,

```text
Q>=7033,
```

where `Q` is the number of projective short circuits cross-realizing at
least one graph nonedge.

The new theorem is a multiplicity-sensitive refinement of Wave196. A fixed
undirected nonedge belongs to at most ten selected exact-three flags: at
most five with either endpoint as center. Combining this degree cap with
the Wave196 bounds `F<=1287` and `J<=3564` gives a new global slack. An
exact rational certificate raises the integer bound from 7,029 to 7,033.

No graph, code, cover, SAT, LP, configuration, enumeration, or isomorphism
search is used.

```yaml
role: proof_a
date_utc: 2026-07-29T05:18:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: prove a degree-ten cap for
  selected exact-three incidence at every nonedge, combine it with the
  Wave196 flag and oriented-label caps, and derive Q>=7033 by an exact
  rational certificate.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave194-five-thirds-verifier/package-manifest.sha256: 236facbec2539a87e197fd0b2b8ca66bc0d53b12415fdf216acf410064d7ca64
  attempts/wave196-four-fiber-hilton-milner-proof-a/package-manifest.sha256: 83bd93ab0980305d59052dd25dc373f582b5a6fc998b122d64d506871e244b1c
method: >-
  SRG triangle incidence, minimal-cover privacy, exact-three flag
  orientation, bounded-degree incidence counting, the Wave196
  Hilton--Milner/four-fiber caps, and an exact rational dual certificate.
  No graph, code, cover, SAT, LP, configuration, enumeration, or
  isomorphism search.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave197-degree10-flag-cap-proof-a\exact_check.py --verify
  attempts\wave197-degree10-flag-cap-proof-a\exact-results.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave197-degree10-flag-cap-proof-a\test_exact_check.py
outputs:
  - agents/2026-07-29-wave197-degree10-flag-cap-proof-a.md
  - attempts/wave197-degree10-flag-cap-proof-a/
limitations:
  - This is a proof-agent derivation, not verifier promotion.
  - It is conditional on the prism-free rank-11 endpoint and on the sealed
    Wave196 derived local theorem.
  - No endpoint graph, code, cover, flag system, or circuit family is
    constructed.
  - The rational null row is arithmetic only and is not an object.
  - Rank 11, endpoint existence, strict original n3 improvement, external
    novelty, and Conway-99 remain UNKNOWN.
```

## 1. Five flags in one orientation

Fix a graph nonedge

```text
e={x,y}.
```

The seven graph triangles through `y` partition its 14 neighbors into
seven pairs. Since `xy` is a nonedge, it has exactly

```text
N(x) intersect N(y)={a,b}
```

with `mu=2`.

The vertices `a,b` lie in two distinct triangles through `y`. If they lay
in the same triangle, they would be adjacent and their graph edge would
have both `x` and `y` as common neighbors, contradicting `lambda=1`.

Exactly those two `y`-triangles contain a neighbor of `x`. The other five
triangles through `y` are anticomplete to `x`. Consequently there are
at most five possible exact-three flag supports

```text
(x,T),  y in T,
```

whose center-to-leaf labels include `xy`.

Each support has one exact-three companion pair. A minimal selected cover
cannot select both companions: they realize the same three nonedge labels,
so if both were selected neither would have a private label. Hence at most
one selected exact-three circuit is used on each support.

Therefore at most five selected exact-three circuits containing `e` have
center `x`. By symmetry, at most five have center `y`. Every canonical
exact-three circuit realizing `e` has one of those two centers, so

```text
d(e)<=10,                                        (1)
```

where `d(e)` is the number of selected exact-three circuits realizing
`e`.

## 2. Multiplicity-sensitive incidence row

Let `U` be the union of the nonedge labels on the selected exact-three
circuits. Each selected exact-three circuit has exactly three labels, so

```text
sum_(e in U) d(e)=3*n3.                          (2)
```

The `p3` private labels of selected exact-three sources each have

```text
d(e)=1.
```

Every other label in `U` has degree at most ten by (1). Thus

```text
3*n3
 <=p3+10*(|U|-p3),
3*n3+9*p3<=10*|U|.                              (3)
```

Now use the full selected/old/new exact-three flag pool of Wave196. Its
oriented label union has size `J<=3564`. Every label in `U` supplies at
least one oriented label in that pool. The `a3+b3` old raw exact-three
assignments add distinct oriented private labels outside `U`: a type-one
source supplies one orientation, while the two raw translates of one
type-two private nonedge supply its opposite orientations. Hence

```text
|U|+a3+b3<=J<=3564.                             (4)
```

Combining (3)--(4) gives the new nonnegative slack

```text
S10=35640-3*n3-9*p3-10*a3-10*b3>=0.            (5)
```

## 3. Flag-count and old exact-three capacities

Wave196 also proves that the complete exact-three flag pool has at most
13 flags per center:

```text
SF=13*99-n3-h-g
  =1287-n3-h-g>=0.                              (6)
```

The verified old raw exact-three pair capacity remains

```text
SH=3*h-a3-b3>=0.                                (7)
```

The `g` pairs in (6) are the genuinely new residual exact-three companion
pairs and are disjoint from the selected and `h`-old pools.

## 4. Exact certificate

Retain the Wave194 raw identities

```text
a1+a2+a3=n1,
b1+b3=2*p2,
c1+c2=p3,
r1=a1+b1+c1,                                    (8)
```

the certified count

```text
Q0=n1+n2+2*n3+r1+r2+2*h+y+2*g+W,
```

and the nonnegative slacks

```text
SI =2*n1+2*n2+3*n3+p2+p3-2*C,
S2 =p2-n2,
SE2=2*r2-a2-c2,
RA =3*h+y+3*g-a2-a3-2*b3-c2,
SL =n1+2*n2+c1+2*r2+y+2*W-C.                  (9)
```

Let `V=99`. After substituting (8), direct coefficient comparison gives

```text
Q0-(57*C-263*V)/30

 =(4/5)*SI
  +(6/5)*S2
  +(1/5)*SE2
  +(7/10)*RA
  +(3/10)*SL
  +(1/90)*S10
  +(4/45)*SH
  +(11/30)*SF
  +a1/10+3*b3/5+c2/5+4*g/15+2*W/5.             (10)
```

Every term on the right is nonnegative. Wave194 proves `Q>=Q0`, so

```text
Q>=(57*C-263*V)/30.
```

At `C=4158,V=99`,

```text
(57*C-263*V)/30
 =70323/10
 =7032.3.
```

Since `Q` is integral,

```text
Q>=7033.                                        (11)
```

Adding the 693 independently verified edge-isolated projective circuits
gives at least 7,726 projective short circuits in total, or 15,452
nonzero scalar circuit words.

## 5. Rational scalar null

All variables omitted below are zero:

```text
n1=a2=y=33/5,
n2=p2=1518/5,
n3=1287,
p3=c1=3531,
b1=3036/5,
r1=20691/5,
r2=33/10.
```

This row satisfies the raw identities and makes

```text
SI=S2=SE2=RA=SL=S10=SH=SF=0,
Q0=70323/10.
```

It has Wave196 slack `S36=99/5`; that row is not needed in (10). The
fractional row proves scalar sharpness only. It is not a graph, cover,
code, flag family, or circuit construction.

## Boundary

```text
five centered flags per oriented nonedge:      DERIVED
selected exact-three degree d(e)<=10:          DERIVED
S10>=0:                                        DERIVED
SF>=0:                                         DERIVED from Wave196
exact certificate (10):                        exact replay PASS
Q>=7033:                                       DERIVED
independent Wave197 verification:              pending
rational null row is an object:                no
rank 11 / endpoint excluded:                   no
Conway-99 / external novelty:                  UNKNOWN
```
