# Compact audit derivation

Use

```text
a1+a2+a3=n1,
b1+b3=2p2,
c1+c2=p3,
r1=a1+b1+c1.
```

Raw capacities give

```text
SE2=2r2-a2-c2>=0,
SE3=3h-a3-b3>=0.
```

The demands `a2,a3,b3,c2` each have a non-exact-two continuation.
Private-label uniqueness and the type-two center-orientation rule make
these pair-label demands.  An old exact-three pair absorbs at most three;
a new orbit-closed pool of `Y` exact-one circuits and exact-three mates
absorbs at most `3Y/2`.  Hence

```text
SR=3h+3Y/2-(a2+a3+b3+c2)>=0.
```

Let `U` be the labels covered by selected type-three circuits.  Then

```text
|U|>=C-(n1+2n2).
```

For one chosen type-three flag per `e in U`, the privacy-free Wave191 leaf
lemma gives a low exact-one/exact-two target.  Its complete collision list
is selected low, raw low, exact-one members of `Y`, or a new low circuit
in `W`.  Therefore

```text
|U|<=n1+2n2+r1+2r2+Y+2W,
SL=2n1+4n2+r1+2r2+Y+2W-C>=0.
```

The disjoint pool count is

```text
Q>=Q0=n1+n2+2n3+r1+r2+2h+Y+W.
```

The exact positive-slack identity frozen in `exact-results.json` gives

```text
Q0>=59C/39.
```

At `C=4158`, integrality yields `Q>=6291`.

