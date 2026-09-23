# Independent Wave198 orientation-lift audit

## Verdict

`VERIFIED_WITH_SCOPE`.

The independent mathematical result was frozen before source inspection at
SHA-256

```text
07a8d5287a1770fa34aea97c3c879e07642da44d728f6e6c199d2f0b5990f07e.
```

For each selected exact-three label, orient its flag incidences from the
canonical center to the leaf.  A fixed orientation `x->y` can occur in at
most five flags: two of the seven graph triangles through `y` contain the
common neighbors of `x,y`, leaving five leaf triangles anticomplete to
`x`.

Let `T` be the number of occupied selected orientations.  Every `p3`
private label has selected multiplicity one and occupies one orientation.
All other occupied orientations have multiplicity at most five.  Hence

```text
3n3<=p3+5(T-p3)=5T-4p3.
```

The old `a3+b3` private orientations are distinct and outside the selected
union.  Wave196 gives

```text
T+a3+b3<=J<=3564,
```

so

```text
S5=17820-3n3-4p3-5a3-5b3>=0.
```

Together with `SH=3h-a3-b3`, `SF=1287-n3-h-g`, and the Wave194 slacks,
exact expansion gives

```text
Q0-(76C-349V)/40
 =4SI/5+6S2/5+SE2/5+7RA/10+3SL/10
  +S5/40+3SH/40+13SF/40
  +a1/10+3b3/5+c2/5+9g/40+2W/5.
```

At `C=4158,V=99`, the target is `281457/40=7036.425`; integrality gives

```text
Q>=7037.
```

Adding 693 edge-isolated projective circuits yields 7,730 projective
circuits and 15,460 scalar circuit words.

An independent integer accounting control has

```text
a2=15, b1=624, c1=3489,
n2=312, n3=1287, r2=8, y=15,
all other split/pool variables zero.
```

It has `Q0=7037`, with `SE2=1`, `SL=1`, `S5=3`, and every other
certificate slack zero.  Its `23/40` rounding gap is exactly

```text
SE2/5+3SL/10+S5/40.
```

This is an arithmetic control, not an object.

Both sealed source packages agree and their explicit test commands pass
6/6.  The hostile package's generic `unittest discover` path has a known
relative-import portability failure; its documented module test command
passes, so this is a packaging limitation rather than mathematical
evidence.

No graph or configuration search was performed.  Rank 11, endpoint
existence, strict original `n3` improvement, external novelty, and
Conway-99 remain `UNKNOWN`.
