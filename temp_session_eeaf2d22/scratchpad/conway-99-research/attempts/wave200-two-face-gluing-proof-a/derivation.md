# Compact derivation

For `Q0` equal to 7,037 or 7,038, the Wave198 certificate budget `B` is
at most 63. Its relevant subrow is

```text
S5+3SH+13SF+9g<=B.
```

With `S5=5delta+5eta+epsilon` and

```text
4q=297-3SF-3g-SH+epsilon+delta+eta,
s>=q-epsilon,
```

coefficient comparison gives

```text
4s>=297-3B>=108,
s>=27.
```

At a tight 13-flag center, the three Hilton--Milner degree-five fibers
give `delta_x>=3s_x`. At a deficient center, each saturated fiber loses
four labels and gives `delta_x>=4s_x`. Thus globally

```text
3s<=delta<=S5/5<=B/5,
delta<=12,
s<=4.
```

The contradiction proves `Q>=7039`.
