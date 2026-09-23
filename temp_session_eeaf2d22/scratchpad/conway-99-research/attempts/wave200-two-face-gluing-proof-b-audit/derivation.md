# Compact hostile derivation

For `Q0=7037,7038`, the exact Wave198 budgets are `B=23,63`. From

```text
S5+3SH+13SF+9g<=B,
S5=5delta+5eta+epsilon,
4q=297-3SF-3g-SH+epsilon+delta+eta,
s>=q-epsilon,
```

coefficient comparison gives `4s>=297-3B`. Thus the two faces force
respectively `s>=57` and `s>=27`.

At one center, pair types partition the leaf labels. If `d_P` is the
number of flags through pair type `P` and `u_P` its distinct leaves,

```text
3c_x-j_x=sum_P(d_P-u_P).
```

A saturated orientation has `d_P=5,u_P=1`, losing four. Different
saturated labels have different types, so these losses add.

At `c_x=13`, the three Hilton--Milner degree-five types give occurrence
loss at least `4s_x+(3-s_x)`, hence `delta_x>=3s_x`. At `c_x<=12`, the
four-unit saturated losses plus the nonnegative baseline give
`delta_x>=4s_x`. Therefore `3s<=delta`.

Finally, `delta<=S5/5<=B/5` implies `delta<=12` and `s<=4`, contradicting
the uniform lower bound 27. Conditionally, `Q>=7039`.
