# Wave 84: rooted complete-domain SAT portfolio

Claim label: `UNKNOWN`.

This package records four bounded solver runs against the independently
byte-matched Wave 34 rooted formula:

```text
variables: 1,233,001
clauses:   4,323,943
SHA-256:  2362d15f3a20df0a0d7745eb619a94061cee9911c8dda36c191fb6d728c1c3d3
```

Three CaDiCaL configurations and one independently built Kissat
configuration all reached their 900-second limits without a model or an
UNSAT proof.  Their status is therefore `UNKNOWN`.  A timeout, conflict
count, variable reduction, or solver exit code is not mathematical evidence.

The raw local transcripts are intentionally not published because they
contain absolute host paths.  `exact-results.json` records their SHA-256
hashes and exact terminal statistics.  No transformed transcript is
substituted for a proof or model.

Longer local continuation runs remain separate and are not claimed by this
checkpoint.

