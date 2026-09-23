# Wave 193 proof A: global low-target and residual flow

## Verdict

`DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

Under the frozen conditional prism-free rank-11 endpoint assumptions, the
number `Q` of projective short circuits cross-realizing graph nonedges
satisfies

```text
Q>=6291.
```

The proof combines two matroidal flows:

1. exact-two raw circuits from selected type-one and type-three sources
   force exact-one/exact-three residuals; and
2. every label used by a selected type-three circuit has a privacy-free
   leaf word forcing a low exact-one/exact-two target.

An exact nonnegative dual certificate gives `117Q>=177C`. No graph, code,
cover, SAT, LP, configuration, enumeration, or isomorphism search is used
in the proof.

```yaml
role: proof_a
date_utc: 2026-07-29T03:14:28Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: refine the orbit-closed raw pool
  by source and exact multiplicity; force residuals from exact-two type-one
  and type-three raws; combine this with one privacy-free low leaf target
  for every label used by a selected type-three circuit; and certify
  117Q>=177C, hence Q>=6291.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
  verification/wave188-affine-star-word-amplification-verifier/package-manifest.sha256: e58bd132b1e1579f5e4e6570d7e0b4318a6c5f970342d4b9493e0c35a3c0dc74
  verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256: fc17484bd8c32a5886ecdcc65d153903cef5f3b60a3de1c9905ed96697c273c4
  verification/wave191-exact-three-residual-verifier/package-manifest.sha256: a14f43310fb5ead05c4bd50b376f3d9d90ec77a92bc00f8c3b7326013f975ab2
method: >-
  Ternary affine circuit elimination, Wave181 exact-two uniqueness,
  companion-closed assignment capacity, a privacy-free type-three
  label-union cover by low circuits, and an exact rational dual
  certificate. No graph, code, cover, SAT, LP, configuration, enumeration,
  or isomorphism search.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave193-global-low-target-proof-a\exact_check.py --verify
  attempts\wave193-global-low-target-proof-a\exact-results.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave193-global-low-target-proof-a\test_exact_check.py
outputs:
  - agents/2026-07-29-wave193-global-low-target-proof-a.md
  - attempts/wave193-global-low-target-proof-a/
limitations:
  - This is a proof-agent derivation, not verifier promotion.
  - The theorem is conditional on the frozen prism-free rank-11 endpoint.
  - The displayed Q=6291 row is only an arithmetic null control.
  - The bound supplies no incompatible upper bound.
  - Rank 11, endpoint existence, strict original n3 improvement, external
    novelty, and Conway-99 remain UNKNOWN.
```

## 1. Raw assignments by source and multiplicity

Retain the selected-cover counts `n_i`, private-label counts `p_i`, and

```text
C=4158,
I=2*n1+2*n2+3*n3+p2+p3>=2*C,
p2>=n2,
p3>=n3.
```

Split raw assignment incidence by selected source type and exact
cross-multiplicity:

```text
a1+a2+a3=n1,       type-one raws;
b1+b3=2*p2,        type-two raws;
c1+c2=p3,          type-three raws.              (1)
```

There is no `b2`: a selected type-two circuit is already the unique
Wave181 exact-two circuit through each private label, while both outside
raw translates are distinct from it. There is no `c3`: Wave191 refutes
every exact-three type-three leaf extraction.

Close the old raw pool under exact-three companionship. Let

```text
r1 = number of exact-one raw circuits,
r2 = number of exact-two raw circuits,
h  = number of exact-three companion pairs.
```

Every exact-one raw circuit receives exactly one raw assignment, while the
other capacities give

```text
r1=a1+b1+c1,
a2+c2<=2*r2,
a3+b3<=3*h.                                      (2)
```

The selected cover, selected type-three companions, and closed raw pool are
pairwise disjoint by the verified Wave189 separation audit.

## 2. Exact-two type-one raws force residuals

Fix a selected type-one circuit with private label `e`, and let `W_e` be a
short majority-translated relation from Wave187. Suppose its raw circuit is
the exact-two canonical conic `R_e`.

If `R_e` is a proper subcircuit of `W_e`, subtract a scalar multiple of its
relation to cancel one conic coordinate. The difference is a nonzero
relation on two proper endpoint-star subsets, hence contains a circuit
crossing `e`. It is not the selected owner, because the majority
translation canceled an owner coordinate, and it is not `R_e`, because the
subtraction canceled a conic coordinate.

If `W_e=R_e` projectively, the selected owner is one of the two nonzero
axis translations of the checkerboard conic. The other axis word has
profile `6+2`, weight eight, and contains neither the selected owner nor
the conic. A circuit inside it again crosses `e` and is new.

In both cases an exact-two residual would have to equal `R_e` by Wave181
uniqueness, which its support excludes. Therefore every `a2` assignment
forces a residual assignment of exact multiplicity one or three.

The verified Wave190 subtraction gives the same conclusion for every `c2`
type-three assignment. Hence

```text
a2+c2
```

residual assignments are forced.

## 3. Residual flow through exact-three raw pairs

An old exact-three raw pair has one common three-label set. The raw
assignments `a3+b3` occupy distinct label slots:

- type-one private labels occur once;
- distinct selected owners have distinct private labels; and
- the two type-two translates for one label cannot be companion mates.

Thus old pairs have at most

```text
3*h-a3-b3
```

slots available for the forced residuals. Residuals not absorbed there
have incidence at least

```text
a2+c2-(3*h-a3-b3)
 =a2+a3+b3+c2-3*h.                               (3)
