# Wave 192 proof A: equality-face circuit elimination

## Verdict

`DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

Under the frozen conditional prism-free rank-11 endpoint assumptions, the
number `Q` of projective short circuits cross-realizing graph nonedges
satisfies

```text
Q>=6238.
```

This is an analytic strict improvement of the independently verified
Wave191 theorem `Q>=6237`. It uses equality-slack reconstruction, the
canonical nonedge involution, affine circuit elimination in two star
modules, and the privacy-free local exact-three exclusion. It performs no
graph, code, cover, SAT, LP, configuration, enumeration, or isomorphism
search.

```yaml
role: proof_a
date_utc: 2026-07-29T03:07:32Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: reconstruct the complete
  equality face of verified Wave191 Q>=6237, sharpen residual orbit
  capacity using the impossibility of exact-two residuals, and exclude
  every equality branch by affine two-star circuit elimination and
  shared-label leaf translations, proving Q>=6238.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
  verification/wave188-affine-star-word-amplification-verifier/package-manifest.sha256: e58bd132b1e1579f5e4e6570d7e0b4318a6c5f970342d4b9493e0c35a3c0dc74
  verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256: fc17484bd8c32a5886ecdcc65d153903cef5f3b60a3de1c9905ed96697c273c4
  verification/wave191-exact-three-residual-verifier/package-manifest.sha256: a14f43310fb5ead05c4bd50b376f3d9d90ec77a92bc00f8c3b7326013f975ab2
method: >-
  Exact equality-slack audit; residual exact-two uniqueness exclusion;
  companion-closed capacity ratios; saturation of canonical-C4 label
  pairs; affine two-star circuit elimination; and shared-label leaf-word
  extraction. No graph, code, cover, SAT, LP, configuration, enumeration,
  or isomorphism search.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave192-equality-face-proof-a\exact_check.py --verify
  attempts\wave192-equality-face-proof-a\exact-results.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave192-equality-face-proof-a\test_exact_check.py
outputs:
  - agents/2026-07-29-wave192-equality-face-proof-a.md
  - attempts/wave192-equality-face-proof-a/
limitations:
  - This is a proof-agent derivation, not verifier promotion.
  - The theorem is conditional on the frozen prism-free rank-11 endpoint.
  - The one-unit improvement supplies no incompatible upper bound.
  - Rank 11, endpoint existence, strict improvement of the original graph
    parameter n3, external novelty, and Conway-99 remain UNKNOWN.
```

## 1. Wave191 equality slacks

Use the verified notation

```text
C=4158,
I=2*n1+2*n2+3*n3+p2+p3>=2*C,
A=n1+2*p2+p3,
B=n1+n2+2*n3,
delta=2*r+3*h-A.
```

The Wave191 certificate is

```text
Q>=B+A/2+delta/2+h/2+Y
 >=B+A/2+p2/3+p3/2,

12*Q
 >=9*I+6*(p2-n2)+p2+3*(p3-n3)
 >=18*C.                                         (1)
```

Assume for contradiction that `Q=3C/2=6237`. Equality in the coefficient
row forces

```text
I=2*C,
p2=n2=0,
p3=n3.                                           (2)
```

Write `m=n3=p3`. Then

```text
n1=C-2*m,
B=C,
A=C-m,
0<=m<=2079.                                      (3)
```

Let `r1` count exact-one circuits in the old low raw pool, let `t` count
type-three raw assignments on them, and put `u=r1-t`. Let `Z` count
residual-assignment incidence outside every old pool. Wave191 proves

```text
p3+u<=delta+Z,
2*p2<=u+3*h.                                     (4)
```

## 2. Residuals have capacity strictly below two per circuit

Wave191 independently records the following unused lever. If a type-three
raw is exact-two, Wave181 identifies it as the unique canonical
checkerboard circuit `r_e` through its label `e`. Its Wave190 residual
crosses `e` but omits coordinates of `r_e`. Therefore the residual cannot
be exact-two: uniqueness would force it to equal `r_e`.

Close every new exact-three residual under the companion involution. If the
closed new pool has `y` exact-one residual circuits and `g` exact-three
companion pairs, then

```text
Y=y+2*g,
Z<=y+3*g,
2*Z<=3*Y.                                        (5)
```

There are no exact-two residual assignments, so no other new-pool type
occurs.

Equality in (1)--(4) first gives

```text
h=0,
delta+2*Y=p3,
u=0.                                             (6)
```

Using (5) instead of the weaker `Z<=2Y`, the same penalty satisfies

```text
delta/2+h/2+Y

 >=(2*delta+3*Y)/6
  +(2*delta+6*h+3*Y)/12
  +Y/4

 >=p2/3+p3/2+Y/4.                                (7)
