# Independent Wave200 two-face gluing audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Conditionally on the frozen prism-free rank-11 endpoint, the two integer
faces immediately above the sealed Wave198 rational bound are impossible:

```text
Q0 notin {7037,7038},
Q>=Q0>=7039.
```

This gives at least 7,732 projective short circuits after adding the 693
verified edge-isolated circuits, or 15,464 nonzero scalar short-circuit
words.

The proof is analytic.  The independent checker uses exact integer
incidence arithmetic and instantiates the two fixed Hilton--Milner
equality formulas.  It performs no graph, code, cover, flag-family, SAT,
LP, configuration, enumeration, isomorphism, or brute-force search.

## 1. Frozen inputs

The audit uses two prior verifier theorems.

- Wave196 supplies the simple intersecting fixed-center family of
  3-subsets of seven local blocks, the four vertices in each block-pair
  fibre, `c_x<=13`, `j_x<=36`, and the two Hilton--Milner equality
  formulas when `c_x=13`.
- Wave198 supplies the oriented multiplicity-five row, the full-pool
  separation, the integer lower-bound variable `Q0`, and the exact
  certificate target
  `(76C-349V)/40=281457/40`.

All sealed input-manifest hashes match `input-freeze.sha256`.  The
Wave200 proof-A source package was also sealed and its manifest entries
were replayed without drift.

## 2. The two integer budgets

Multiplying the Wave198 certificate by 40 gives

```text
40Q0-(76C-349V)

 =32SI+48S2+8SE2+28RA+12SL
  +S5+3SH+13SF
  +4a1+24b3+8c2+9g+16W.
```

At `C=4158,V=99`, the integer values `Q0=7037,7038` have budgets

```text
B=23,63,
```

respectively.  Hence either face satisfies

```text
S5+3SH+13SF+9g<=B<=63.                         (1)
```

## 3. Oriented incidence forces many saturated labels

Let

```text
delta   =3564-J,
eta     =J-T-(a3+b3),
epsilon =sum (5-m) over nonprivate selected orientations,
q       =number of those orientations,
s       =number with m=5.
```

Direct substitution from the definitions, independently reproduced by
coefficient vectors, gives

```text
S5=5delta+5eta+epsilon,                         (2)
4q=297-3SF-3g-SH+epsilon+delta+eta.             (3)
```

At most `epsilon` of the `q` orientations are unsaturated, so
`s>=q-epsilon`.  Equations (2)--(3) imply

```text
4s>=297-(3SF+3g+SH+3S5).                        (4)
```

Three times (1) dominates the parenthesis in (4) coefficientwise; the
unused coefficient vector is

```text
8SH+36SF+24g>=0.
```

Therefore

```text
4s>=297-3B>=108,
s>=27.                                          (5)
```

## 4. Local four-fibre loss permits very few

For a center `x`, put

```text
delta_x=36-j_x,
s_x=number of saturated selected orientations centered at x.
```

A necessary collision guard deserves explicit treatment.  A block pair
in a simple 3-uniform family on seven points has only five possible
third points.  A saturated orientation occurs in five distinct flags,
all whose local triples contain its block pair.  It therefore exhausts
all five possible triples on that pair.  Two saturated orientations at
the same center cannot occupy the same fibre.

If `c_x=13`, the fixed-center family is one of the two verified
Hilton--Milner equality formulas.  Each has exactly three block pairs of
degree five.  A saturated one loses four distinct leaf labels; each
remaining degree-five fibre loses at least one because it contains only
four vertices.  Thus the total loss from the 39 leaf occurrences is at
least

```text
4s_x+(3-s_x)=3+3s_x,
```

and

```text
delta_x>=3s_x.                                  (6)
```

If `c_x<=12`, the saturated fibres are distinct and each loses four
labels, so

```text
j_x<=3c_x-4s_x,
delta_x>=36-3c_x+4s_x>=4s_x.                   (7)
```

Summing (6)--(7), then using (1)--(2), yields

```text
3s<=delta<=S5/5<=63/5.
```

Because `delta` is integral,

```text
delta<=12,
s<=4.                                           (8)
```

Equations (5) and (8) contradict one another.

## 5. Source wording correction

The proof-A sentence saying that distinct saturated labels use distinct
fibres because “one flag has only one leaf in each fibre type” is not,
by itself, sufficient: disjoint sets of flags could in principle use two
different leaves of one type.  The claim remains valid because the
verified fixed-center family is simple, and a fixed pair belongs to at
most the five triples obtained by choosing its third point.  One
multiplicity-five orientation exhausts that entire pair degree.

This clarification is part of the verifier proof and is recorded here
rather than silently repairing the source argument.

## 6. Replays and boundary

The independent result and its eight tests pass.  The sealed proof-A
checker and all six source tests pass.  The separately sealed hostile
proof-B checker and all seven of its tests also pass.  Both source
manifests have no hash mismatch.  Proof B independently records the same
simple-family pair-degree correction and obtains the sharper
face-specific saturation lower bounds `57` and `27`.  All three routes
agree exactly on the consequence:

```text
excluded faces:                  Q0=7037,7038
conditional lower bound:         Q>=7039
all projective short circuits:   7732
nonzero scalar circuit words:    15464
```

The mechanism stops at `Q0=7039`, whose multiplied budget is 103; the
coarse saturation lower bound no longer contradicts the local cap.

No graph, code, cover, or endpoint object is constructed.  Rank 11,
endpoint existence, a strict improvement of the original `n3` endpoint
bound, external novelty, and Conway-99 all remain `UNKNOWN`.

```text
Wave200 two-face exclusion:       VERIFIED_WITH_SCOPE
source wording clarification:     RECORDED
endpoint contradiction:           no
rank 11 / Conway-99:               UNKNOWN
```
