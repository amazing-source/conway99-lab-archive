# Independent Wave 190 residual-stability audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Under the frozen prism-free rank-11 endpoint assumptions, the number `Q` of
projective short circuits cross-realizing graph nonedges satisfies

```text
Q>=5544.
```

This is a conditional circuit theorem. It is not a graph, cover, code, or
endpoint construction and does not resolve Conway-99.

## Integrity and clean-room separation

The source package manifest has SHA-256
`e66987333e3f7119026520be9680699bcfdcfcddbf8877016d8d817193684a5a`;
all nine listed entries match. The sealed Wave189 verifier manifest has
SHA-256
`fc17484bd8c32a5886ecdcc65d153903cef5f3b60a3de1c9905ed96697c273c4`;
all eight entries match. Both proof-agent accounts and all five direct
inputs match their frozen hashes.

The clean-room checker imported and executed no discovery code. The
independent result was fixed before source replay, with payload SHA-256
`f70b5e28d22a0e4caf48cb7285289420abf84b38b0e1dd75c02fc1ab9d0ec832`.

## 1. Exact-one slack

Retain the Wave189 orbit-closed extraction pool:

```text
A=n1+2*p2+p3
|X|=r+2*h
delta=2*r+3*h-A>=0.
```

If `r1` low circuits have exact cross-multiplicity one, actual assignment
capacity is

```text
A<=r1+2*(r-r1)+3*h=2*r-r1+3*h.
```

Subtracting this from the definition of `delta` gives

```text
r1<=delta.
```

No assignment is counted twice for one circuit-label pair: type-two's two
raw circuits are distinct, while types one and three supply only one raw
assignment per private label.

## 2. Which type-three assignments force residuals

Let `aH` count all raw assignments absorbed by the `h` exact-three companion
pairs and `qH` its type-three part. At most `r1` of the `p3` type-three leaf
assignments land on exact-one circuits. Therefore at least

```text
k>=p3-r1-qH
```

land on exact-two circuits.

For each such private label `e`, Wave181 uniqueness identifies the raw
circuit as the canonical checkerboard conic `r_e` inside the all-two `3+6`
leaf relation `w_e`. Either difference `w_e-r_e` or `w_e-2*r_e` is a true
weight-seven `2+5` relation. A minimal circuit in its support crosses `e`
and omits coordinates of `r_e`.

## 3. Complete collision audit

A residual cannot collide with the low part of the raw pool:

- an exact-one residual equaling a raw circuit assigned to another label
  would cross two labels;
- its only raw assignment for the same type-three label is `r_e`; and
- an exact-two residual would, by Wave181 uniqueness, have to equal `r_e`,
  whose omitted coordinates prevent containment.

Privacy excludes the selected cover and selected-type-three companion pool.
Thus an old circuit can absorb a residual only in one of the `h` exact-three
orbits.

For one fixed label, raw and residual use of such an orbit are mutually
exclusive:

- type-one and type-two labels produce no residual in this count;
- a type-three residual exists only when its raw leaf assignment landed on
  an exact-two conic, not in the exact-three orbit; and
- the two type-two raw extractions cannot be the two orbit mates, because
  their `6+2` and `2+6` supports force different centers while companions
  share a center.

Each orbit has only three labels. Hence, if `bH` residual assignments are
absorbed by old exact-three orbits,

```text
aH+bH<=3*h.
```

This bound is three per *pair*, not six: both companion members have the
same three-label set.

## 4. Residual stability as an exact slack identity

Let `Y` count genuinely new residual circuits. Capacity three gives

```text
3Y>=k-bH.
```

The master inequality is the sum of five independently nonnegative slacks:

```text
(3Y-k+bH)
+(k-p3+r1+qH)
+(delta-r1)
+(aH-qH)
+(3h-aH-bH)

=delta+3h+3Y-p3.
```

Therefore

```text
delta+3h+3Y>=p3.
```

This identity retains every collision allowed by exact cross-multiplicity.
It is the key point that closes the preliminary raw-versus-residual
overcounting risk.

## 5. The `6Q>=8C` coefficient certificate

Write

```text
B=n1+n2+2*n3.
```

The selected cover, selected triple companions, closed extraction pool, and
new residual pool are disjoint:

```text
Q>=B+r+2h+Y.
```

Using `2r+3h=A+delta`,

```text
Q>=B+A/2+delta/2+h/2+Y.
```

The residual master row plus nonnegativity of `delta,Y` gives

```text
3delta+3h+6Y>=p3,
Q>=B+A/2+p3/6.
```

Multiplying by six yields the exact coefficient row

```text
6Q
>=9*n1+6*n2+12*n3+6*p2+4*p3

=4*(2*n1+2*n2+3*n3+p2+p3)
 +n1+2*(p2-n2).
```

The private-incidence row is at least `2C`, minimality gives `p2>=n2`, and
`n1>=0`. Hence

```text
6Q>=8C.
```

For `C=4158`,

```text
Q>=4*C/3=5544.
```

## 6. Sharp arithmetic control

The row

```text
n3=1386, p3=4158, h=1386,
n1=n2=p2=r=delta=Y=0
```

saturates all displayed scalar inequalities. All 4,158 raw type-three
assignments are charged three per exact-three orbit; no checkerboard residual
is generated. This is an arithmetic null control only. No cover or graph
realizing it is asserted.

## Consequence and boundary

Adding 693 verified edge-isolated projective circuits gives

```text
all projective short circuits>=6237,
scalar short-circuit words>=12474.
```

Wave188's verified `18018` lower bound on all short dual words remains
numerically stronger because it includes nonminimal words.

```text
conditional residual-stability theorem: VERIFIED
sharp arithmetic row realized:          not claimed
rank 11 excluded:                       no
endpoint excluded:                      no
strict n3 improvement:                  no
Conway-99 / external novelty:           UNKNOWN
```

## Reproducibility

After the independent result was frozen:

```text
independent verifier replay: PASS
independent tests:            6/6 PASS
source tests:                 3/3 PASS
source manifest:              PASS
```

No graph, cover, code, SAT, configuration, LP, isomorphism, or enumeration
search was used.