```

No residual can enter an old low circuit: exact-one multiplicity and
privacy exclude a different label, while exact-two uniqueness excludes the
source label.

Close every genuinely new exact-three residual under companionship. Let
`Y` be the number of circuits in this closed new pool. Its members are:

- exact-one circuits, with one residual-label slot per circuit; and
- exact-three pairs, with three slots per two circuits.

Its assignment capacity is therefore at most `3Y/2`. Define the
nonnegative residual slack

```text
S_R
 =3*h+(3/2)*Y-(a2+a3+b3+c2)
 >=0.                                             (4)
```

Orbit closure and privacy keep the new pool disjoint from the selected,
selected-companion, and old raw pools.

## 4. Every selected-type-three label has a low target

Let `U` be the set of nonedge labels appearing in at least one selected
type-three circuit. A label outside `U` must be covered by a selected
type-one or type-two circuit. Hence

```text
|U|>=C-(n1+2*n2).                                (5)
```

For each `e in U`, choose one selected type-three flag containing `e` and
form its `3+6` leaf relation. Its two star sides are proper, so it contains
a circuit crossing `e`. The Wave191 exact-three exclusion is local and
does not use privacy. Thus the chosen target has exact multiplicity one or
two.

Choose only one target per label. The already counted low-label capacity
is:

```text
selected low circuits:   n1+2*n2,
old raw low circuits:    r1+2*r2,
new residual pool:       at most Y.
```

The last term is `Y`, not `2Y`: exact-three residual pairs cannot be low
leaf targets, and only the exact-one part of that pool contributes.

Let `W` count all additional low circuits required by these targets. They
have capacity at most two labels each. Combining with (5),

```text
C<=2*n1+4*n2+r1+2*r2+Y+2*W.                     (6)
```

The `W` pool is, by definition, disjoint from every previously counted
pool.

## 5. Exact nonnegative coefficient certificate

The disjoint circuit pools give

```text
Q>=Q0,

Q0=n1+n2+2*n3+r1+r2+2*h+Y+W.                    (7)
```

Define the nonnegative slacks

```text
S_I =I-2*C,
S_2 =p2-n2,
S_3 =p3-n3,
S_E2=2*r2-a2-c2,
S_E3=3*h-a3-b3,
S_L =2*n1+4*n2+r1+2*r2+Y+2*W-C.
```

Using the exact identities (1)--(2), direct expansion gives

```text
Q0-59*C/39

 =(29/39)*S_I
  +(23/39)*S_2
  +(3/13)*S_3
  +(38/117)*S_E2
  +(2/117)*S_E3
  +(76/117)*S_R
  +(1/39)*S_L
  +(17/39)*(a1+a2)
  +(5/39)*a3
  +(4/13)*b1
  +(35/117)*r2
  +(37/39)*W.                                    (8)
```

Every term on the right is nonnegative. Therefore

```text
117*Q>=177*C,
Q>=ceil(59*C/39).                                (9)
```

For `C=4158`,

```text
59*C/39=6290+4/13,
Q>=6291.                                         (10)
```

Adding the 693 verified edge-isolated projective circuits gives at least

```text
6984
```

projective short-circuit classes and the circuit-specific scalar
consequence

```text
B4+B5+B6+B7+B8+B9>=13968.
```

Wave188's verified `18018` bound on all short dual words remains
numerically stronger because it includes nonminimal words.

## 6. Exact integer arithmetic null

The displayed inequalities admit the integer row

```text
n1=0,
n2=p2=640,
n3=p3=1599,
b3=1280,
c1=r1=1599,
h=427,
r2=Y=W=0,
all other a,b,c variables zero.
```

Here

```text
I=8316,
3*h-b3=1,
4*n2+r1-C=1,
Q0=6291.
```

It has one unused exact-three raw-label slot and one unused low leaf-label
slot. This is an arithmetic null control only. It is not a cover, circuit
family, code, graph, or endpoint construction.

## Boundary

```text
conditional Q>=6237 theorem:      VERIFIED
conditional Q>=6238 theorem:      DERIVED (Wave192)
conditional Q>=6291 theorem:      DERIVED
independent verification of 6291: pending
rank 11 / endpoint excluded:      no
strict original n3 improvement:   no
Conway-99 / external novelty:     UNKNOWN
```