```

Thus equality in (1) forces

```text
Y=0.                                             (8)
```

Now (4), (6), and the fact that an old exact-two residual is also excluded
show

```text
Z=0,
t=r1=p3=m,
delta=m,
r=2079.                                          (9)
```

Indeed, every type-three raw not on an exact-one circuit would force a
residual that cannot be absorbed by an old low circuit, while `h=Y=0`.

The complete scalar equality face is therefore

```text
n1=C-2*m, n2=p2=0, n3=p3=m,
r=2079, r1=t=delta=m,
h=u=Y=Z=0,
0<=m<=2079.                                     (10)
```

This is already much smaller than the weak arithmetic null row displayed
in the Wave191 source report.

## 3. Canonical involution on the type-one labels

On (10), all `m` type-three private leaf raws are exact-one. The remaining

```text
r-r1=2079-m
```

raw circuits are exact-two. There are

```text
n1=C-2*m=2*(2079-m)
```

type-one raw assignments, and they saturate those exact-two circuits at two
distinct labels apiece.

Wave181 associates every nonedge `e` with its opposite common-neighbor
nonedge `tau(e)`. The unique exact-two circuit through `e`, if dependent,
is the canonical four-block circuit with label set

```text
{e,tau(e)}.
```

Consequently the set `L1` of type-one labels is `tau`-invariant and
partitions into exactly `2079-m` canonical pairs. No equality-face
exact-two circuit crosses a label outside `L1`.

## 4. The all-type-one endpoint is impossible

First suppose `m=0`. Every nonedge is the private label of one selected
exact-one circuit `C_e`, and every canonical quadrilateral is a raw
exact-two circuit `R_e`.

Apply the verified Wave187 majority translation to `C_e`. It produces a
short true relation `W_e` on two proper endpoint-star subsets, and the raw
circuit extracted inside it must be `R_e` by equality and Wave181
uniqueness.

If `R_e` were a proper subcircuit of `W_e`, subtracting a scalar multiple
of its relation would leave a nonzero relation on the same two proper star
subsets. A minimal circuit in the difference would cross `e`. It would be
neither:

- `C_e`, because the majority translation canceled a coordinate of
  `C_e`; nor
- `R_e`, because the subtraction canceled a coordinate of `R_e`.

No other equality-face circuit crosses the private label `e`. Hence this
would be an extra circuit, contradicting `Q=6237`. Therefore

```text
W_e=R_e projectively.                            (11)
```

Relative to `e`, normalize the canonical checkerboard word as

```text
R_e=(1,2,0,0,0,0,0 | 2,1,0,0,0,0,0).
```

The two nonzero translations along the endpoint used in (11) have profiles
`6+2` and supports omitting opposite canonical coordinates. One is
`C_e`. The other, call it `C'_e`, is another true weight-eight relation.
Its support contains neither `C_e` nor `R_e`. Since both star sides are
proper, `C'_e` contains a circuit crossing `e`, necessarily new. This
again contradicts equality.

Thus

```text
m=0 is impossible.                              (12)
```

## 5. Every branch with a type-three circuit is impossible

Now suppose `m>0`. Minimality gives at least one private label to every
selected circuit. Since `p3=n3=m`, every selected type-three circuit has
exactly one private label and two nonprivate label incidences.

There are

```text
n1+p3=C-m
```

private labels in total, so exactly `m` labels are nonprivate. The selected
cover has `2m` incidences on them. Since a nonprivate label has selected
degree at least two, every such label has degree exactly two.

Choose one nonprivate label `f` on any selected type-three flag. Construct
its `3+6` leaf relation exactly as for a private leaf. This relation has
two proper star sides and therefore contains a circuit crossing `f`.

The Wave191 local exact-three exclusion uses only the flag geometry,
proper-star independence, and the canonical Gram kernel; privacy is not
used. Hence the extracted circuit has exact multiplicity one or two.

- It cannot be exact-one within the equality pool: every equality-face
  exact-one circuit has a private label, while `f` is nonprivate.
- It cannot be exact-two within the equality pool: all exact-two circuits
  are the saturated canonical pairs on the `tau`-invariant type-one set
  `L1`, while `f` is not a type-one label.

Thus the leaf relation contains a new circuit outside every pool counted by
`Q=6237`, a contradiction. Therefore

```text
m>0 is impossible.                              (13)
```

Equations (12)--(13) exclude the entire equality face (10). Since `Q` is an
integer,

```text
Q>=6238.                                         (14)
```

Adding the 693 verified edge-isolated projective circuits gives at least

```text
6931
```

projective short-circuit classes and the circuit-specific scalar
consequence

```text
B4+B5+B6+B7+B8+B9>=13862.
```

Wave188's verified `18018` bound for all short dual words remains
numerically stronger because it also counts nonminimal words.

## Boundary

```text
conditional Q>=6237 theorem:        VERIFIED
Q=6237 equality face:               analytically excluded
conditional Q>=6238 theorem:        DERIVED
independent verification of 6238:   pending
rank 11 / endpoint excluded:        no
strict original n3 improvement:     no
Conway-99 / external novelty:       UNKNOWN
```
