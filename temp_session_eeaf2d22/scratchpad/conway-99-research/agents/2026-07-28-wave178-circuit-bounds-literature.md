# Wave 178--179 circuit-bound literature audit

## Verdict

`CITED`, with endpoint status `UNKNOWN`.

The verified circuit supply is genuine:

```text
693 distinct balanced edge circuits of sizes 4,6,8,
2079 distinct projective circuits of sizes 4..9,
B_4+...+B_9>=4158.
```

The checked primary theorem families do not exclude these parameters.

## Locally recoverable codes

Every short word of `W^perp` is a parity check for `W`, but standard
all-symbol locality requires a short check through every coordinate.
Availability bounds require several pairwise-disjoint recovery sets at
every coordinate.  The global circuit count supplies neither minimum
coordinate coverage nor disjoint availability.

Even if all-symbol locality `r=7` were granted, the Tamo--Barg
Singleton-type substitution gives only

```text
d(W) <= 231-11-ceil(11/7)+2 = 220,
```

while the 99 distinguished primal words already have weight 198.  The
bound is therefore slack.  Applying it to `W^perp` would reverse the code
side: locality there would require short words in `W`.

Primary sources:

- Itzhak Tamo and Alexander Barg,
  [*Bounds on Locally Recoverable Codes with Multiple Recovering Sets*](https://arxiv.org/abs/1402.0916).
- N. Prakash, Govinda M. Kamath, V. Lalitha, and P. Vijay Kumar,
  [*Optimal Linear Codes with a Local-Error-Correction Property*](https://arxiv.org/abs/1202.2414).

## Critical exponent and subspace intersections

The Crapo--Rota critical exponent concerns a primal full-coordinate-support
subcode or equivalent characteristic-polynomial data.  Short isolated words
of `W^perp` do not supply that input.

The 99 star spaces are six-spaces in an 11-space, so nontrivial pairwise
intersection is automatic.  Hsieh's sharp vector-space EKR regime for
`q>=3` requires `n>=2k+1`; here `11<13`.  Moreover only graph edges have
the stronger cycle-dependent intersection data.  Equidistant/sunflower
theorems require constant intersection dimension, extremal cardinality, or
large-field hypotheses absent here.

Primary sources:

- Gianira N. Alfarano and Eimear Byrne,
  [*The Critical Theorem for q-Polymatroids*](https://arxiv.org/abs/2305.07567).
- W. N. Hsieh,
  [*Intersection theorems for systems of finite vector spaces*](https://doi.org/10.1016/0012-365X(75)90091-6).
- Tuvi Etzion and Netanel Raviv,
  [*Equidistant Codes in the Grassmannian*](https://arxiv.org/abs/1308.6231).
- Elisa Gorla and Alberto Ravagnani,
  [*Equidistant subspace codes*](https://arxiv.org/abs/1507.01728).

## Circuit-count scale and hostile control

A direct cap ceiling already allows up to

```text
floor(binomial(231,3)/4)=506948
```

four-circuit supports, far above 2,079.

More sharply, the rank-11 ternary graphic matroid of `K_(6,6)` has girth
four and, with every edge oriented from one bipartition class to the other,
has balanced signed cycles:

```text
225 four-circuits,
2400 six-circuits,
2625 balanced short circuits total.
```

Its length and distinguished geometry differ from the target, so it is not
an endpoint model.  It is a hostile control showing that rank 11,
projectivity, dual distance four, and raw balanced short-circuit abundance
cannot alone contradict the Wave 179 count.

## Missing bridge

A usable exclusion must exploit information discarded by ordinary matroid
or LRC bounds, for example:

1. per-coordinate disjoint circuit availability;
2. a signed-circuit intersection theorem using exact two-star balance;
3. a complete-weight upper bound below `B_4+...+B_9=4158`; or
4. the 99 distinguished seven-star spaces and exact triangle
   cross-realization geometry.

```yaml
role: literature
date_utc: 2026-07-28T23:55:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: CITED
scope: >-
  Applicability of LRC, critical-exponent, vector-space EKR, sunflower,
  equidistant-subspace, and ordinary circuit-count bounds to the verified
  Wave178--179 short-circuit supply.
inputs:
  - attempts/wave178-edge-circuit-injection/package-manifest.sha256
  - verification/wave178-edge-circuit-injection/package-manifest.sha256
  - attempts/wave179-global-transversal-circuits/package-manifest.sha256
  - verification/wave179-global-transversal-circuits/package-manifest.sha256
method: >-
  Exact hypothesis matching and direct parameter substitution against
  primary sources, plus a rank-11 graphic-matroid hostile control.
command: >-
  python -c "import math; print(math.comb(231,3)//4,
  math.comb(6,2)**2, math.comb(6,3)**2*6)"
outputs:
  - agents/2026-07-28-wave178-circuit-bounds-literature.md
limitations:
  - No checked theorem consumes the simultaneous signed balance,
    unique-edge localization, and 99 star spaces.
  - The endpoint and rank-11 branch remain UNKNOWN.
  - External novelty is UNKNOWN.
```
