# Wave 193 proof-B audit: aggregate low-target certificate

```yaml
role: proof_b
date_utc: 2026-07-29T03:16:03Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Independent adversarial audit of the Wave193 aggregate raw/residual and
  type-three-union low-target scheme, including collision separation and
  the exact dual certificate Q>=ceil(59C/39)=6291.
inputs:
  attempts/wave192-c4-cohomology-proof-b/package-manifest.sha256: 2b5280347f7440b181106daf724963b1969b1e4a6ccdb1d85521181dc6c89cea
  attempts/wave191-exact-three-residual-proof-a/package-manifest.sha256: a0e2697b7e826f5543c2e007a1428633e37fb54e9e8449e73a731a7291f468c4
  verification/wave190-residual-stability-verifier/package-manifest.sha256: 15686d17472fd60122072b3d679980d90d3cfe12fd87e5359344e52e216f1280
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
method: >-
  Clean algebraic expansion of the proposed rational dual certificate;
  independent circuit-support audit of type-one exact-two continuations;
  exact-three orbit label capacity; and an exhaustive-by-type, not
  exhaustive-by-configuration, collision partition for the union of labels
  covered by selected type-three circuits.
command: >-
  python -B attempts/wave193-aggregate-proof-b-audit/exact_check.py --verify
  attempts/wave193-aggregate-proof-b-audit/exact-results.json;
  python -B -m unittest -v
  attempts/wave193-aggregate-proof-b-audit/test_exact_check.py
outputs:
  - agents/2026-07-29-wave193-aggregate-proof-b-audit.md
  - attempts/wave193-aggregate-proof-b-audit/
limitations:
  - This is an independent proof-B audit, not verifier promotion.
  - The theorem is conditional on the prism-free rank-11 endpoint and the
    frozen Wave181, Wave190, Wave191, and Wave192 inputs.
  - No actual cover, circuit family, code, or graph realizing the rational
    equality row is asserted.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain
    UNKNOWN.
```

## Verdict

`AUDIT_PASS`.

The proposed collision rows `SR` and `SL` are sound, and the rational
coefficient identity expands exactly.  Conditional on the frozen inputs,

```text
Q>=ceil(59*4158/39)=6291.                        (1)
```

Adding the 693 edge-isolated projective circuits gives at least 6,984
projective short circuits and the circuit-only scalar consequence

```text
B_4+...+B_9>=13968.
```

Wave188's independently verified `18018` all-short-word bound remains
larger because it includes nonminimal words.

## 1. Raw-type split

Split the raw assignment incidence by source type and target exact
cross-multiplicity:

```text
a1+a2+a3=n1,
b1+b3=2p2,
c1+c2=p3,
r1=a1+b1+c1.
```

Here type two has no exact-two raw because its selected owner is already
the unique exact-two conic through either private label.  Type three has
no exact-three raw by the Wave191 local lemma.

If `r2` is the number of raw exact-two circuits and `h` the number of
closed exact-three companion pairs, then

```text
a2+c2<=2r2,                                      (2)
a3+b3<=3h.                                       (3)
```

For (3), capacity is three labels per companion *pair*, not six
circuit-label incidences.  The two type-two translations for one private
label cannot be the two members of a single pair: their `6+2` and `2+6`
profiles force opposite centers, while companions share one center.

## 2. Audit of the residual row `SR`

There is one non-exact-two continuation demand for every incidence counted
by

```text
a2+a3+b3+c2.                                     (4)
```

- `a2`: if the type-one majority translate strictly contains its raw
  conic, subtract the conic and extract minimally; if it equals the conic,
  use the other signed `6+2` axis word from Wave192.
- `a3`: use the other member of the exact-three companion pair.
- `b3`: use the companion of that type-two raw.  Same-label type-two raws
  occupy different companion pairs by center orientation.
- `c2`: use the Wave190 checkerboard residual.

The `a2` continuation is short and cross-star because both sides of the
parent translate are proper.  It is not the selected type-one owner: in
the strict case the parent translate omits a selected-owner coordinate,
and in the equality case the two signs omit opposite conic coordinates.
It cannot be exact two, since the raw conic is the unique exact-two circuit
through the label.

