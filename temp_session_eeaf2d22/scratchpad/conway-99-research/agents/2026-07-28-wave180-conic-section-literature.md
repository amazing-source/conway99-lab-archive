# Wave 180 conic-section and Grassmannian literature audit

## Verdict

`CITED`, with endpoint status `UNKNOWN`.

The primary results classify the local four-point configuration and give
section-size ceilings, but none excludes the Wave 180 incidence.

## Exact local finite-polar classification

Choose six simplex vectors spanning `E_x`.  Their Gram determinant is

```text
det(J_6-I_6)=-5=1 mod 3.
```

The nondegenerate six-space is therefore minus type, and its singular points
form

```text
Q^-(5,3).
```

Any three star points span a nondegenerate projective plane.  Its singular
points form `Q(2,3)`, with the fourth point

```text
<s_i+s_j+s_k>.
```

Segre's theorem identifies every four-point oval in `PG(2,3)` as a
nonsingular conic.  The seven-point simplex has only its full seven-point
dependence, so different triples have different completion points.  There
are exactly

```text
binomial(7,3)=35
```

local conic completions per star space.  This classifies Wave 180's
weight-four circuit; it does not forbid it.

Primary source:

- Beniamino Segre,
  [*Ovals in a Finite Projective Plane*](https://doi.org/10.4153/CJM-1955-045-X).

## Cap-section ceilings

Because the global selected set is an ordinary projective cap,
`S intersect PG(E_x)` is a cap in `PG(5,3)`.  The sharp maximum is 56.
Hill, Landjev, Jones, Storme, and Barát also show that every 53-cap extends
to the Hill 56-cap.

Wave 180 supplies no intersection lower bound near 53, and an extension
inside `E_x` need not consist of globally selected points.  For points
arising by the proved three-star-point conic mechanism, the elementary
ceiling is already smaller:

```text
7+35=42 selected candidates per E_x.
```

Even if this applied to every external incidence, it would give

```text
sum_x |S intersect E_x|<=99*42=4158,
```

while the 231 block points contribute only `231*3=693` compulsory
incidences.  The ceiling is therefore far from contradictory.

Primary source:

- Ray Hill, Ivan Landjev, Chris Jones, Leo Storme, and János Barát,
  [*On Complete Caps in the Projective Geometries over F3*](https://doi.org/10.1007/BF01220305).

## Pluecker and exterior-algebra mismatch

Let `omega_x` be the Pluecker point of the six-space `E_x` in the
11-dimensional ambient space.  Pairwise incidence cannot be constrained by

```text
omega_x wedge omega_y,
```

because `exterior_power^12(V)=0` identically.  Point incidence is correctly
encoded by

```text
z wedge omega_x=0 in exterior_power^7(V),
```

but no linear-section or design condition on the 99 Pluecker points is
known.  The 99 selected spaces are not the intersection of the full
Grassmann variety with a projective linear space, so linear-section bounds
do not apply.  Polar-Grassmannian theorems about totally singular
subspaces also miss the target because every `E_x` is nondegenerate.

Primary source:

- Sudhir R. Ghorpade, Arunkumar R. Patil, and Harish K. Pillai,
  [*Decomposable Subspaces, Linear Sections of Grassmann Varieties, and
  Higher Weights of Grassmann Codes*](https://arxiv.org/abs/0710.5161).

## Missing bridge

The applicable missing theorem would need either a forced lower bound on
external incidences `z_T in E_x`, or a global restriction on which of the 35
local conic completions can coexist across overlapping star spaces.  None of
the checked primary results supplies that bridge.

```yaml
role: literature
date_utc: 2026-07-28T23:06:45Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: CITED
scope: >-
  Conic, cap-section, Pluecker, and polar-incidence theorem audit for the
  Wave180 six-space/simplex/external-point configuration.
inputs:
  - attempts/wave176-star-projector-circuits/package-manifest.sha256
  - orchestrator-frozen Wave180 equality configuration
method: >-
  Identified the six-space orthogonal type, substituted q=3 into the oval
  and PG(5,3) cap theorems, counted simplex-triple conic completions, and
  checked exterior-incidence hypotheses.
command: >-
  .\.venv\Scripts\python.exe -c "import math;
  print(math.comb(7,3),99*(7+math.comb(7,3)),231*3,99*56)"
outputs:
  - agents/2026-07-28-wave180-conic-section-literature.md
limitations:
  - No lower bound on external E_x incidences is supplied.
  - No global compatibility rule for the 35 local completions is supplied.
  - The endpoint and rank-11 branch remain UNKNOWN.
  - External novelty is UNKNOWN.
```
