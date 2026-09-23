# Independent derivation

For each selected unordered exact-three label `e`, let `s_e` be selected
multiplicity and `t_e` its number of occupied center orientations.
Five flags per fixed orientation give `s_e<=5t_e`. On each private label,
`s_e=t_e=1`. Therefore

```text
3n3+4p3<=5T.
```

The `a3+b3` old raw assignments give distinct oriented labels outside the
selected union, while the full pool has oriented union at most `36V`.
Thus

```text
T+a3+b3<=36V,
S5=180V-3n3-4p3-5a3-5b3>=0.
```

Independent coefficient expansion then yields the certificate recorded
in the main audit report.
