# Compact orientation-lift derivation

For an unordered selected type-three label `e`, let `s_e` be its selected
flag multiplicity and `t_e` the number of its two occupied orientations.
The five-flags-per-orientation theorem gives `s_e<=5t_e`.  On each of the
`p3` private labels, `s_e=t_e=1`.  Hence

```text
3n3+4p3<=5T,
```

where `T=sum t_e`.  The old-raw `a3+b3` orientations are distinct and lie
outside the selected union, while Wave196 gives `J<=H=3564`.  Therefore

```text
T+a3+b3<=J<=H,
S5=5H-3n3-4p3-5a3-5b3>=0.
```

The exact certificate is

```text
Q0-(76C-349V)/40
 =4SI/5+6S2/5+SE2/5+7RA/10+3SL/10+S5/40
  +3SH/40+13SF/40+a1/10+3b3/5+c2/5+9g/40+2W/5.
```

At `C=4158,V=99`, the target is `281457/40`; thus `Q>=7037`.
