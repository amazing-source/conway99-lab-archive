# Compact equality-face derivation

With `L=delta-3q+epsilon`, the exact conditional certificate is

```text
10Q0-(19C-85V)
 =8SI+12S2+2SE2+7RA+3SL+L+delta+2eta+SF
  +a1+6b3+2c2+4W.
```

At `Q0=7059,C=4158,V=99`, the right side is three. Hence

```text
SI=S2=RA=b3=W=0,
3SL+2(SE2+eta+c2)+(L+delta+SF+a1)=3.
```

The three symbolic classes are:

```text
SL=1,E=U=0;
SL=0,E=0,U=3;
SL=0,E=1,U=1,
```

with `E=SE2+eta+c2`, `U=L+delta+SF+a1`.

Locally, if

```text
e_P=rho_P-sum_selected(m_y-1),
```

then

```text
c_x<=12: L_x=3(12-c_x)+q_x+sum e_P,
c_x=13:  L_x=q_x-3+sum e_P.
```

Local zero slack means no nonprivate orientation at a 12-flag center. At
a 13-flag center, every non-degree-five type is empty with zero excess,
and each of the three degree-five types has exactly `e_P+k_P=1`.

The three-unit face forces `c_x in {12,13}` and at most three
multiplicity-one nonprivate orientations. Each such orientation has an
occupied opposite orientation, but the opposite may have higher
multiplicity, so no parity or two-center contradiction follows.
