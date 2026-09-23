# Wave 194 proof-B audit: doubled type-two residual and sharpened union capacity

```yaml
role: proof_b
date_utc: 2026-07-29T03:22:22Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Independent hostile audit of the proposed Wave194 type-two exact-three
  residual lemma, sharpened type-three-label-union capacity, and exact
  conditional certificate Q>=5C/3=6930.
inputs:
  attempts/wave193-aggregate-proof-b-audit/package-manifest.sha256: 64e65e5cccb25b9eae7fbdfc3e4f1780fa229270f9dda9c45711447a243427cc
  attempts/wave192-c4-cohomology-proof-b/package-manifest.sha256: 2b5280347f7440b181106daf724963b1969b1e4a6ccdb1d85521181dc6c89cea
  attempts/wave191-exact-three-residual-proof-a/package-manifest.sha256: a0e2697b7e826f5543c2e007a1428633e37fb54e9e8449e73a731a7291f468c4
  verification/wave190-residual-stability-verifier/package-manifest.sha256: 15686d17472fd60122072b3d679980d90d3cfe12fd87e5359344e52e216f1280
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
method: >-
  Exact support subtraction in the two endpoint translations of a
  canonical conic, center and dual-distance collision separation,
  private-label cover incidence, exact-cross-multiplicity capacity, and
  independent rational expansion of the proposed dual certificate.
command: >-
  python -B attempts/wave194-five-thirds-proof-b-audit/exact_check.py
  --verify attempts/wave194-five-thirds-proof-b-audit/exact-results.json;
  python -B -m unittest -v
  attempts/wave194-five-thirds-proof-b-audit/test_exact_check.py
outputs:
  - agents/2026-07-29-wave194-five-thirds-proof-b-audit.md
  - attempts/wave194-five-thirds-proof-b-audit/
limitations:
  - This is a proof-B audit, not verifier promotion.
  - The theorem is conditional on the frozen prism-free rank-11 endpoint.
  - The scalar equality row is an arithmetic null, not an asserted cover,
    code, graph, or circuit family.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain
    UNKNOWN.
```

## Verdict

`AUDIT_PASS`.

Both proposed refinements survive the hostile collision audit, and the
exact dual identity is correct.  Conditional on the frozen inputs,

```text
Q>=5C/3=6930,  C=4158.                           (1)
```

Adding the 693 edge-isolated projective circuits gives at least 7,623
projective short circuits and

```text
B_4+...+B_9>=15246
```

from circuits alone.  The verified Wave188 value `18018`, which includes
nonminimal short words, remains numerically stronger.

## 1. Frozen split

Use the Wave193 raw split

```text
a1+a2+a3=n1,
b1+b3=2p2,
c1+c2=p3,
r1=a1+b1+c1.                                    (2)
```

The raw exact-two and exact-three capacities are

```text
SE2:=2r2-a2-c2>=0,
SE3:=3h-a3-b3>=0.                               (3)
```

Split the genuinely new non-exact-two continuation pool as

```text
Y=y+2g,
```

where `y` counts exact-one circuits and `g` counts complete exact-three
companion pairs.

## 2. Type-two exact-three raw forces a residual

Fix a private nonedge `e=xy` of a selected type-two checkerboard conic.
Its two raw parents have profiles

```text
tau_x: 6+2,
tau_y: 2+6.
```

Suppose an extracted raw `D_x` in `tau_x` is exact three.  Its center is
`x`, and its unique leaf block is one of the two `y`-side conic blocks.
The two companion members use complementary subsets of the full `x`-star.
Because `D_x` is contained in `tau_x`, it avoids the unique `x`-side conic
coordinate omitted by `tau_x`; its companion therefore uses that omitted
coordinate and is not contained in the parent.

Scale `D_x` to cancel its unique leaf block in

```text
tau_x-lambda*D_x.
```

The difference is nonzero because the other `y`-side conic block remains.
It is supported inside the proper `6+2` parent and now has only one
`y`-side block.  A minimal circuit in it therefore crosses `e`.  It is
distinct from:

- `D_x`, because its leaf block was cancelled;
- the companion, because the companion uses the omitted `x`-side conic
  coordinate; and
- the selected conic, because that conic also uses the omitted coordinate.

Wave181 exact-two uniqueness consequently makes the residual exact one or
exact three.  The `tau_y` case is symmetric.

