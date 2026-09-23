# Compact derivation

If `Q0=7037`, the Wave198 certificate multiplied by 40 has budget 23.
Thus

```text
SF<=1, g<=2, SH<=7, S5<=23.
```

Split `S5=5delta+5eta+epsilon`, where `delta=3564-J` and `epsilon`
is the total deficit from multiplicity five on nonprivate selected
oriented labels. Then `delta<=4,epsilon<=23`.

If `q` is the number of nonprivate selected orientations, elimination of
the flag-count, old-capacity, incidence, and union identities gives

```text
4q=297-3SF-3g-SH+epsilon+delta+eta.
```

Hence `q>=71`, so at least `q-epsilon>=48` orientations have multiplicity
five.

At a 13-flag center the Hilton--Milner equality templates have exactly
three degree-five pairs. A saturated pair loses four leaf labels, and the
other two degree-five fibers lose at least one each, forcing `j_x<=33`.
At the at most one deficient center, there are at most seven degree-five
pairs and one saturated label forces `j_x<=32`. Since total
`36-j_x` deficit is at most four, globally at most 7 orientations can
be saturated. Contradiction.
