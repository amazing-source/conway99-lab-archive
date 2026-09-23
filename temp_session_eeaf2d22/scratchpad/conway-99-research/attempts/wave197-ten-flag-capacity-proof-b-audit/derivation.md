# Compact derivation

For a nonedge `{x,y}`, two of the seven graph triangles through `y`
contain the two common neighbors of `x,y`; the other five are
anticomplete to `x`.  Hence at most five flags containing the label are
centered at either endpoint, for a total capacity ten.

If `s_e` counts selected type-three flags using `e`, minimality injects
selected circuits into flags.  Since the `p3` private labels have
`s_e=1`, while every other label has `s_e<=10`,

```text
3n3+9p3<=10|U|.
```

Wave196 gives `|U|+a3+b3<=J<=H=3564`, hence

```text
S10=10H-3n3-9p3-10a3-10b3>=0.
```

Together with `SF=1287-n3-h-g>=0`, `SH=3h-a3-b3>=0`, and the Wave194
rows,

```text
Q0-(57C-263V)/30
 =4SI/5+6S2/5+SE2/5+7RA/10+3SL/10+S10/90
  +4SH/45+11SF/30+a1/10+3b3/5+c2/5+4g/15+2W/5.
```

At `C=4158,V=99`, the target is `70323/10`, so `Q>=7033`.