### Same-label double-residual collision

The two type-two raws for one private label can both be exact three, so the
factor two on `b3` needs a separate check.

An exact-three residual from `tau_x` has center `x`, because its `y` side
has one block.  An exact-three residual from `tau_y` has center `y`.
They cannot be equal.

If both residuals were the same exact-one circuit, its support would be
contained in

```text
supp(tau_x) intersect supp(tau_y).
```

The two parents retain opposite single conic coordinates on their
translated sides.  Their intersection consists of exactly one `x`-side
and one `y`-side conic coordinate, hence has size two.  This contradicts
the verified dual distance at least four.

Thus the two residuals are distinct.  Neither can use the companion pair
of the opposite raw because those pairs have opposite centers.  Hence each
`b3` incidence genuinely supplies both its companion continuation and a
separate residual continuation.

## 3. Strengthened residual capacity

There is one continuation demand for each `a2,a3,c2` incidence and two for
each `b3` incidence:

```text
a2+a3+2b3+c2.                                    (4)
```

Old exact-three pairs have three distinct pair-label slots.  The preceding
same-label audit prevents two demands from one type-two private label from
silently occupying one slot.  A new pool with `y` exact-one circuits and
`g` exact-three pairs has capacity `y+3g`.  Therefore

```text
RA:=3h+y+3g-(a2+a3+2b3+c2)>=0.                  (5)
```

Privacy, omitted-coordinate separation, and orbit closure give the same
pool disjointness as Waves190--193.

## 4. Joint capacity on the type-three label union

Let `U` be the set of labels covered by selected type-three circuits.
Let `k` count the selected type-two label incidences that lie in `U`.
A selected type-one contributes none because its sole label is private.
A selected type-two has at least one private label, so `k<=n2`.

Labels outside `U` are covered by the remaining selected type-one/type-two
incidences, so

```text
C-|U|<=n1+2n2-k.                                 (6)
```

Choose one local `3+6` leaf target per `e in U`.  The privacy-free
Wave191 lemma makes every chosen target exact one or two.

The previous selected/raw capacities sharpen as follows.

1. A selected type-one circuit contributes zero.
2. Selected type-two circuits contribute at most the same `k` incidences
   already removed in (6).
3. An exact-one raw of type `a1` or `b1` crosses its source private label,
   which is outside `U`.  Only type-three exact-one raws `c1` can absorb a
   chosen `U` target.
4. Raw exact-two circuits contribute at most `2r2`; only the `y`
   exact-one members of the new residual pool can be low targets; and new
   low circuits `W` contribute at most `2W`.

Consequently

```text
|U|<=k+c1+2r2+y+2W.                              (7)
```

Combining (6)--(7),

```text
SL:=n1+2n2+c1+2r2+y+2W-C>=0.                    (8)
```

Every omitted pool in (7) consists of exact-three circuits, so the
collision list is exhaustive by exact multiplicity.  This is stronger
than the separately relaxed row with coefficient `3n2`.

## 5. Exact coefficient certificate

Let

```text
SI=I-2C,
S2=p2-n2,
Q0=n1+n2+2n3+r1+r2+2h+y+2g+W.
```

The selected, companion, raw, residual, and new-low pools counted by `Q0`
are disjoint, so `Q>=Q0`.

Using (2), exact expansion gives

```text
Q0-5C/3

=2SI/3
 +S2
 +2RA/3
 +SL/3
 +a1/3
 +b1/6
 +b3/2
 +r2/3
 +W/3.                                           (9)
```

Every term is nonnegative.  No `p3-n3` slack is required.  Equation (9)
proves (1).

The scalar inequalities have the exact null row

```text
n3=C/3=1386,
p3=c1=r1=C=4158,
all other split and pool variables zero.
```

It describes selected triple label sets partitioning all nonedges and one
exact-one leaf circuit per label.  It is an arithmetic control only.  At
one selected flag, differences of its three leaf words reduce to adjacent
outer-star relations, so the first local circuit-elimination test produces
the already counted edge-circuit sector rather than a contradiction.

## Boundary

```text
type-two residual lemma:          pass
same-label doubled b3 audit:      pass
joint U-capacity with k:          pass
exact five-thirds certificate:    pass
conditional Q lower bound:        6930
independent verifier promotion:   pending
rank 11 / endpoint excluded:      no
Conway-99 / external novelty:     UNKNOWN
```
