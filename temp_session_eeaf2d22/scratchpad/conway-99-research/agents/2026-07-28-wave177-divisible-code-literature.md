# Wave 177 literature report: divisible-code theorems do not cover the cap

```yaml
role: literature
date_utc: 2026-07-28T22:30:57Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: CITED
scope: >-
  Applicability audit of projective divisible-code theorems to the
  conditional self-orthogonal ternary [231,11] cap with dual distance at
  least four, singular columns, zero frame, and distinguished weight-198
  words.
inputs:
  - https://arxiv.org/abs/1912.10147
  - https://arxiv.org/abs/2112.11763
  - https://arxiv.org/abs/2311.11634
method: >-
  Matched field, divisor, length, dimension, projectivity, dual-distance,
  cap, and self-duality hypotheses against the frozen endpoint parameters.
command: n/a
outputs: []
limitations:
  - The source pass is targeted, not exhaustive.
  - Exact existence or nonexistence remains UNKNOWN.
  - No cited theorem combines all endpoint hypotheses.
```

## Applicable terminology

Over `F_3`,

```text
wt(c)=c dot c mod 3.
```

Thus a ternary linear code is 3-divisible exactly when it is
self-orthogonal; polarization supplies mutual orthogonality.  Li--Heng
record the same equivalence.  Heinlein--Honold--Kiermaier--Kurz--Wassermann
identify projective 3-divisible codes with 3-divisible point sets.

Here “projective” means dual distance at least three.  Wave 174 supplies the
stronger cap condition `d^perp>=4`.

## Why the length theorems do not exclude 231

The principal divisible-code results classify or constrain possible
lengths, usually without fixed dimension, cap, singular-quadric,
zero-frame, or distinguished-word conditions.  Length 231 is arithmetically
ordinary for `q=3,r=1`; for example

```text
231=51*4+3*9.
```

The corresponding standard juxtaposed constructions are not caps and need
not have dimension 11.  This calculation shows only that length
classification cannot exclude the target.

Ward's coprime replication theorem assumes `gcd(Delta,q)=1`, which fails for
`Delta=q=3`.  Gleason--Pierce--Ward concerns self-dual or half-dimensional
divisible codes; here `k=11` while `n/2=115.5`.  The 231 distinguished
scalar pairs of weight 198 do not make the minimum distance 198, so a
Griesmer substitution with `d=198` would also be invalid.

## Boundary

No inspected theorem simultaneously uses:

```text
[231,11], d^perp>=4, singular columns in Q(10,3),
sum z_i tensor z_i=0, and 231 distinguished weight-198 scalar pairs.
```

The appropriate literature label is therefore `UNKNOWN`, not a claimed
classification or an exclusion.
