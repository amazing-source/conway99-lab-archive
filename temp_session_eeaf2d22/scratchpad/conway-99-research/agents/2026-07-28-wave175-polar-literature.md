# Wave 175 literature report: the exact polar object is not a standard named class

```yaml
role: literature
date_utc: 2026-07-28T21:50:40Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: CITED
scope: >-
  Named-class and exclusion-theorem check for 231 singular points of Q(10,3)
  having induced polar degree 32, ordinary no-three-collinear property, and
  a spanning zero-tight-frame identity.
inputs:
  - https://cage.ugent.be/~bamberg/Research_files/Tight%20Sets%20and%20movoids%20of%20Polar%20Spaces.pdf
  - https://cage.ugent.be/geometry/Files/412/nonexistence.pdf
  - https://www.ericmoorhouse.org/pub/orthog.pdf
  - https://arxiv.org/abs/2406.03043
  - https://arxiv.org/abs/2012.12977
  - https://cage.ugent.be/~mrodgers/papers/CLPolar.pdf
  - https://arxiv.org/abs/1502.01926
  - https://arxiv.org/abs/2101.11756
method: >-
  Primary-source definition and theorem comparison, with exact substitution
  of the Wave 175 parameters and moments.
command: >-
  Exact rational arithmetic and primary-source PDF inspection; no graph,
  code, SAT, isomorphism, or numerical optimization search.
outputs: []
limitations:
  - Exact existence or nonexistence remains UNKNOWN.
  - This is a targeted named-class search, not an exhaustive literature proof.
  - No classification theorem found covers all four Wave 175 conditions.
```

## Exact object searched

At the conditional centered rank `k=11`, Wave 175 asks for

```text
S subset Q(10,3),
|S|=231,
the polar graph induced on S is 32-regular,
no three points of S are projectively collinear,
sum_(g in S) g*g^T=0 over F_3.
```

No inspected theorem excludes or classifies this conjunction.

## Named classes that do not apply

Bamberg--Kelly--Law--Penttila characterize proper intriguing sets of a finite
polar space as tight sets or `m`-ovoids. In rank-five `Q(10,3)`, their sizes
specialize to

```text
|m-ovoid|=244*m,
|i-tight set|=121*i.
```

Neither can equal 231. The Wave 175 outside orthogonality count also has
nonintegral mean

```text
2265648/29293 = 205968/2663,
```

so the outside intersection number is not constant. Internal regularity
alone therefore does not make the set intriguing.

De Bruyn proves that a two-character set contained in a nonsingular
parabolic quadric is a projective subspace contained in the quadric. The
Wave 175 moments already show that the needed two-character premise fails.
Selected tangent hyperplanes have intersection size 33. If every outside
tangent hyperplane had one other character `h`, the first two moments would
force

```text
h=(176288112-33*2265648)/(2265648-33*29293)
 =1025472/13121,
```

which is not an integer.

Blokhuis--Moorhouse use “cap on a quadric” to forbid every pair on a quadric
line. The Wave 175 set has 3,696 such orthogonal pairs. Its ordinary
projective-cap condition only forbids three selected points on one ambient
line, so their cap bound is inapplicable.

The inspected partial-`m`-ovoid results require generator-intersection bounds
not supplied by an ordinary projective cap. Cameron--Liebler classifications
concern sets of generators rather than points. Weighted intriguing sets
still require the characteristic vector to lie in the principal plus one
polar eigenspace, whereas both Wave 175 nonprincipal spectral energies are
positive.

Greaves--Iverson--Jasper--Mixon call the matrix identity a zero-tight or
totally isotropic finite-field frame. Their immediate size bound is only
`231>=2*11`. This tight-frame terminology is unrelated to a polar tight set,
and it does not incorporate the singular, cap, or induced-degree conditions.
The single zero-frame identity likewise does not supply the higher operator
moments of a finite-field projective 2-design.

## Boundary

The next applicable theorem must address the combined class of ordinary
projective caps inside `Q(10,3)` with prescribed induced polar regularity and
a characteristic-three zero-tight-frame identity. None of the standard
named-class classifications inspected here collapses that boundary.