All demands in (4) are keyed by private labels.  One old exact-three pair
can absorb at most its three distinct label slots.  The type-two
same-label double assignment cannot consume one pair twice.  If the
genuinely new closed continuation pool contains `y` exact-one circuits and
`g` exact-three pairs, then

```text
Y=y+2g,
continuation capacity<=y+3g<=3Y/2.
```

Privacy excludes the selected pools, exact-two uniqueness excludes the old
low conics, and orbit closure prevents a new mate from silently returning
to an old exact-three pair.  Therefore

```text
SR:=3h+3Y/2-(a2+a3+b3+c2)>=0.                    (5)
```

No residual is assumed distinct when it can legitimately reuse an unused
label slot of an old pair; that collision is exactly the `3h` term.

## 3. Audit of the aggregate low-target row `SL`

Let `U` be the union of labels covered by selected type-three circuits.
Every label outside `U` is covered by a selected type-one or type-two
circuit, so

```text
|U|>=C-(n1+2n2).                                 (6)
```

For each distinct `e in U`, choose one selected type-three flag containing
`e` and form its `3+6` leaf relation along `e`.  The Wave191 local
exact-three exclusion uses no privacy; after relabelling the chosen leaf,
every minimal circuit inside this relation has exact multiplicity one or
two.

Such a low target cannot equal a selected type-three circuit or companion,
nor an old raw exact-three circuit.  Its possible collisions are exhausted
by:

```text
selected low circuits:       n1+2n2 label slots,
raw low circuits:            r1+2r2 label slots,
exact-one members of Y:      at most Y label slots,
new low circuits W:          at most 2W label slots.
```

This is exhaustive because the omitted pools consist only of exact-three
circuits.  One target was selected per distinct label, so ordinary exact
cross-multiplicity is precisely the needed reuse capacity.  Thus

```text
|U|<=n1+2n2+r1+2r2+Y+2W.                        (7)
```

Combining (6)--(7),

```text
SL:=2n1+4n2+r1+2r2+Y+2W-C>=0.                   (8)
```

## 4. Disjoint circuit pools

The counted circuit total is

```text
Q0=n1+n2+2n3+r1+r2+2h+Y+W.                      (9)
```

The first five terms are the selected cover, selected type-three mates,
and orbit-closed raw pool.  `Y` is defined outside all those pools.
`W` contains only the remaining low targets after collisions with selected
low circuits, raw low circuits, and exact-one members of `Y` have been
removed.  It cannot collide with an omitted exact-three pool because every
member of `W` has exact multiplicity at most two.  Hence the pools in (9)
are disjoint and `Q>=Q0`.

## 5. Exact dual certificate

Put

```text
SI = I-2C,
S2 = p2-n2,
S3 = p3-n3,
SE2=2r2-a2-c2,
SE3=3h-a3-b3.
```

All named slacks are nonnegative.  Direct rational expansion using the four
raw-split identities gives

```text
Q0-59C/39

=29SI/39
 +23S2/39
 +3S3/13
 +38SE2/117
 +2SE3/117
 +76SR/117
 +SL/39
 +17(a1+a2)/39
 +5a3/39
 +4b1/13
 +35r2/117
 +37W/39.                                       (10)
```

Every coefficient is nonnegative.  Therefore `Q>=Q0>=59C/39`, and
integrality gives (1).

The simultaneous zero-slack row is only rational:

```text
n2=p2=2C/13,
n3=p3=5C/13,
h=2p2/3,
r1=n3,
r2=Y=W=n1=0.
```

For `C=4158`, `59C/39=81774/13`, so it does not itself define an integer
cover.

## Boundary

```text
aggregate certificate:             exact
SR collision audit:                pass
SL collision audit:                pass
conditional Q lower bound:         6291
independent verifier promotion:     pending
rank 11 / endpoint excluded:        no
Conway-99 / external novelty:       UNKNOWN
```

