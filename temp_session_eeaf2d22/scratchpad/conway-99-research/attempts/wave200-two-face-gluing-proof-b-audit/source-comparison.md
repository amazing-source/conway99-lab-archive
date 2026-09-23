# Sealed source comparison

The Wave200 proof-A package manifest has SHA-256

```text
b909a16d3324f76e394322e6058f844bcf3bcc61409d567fdfd6f50ab53aced4.
```

All 10 manifest entries match. Its exact replay passes and all six tests
pass.

The hostile audit agrees with the source on the two budgets, the uniform
lower bound `s>=27`, the additive inequality `3s<=delta`, the upper
bound `s<=4`, and the conditional consequence `Q>=7039`.

The audit makes the distinct-fiber step explicit via

```text
3c_x-j_x=sum_P(d_P-u_P),
```

and records the stronger face-specific lower bound `s>=57` at
`Q0=7037`. Neither point changes the source conclusion.
