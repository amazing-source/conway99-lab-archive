# Wave 190 proof-A audit: residual label stability

## Verdict

`DERIVED_INDEPENDENTLY_SOUND_PENDING_VERIFIER`.

The proposed raw-plus-residual capacity refinement is sound.  Under the
conditional rank-11 endpoint assumptions it gives

```text
Q>=5544,
```

where `Q` counts projective short circuits cross-realizing nonedges.

```yaml
role: proof_a
date_utc: 2026-07-29T02:32:53Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Independent adversarial reconstruction of the Wave190 residual-stability
  strengthening from orbit-closed private-label extractions, including all
  raw/residual collision cases and the coefficient certificate Q>=5544.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  attempts/wave189-degree7-star-complete/package-manifest.sha256: dce4157a05fc20f9b3965ec9830a08f893eeefacdb347b084af13807fa417c90
  attempts/wave190-residual-stability-proof-b/package-manifest.sha256: e66987333e3f7119026520be9680699bcfdcfcddbf8877016d8d817193684a5a
method: >-
  Label-by-label collision audit, exact-one slack, Wave181 uniqueness for
  exact-two conics, exact-three companion-orbit capacity, and independent
  scalar coefficient reconstruction. No graph, cover, code, SAT,
  configuration, LP, isomorphism, or enumeration search.
command: >-
  python -B attempts/wave190-residual-stability-proof-b/exact_check.py;
  python -B -m unittest -v
  attempts/wave190-residual-stability-proof-b/test_exact_check.py
outputs:
  - agents/2026-07-29-wave190-residual-stability-proof-a-audit.md
limitations:
  - This is a proof-agent audit, not independent verifier promotion.
  - The result inherits the conditional and still-derived Wave189 inputs.
  - The sharp relaxation row is arithmetic, not an asserted cover.
  - Rank 11, endpoint existence, strict n3 improvement, external novelty,
    and Conway-99 remain UNKNOWN.
```

## 1. Frozen pool notation

Let

```text
A=n_1+2*p_2+p_3
```

be the raw extraction-assignment incidence.  Close its exact-three members
under the Wave 180 companion involution.  Write the closed pool as

```text
r circuits of exact multiplicity at most two,
h complete exact-three companion pairs.
```

Wave 189 gives

```text
A<=2*r+3*h.
```

Define the integral slack

```text
delta=2*r+3*h-A>=0.                              (1)
```

If `r_1` of the low circuits have exact multiplicity one, actual assignment
capacity sharpens the same inequality to

```text
A<=r_1+2*(r-r_1)+3*h,
r_1<=delta.                                      (2)
```

## 2. Residuals forced by type-three assignments

Let `a_H` be the total raw-assignment incidence absorbed by the `h`
exact-three pairs, and let `q_H` be its type-three part.  Of the `p_3`
type-three leaf assignments:

- at most `r_1` land on exact-one circuits;
- exactly `q_H` of those counted here land in exact-three pairs; and
- every remaining assignment lands on an exact-two circuit.

Thus the number `k` landing on exact-two circuits satisfies

```text
k>=p_3-r_1-q_H.                                  (3)
```

For each such assignment with private label `e`, Wave 181 identifies the
raw circuit as the unique canonical checkerboard conic `r_e`.  It lies in
the all-two `3+6` leaf relation `w_e`.  Either difference

```text
w_e-r_e, w_e-2*r_e
```

is a nonzero `2+5` weight-seven relation.  A circuit in its support
cross-realizes `e` and is distinct from `r_e`, the selected source, and its
selected-source companion.

## 3. Complete collision audit

A residual circuit cannot lie in the low part of the raw pool.

1. If it has exact multiplicity one, equality with a raw circuit assigned
   to another private label would make it cross two labels.  The only raw
   assignment for its own type-three label is `r_e`.
2. If it has exact multiplicity two, Wave 181 uniqueness forces it to be
   `r_e`, but the residual support omits two coordinates of `r_e`.

Privacy excludes the selected cover and selected-type-three companion
pool.  Therefore an old circuit can absorb the residual only inside one of
the `h` exact-three pairs.

The delicate improvement is label-by-label.  A pair has only three labels.
Wave 189 proves that the two raw type-two extractions for one label cannot
be its two companion members, so raw assignments in a pair use distinct
labels.  For a type-three label, a residual exists only when its raw leaf
assignment landed on an exact-two conic; if its raw assignment is already
in the exact-three pair, no residual for that label was generated.
Type-one and type-two labels generate no checkerboard residual in this
count.

Hence raw and residual assignments together use each of the pair's three
labels at most once.  If `b_H` residual assignments are absorbed by the
pairs, then

```text
a_H+b_H<=3*h,
b_H<=3*h-a_H.                                    (4)
```

Let `Y` be the number of genuinely new residual circuits outside every
old pool.  Different residual labels can reuse one such circuit at most
three times.  From (2)--(4) and `a_H>=q_H`,

```text
3*Y
 >=k-b_H
 >=p_3-r_1-q_H-3*h+a_H
 >=p_3-delta-3*h.                                (5)
```

Equivalently,

```text
delta+3*h+3*Y>=p_3.                              (6)
```

No factor of two for the two members of an exact-three pair is available:
both members have the same three-label set.

## 4. Scalar certificate

Let

```text
B=n_1+n_2+2*n_3
```

count the selected cover together with the distinct selected-type-three
companions.  The disjoint pools give

```text
Q>=B+r+2*h+Y.
```

Solving (1) for `r`,

```text
Q>=B+A/2+delta/2+h/2+Y.
```

Six times the last three terms is

```text
3*delta+3*h+6*Y
 >=delta+3*h+3*Y
 >=p_3,
```

where the first inequality uses `delta,Y>=0` and the second is (6).
Therefore

```text
Q>=B+A/2+p_3/6.                                  (7)
```

Multiplying by six gives the exact coefficient row

```text
6*Q
 >=9*n_1+6*n_2+12*n_3+6*p_2+4*p_3

 =4*(2*n_1+2*n_2+3*n_3+p_2+p_3)
  +n_1+2*(p_2-n_2)

 >=8*C.                                          (8)
```

Here the private-label row is at least `2C` and `p_2>=n_2`.
For `C=4158`, equation (8) is

```text
Q>=4*C/3=5544.                                   (9)
```

The exact replay and all three proof-B tests passed after the package
manifest was frozen.

## 5. Sharp arithmetic control and boundary

The relaxation row

```text
n_3=1386, p_3=4158, h=1386,
n_1=n_2=p_2=r=delta=Y=0
```

saturates every displayed scalar inequality and gives `Q=5544`.  It means
all 4,158 raw type-three assignments are packed three per exact-three
orbit pair.  This is an arithmetic null control, not a circuit cover.

Adding the 693 verified edge-isolated projective circuits yields

```text
5544+693=6237
```

projective short-circuit classes and the circuit-only consequence

```text
B_4+B_5+B_6+B_7+B_8+B_9>=12474.
```

Wave 188's verified `18018` bound on all short dual words remains
numerically stronger.
