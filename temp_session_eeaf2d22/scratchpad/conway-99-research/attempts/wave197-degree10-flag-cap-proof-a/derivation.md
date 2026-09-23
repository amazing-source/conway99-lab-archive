# Compact Wave197 derivation

For a fixed nonedge `xy`, the two common neighbors of `x,y` occupy two
distinct triangles through `y`. The other five triangles through `y` are
anticomplete to `x`, so there are at most five possible exact-three flag supports centered at
`x` containing label `xy`. Minimality allows at most one selected
companion per support. Symmetrically there are five centered at `y`, hence

```text
d(xy)<=10.
```

If `U` is the selected exact-three label union, its `p3` private labels
have degree one and all other labels degree at most ten:

```text
3*n3+9*p3<=10*|U|.
```

Wave196 gives

```text
|U|+a3+b3<=J<=3564,
F=n3+h+g<=1287.
```

Therefore

```text
S10=35640-3*n3-9*p3-10*a3-10*b3>=0,
SF=1287-n3-h-g>=0.
```

With `SH=3h-a3-b3>=0` and the Wave194 slacks,

```text
Q0-(57*C-263*99)/30

 =(4/5)*SI+(6/5)*S2+(1/5)*SE2
  +(7/10)*RA+(3/10)*SL+(1/90)*S10
  +(4/45)*SH+(11/30)*SF
  +a1/10+3*b3/5+c2/5+4*g/15+2*W/5.
```

At `C=4158`, the target is `70323/10`, so `Q>=7033`.
