# Independent compact derivation

If `Q=7037`, integrality forces `Q0=7037`.  Multiplying the Wave198
certificate by 40 gives a nonnegative integer budget of 23.  In
particular,

```text
SF<=1, g<=2, SH<=7, S5<=23.
```

For each nonprivate occupied selected orientation, let `m` be its
multiplicity and put

```text
q=number of such orientations,
epsilon=sum(5-m),
eta=J-T-(a3+b3),
delta=3564-J.
```

Exact substitution gives

```text
S5=5delta+5eta+epsilon,
4q=297-3SF-3g-SH+epsilon+delta+eta.
```

Hence `delta+eta<=4`, `epsilon<=23`, and `q>=71`.  At most `epsilon`
orientations have multiplicity below five, so at least 48 have
multiplicity five.

Since `SF<=1`, every center has 13 full-pool flags except possibly one
center with 12.  A saturated orientation at a 13-flag Hilton--Milner
center exhausts one of its three degree-five pairs with one fiber vertex.
That pair loses four occurrences, and the other two degree-five pair
fibers lose at least one each, so `36-j_x>=3` and the center has at most
three saturated orientations.

At a 12-flag center, saturation alone gives `36-j_x>=4`; its 36 pair
incidences support at most `floor(36/5)=7` saturated orientations.  Since
`delta<=4`, globally there are at most seven saturated orientations.
This contradicts the required 48, excludes `Q=7037`, and proves the
conditional integer bound `Q>=7038`.
