# Independent Wave202 three-unit equality-face audit

## Verdict

`VERIFIED_FACE_CHARACTERIZATION_NO_EXCLUSION`.

Conditionally on the frozen prism-free rank-11 endpoint and the verified
Wave201 theorem, the face `Q0=7059` has an exact three-unit certificate
and exactly three analytic slack-partition classes.  The local equality
conditions are strong, but they do not contradict the current
one-center or two-orientation rows.  The verified bound therefore remains

```text
Q>=7059,
```

giving 7,752 projective or 15,504 nonzero scalar short circuits after
the 693 edge-isolated contribution.

The source-blind result was frozen at SHA-256

```text
50be7fba9ab2a56c974e2044d60ac2d448d3556f4eea57e5e4063aed4fd8ed7e
```

before the Wave202 source was opened.

## 1. Complete three-unit partition

Multiplying the verified Wave201 certificate by ten gives, at
`Q0=7059`,

```text
3=8SI+12S2+2SE2+7RA+3SL
  +delta+2eta+SM+SF+a1+6b3+2c2+4W.             (1)
```

All terms are nonnegative integers.  Thus

```text
SI=S2=RA=b3=W=0.
```

Writing

```text
E=SE2+eta+c2,
U=delta+SM+SF+a1,
```

equation (1) reduces to `3SL+2E+U=3`.  Its complete analytic
classification is

```text
A. SL=1, E=0, U=0;
B. SL=0, E=0, U=3;
C. SL=0, E=1, U=1.
```

No graph, flag, or family configurations are enumerated.

## 2. Raw-variable consequences

Exact affine elimination of the raw identities gives

```text
delta =3-2SE2-3SL-2eta-SM-SF-a1-2c2,
a2    =60-SE2-c2-2SF,
r2    =30-SF,
n2    =357-a1-SL+SF,
y     =a3+3n3-3801-SE2+SF,
h     =1287-n3-SF-g,
q     =3n3+a3+eta+SM-3564,
p3    =7128-delta-2a3-2eta-SM-3n3.
```

The remaining variables follow from

```text
c1=p3-c2, n1=a1+a2+a3, p2=n2, b1=2n2,
r1=a1+b1+c1, J=3564-delta, T=J-a3-eta,
epsilon=SM-delta+3q.
```

Substitution reconstructs `SI=S2=RA=0`, the prescribed low slacks,
both orientation identities, and `Q0=7059` with zero symbolic residual.
All displayed quantities are integral for integral free counts and
slacks.  Their necessary nonnegativity constraints are recorded in the
frozen result.

## 3. Exact local equality structure

In one pair fibre, let `n_z` be full multiplicities, `m_z` selected
nonprivate multiplicities, `r` the number of selected values, and
`b=1` only for the three degree-five Hilton--Milner baseline fibres at a
tight center.  The local weighted-slack contribution is exactly

```text
sum_selected(n_z-m_z)
+sum_unselected(n_z-1)
+r-b.                                           (2)
```

For a deficient center,

```text
sigma_x=36-3c_x+sum_P(gap_P+r_P).
```

For a tight center,

```text
sigma_x=sum_P(gap_P+r_P-b_P),
SM=sum_x sigma_x.
```

Consequently zero local slack has the following form.

- No nonbaseline fibre contains a selected nonprivate label or repeated
  full label.
- An empty baseline fibre has exactly its one unavoidable repeat.
- An occupied baseline fibre has exactly one selected value, its full
  and selected multiplicities agree, its multiplicity lies in
  `{2,3,4,5}`, and every other full value occurs once.
- A selected multiplicity-one value costs at least one unit of `SM`.

Combining `SF` and `delta` in (1) also proves that every center has 12 or
13 full flags.  A center with 11 flags would contribute at least two to
`SF` and three to `delta`, already exceeding the total budget.

Value-by-value analysis further gives

```text
r<=SM<=3,
```

where `r` is the total number of multiplicity-one nonprivate
orientations.

## 4. Why the face is not excluded

The earlier Wave201 integer accounting profile containing one `m=1`
label cannot realize `SM=0` locally; the equality audit correctly rejects
that particular illustrative profile.  It was never claimed to be an
object.

However, the same raw arithmetic row admits a locally compatible
fibre-multiset profile with

```text
234 labels of multiplicity 2,
three labels of multiplicity 3.
```

It has

```text
q=237,
selected incidence=477,
epsilon=708,
sum(m-2)=3=delta,
SM=0.
```

A one-center distribution uses the three degree-five baseline fibres at
79 tight centers, with the remaining 20 tight centers unselected.  The
required full multiplicity patterns make every local term (2) zero.

This is only a local multiset and coefficient control.  It is not a
graph, flag family, code, cover, or endpoint object and does not prove
existence.  It does prove that the current one-center inequalities alone
cannot exclude the face.

A multiplicity-one orientation would force the opposite orientation of
the same nonprivate unordered label to be occupied, but the opposite
multiplicity need not be one.  No frozen theorem currently couples the
two full fibre-multiplicity multisets strongly enough to yield a parity
or baseline contradiction.

## 5. Sealed source comparison

Only after the independent freeze was proof A opened.  Its manifest

```text
2fde70a48ece42be075e242aa5e1e6b629624d77eef2a31c4c2b70947fa267a4
```

has ten matching entries.  Exact replay and all seven source tests pass.
Five additional verifier tests independently confirm the 12/13-center
restriction, `r<=SM<=3`, and the two-center null conclusion.

The source and verifier agree that no bound improvement follows.  No
mathematical repair is needed.

## Boundary

```text
three-unit partition:                  VERIFIED
raw-variable formulas:                 VERIFIED
local equality characterization:       VERIFIED
all centers have 12 or 13 flags:       VERIFIED
multiplicity-one count at most three:  VERIFIED
two-center obstruction:                not proved
Q0=7059 excluded:                      no
conditional Q>=7059:                   unchanged
global face realization:               UNKNOWN
rank 11 / Conway-99 / novelty:          UNKNOWN
```
