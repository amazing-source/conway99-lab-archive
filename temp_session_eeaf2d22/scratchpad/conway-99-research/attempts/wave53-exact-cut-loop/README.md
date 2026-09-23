# Wave53: bounded exact rational cut loop

Status: **CANDIDATE** discovery result.

## Result

Starting from the independently verified Wave51 support-136 rational
witness, this run completed three exact cut-and-resolve iterations.

At each of four rational witnesses it evaluated all 32 available moment
matrices exactly: three Wave45 families, eight Wave47 families, and twenty-one
Wave49 families. All 128 matrices were exactly indefinite, each witnessed by
a primitive integer direction with a strictly negative rational quadratic.

The deterministic selection rule added these cuts:

1. Wave49 root `220`, cut
   `33050a2dedb7b7a9c59a8e6778029f8477c5fe09def8af4ac8631b1e7a851d19`;
2. Wave49 root `62`, cut
   `efcd988d6b89ea6873b5a81281d41b6f6b938ac4df94368f73ed8f48b1cb9eca`;
3. Wave49 root `221`, cut
   `7923bfc7be97e5acf144316fb110f8e40b96d128334f961c328e7a8ad872c2bc`.

After each cut, rational active-set reconstruction produced an exact feasible
successor. The witness support sizes are `136, 132, 136, 138`; the terminal
witness still has all 32 matrices exactly indefinite.

## Meaning

The exact cutting-plane mechanism works across all three verified moment
layers, but these three cuts do not close the relaxation. The final 177-cut
system is exactly feasible over the rationals.

This does not establish full PSD feasibility, integer count feasibility, an
endpoint graph, or a strict upper bound. Endpoint `n3=4158`, Conway-99, and
novelty remain **UNKNOWN**.

An exploratory fourth-cut numerical infeasibility status was rejected because
no exact Farkas certificate could be reconstructed. It is documented only in
`failed-routes.md`.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B attempts\wave53-exact-cut-loop\exact_cut_loop.py --validate
.\.venv\Scripts\python.exe -B -m unittest attempts\wave53-exact-cut-loop\test_exact_cut_loop.py
```

The construction command is:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave53-exact-cut-loop\exact_cut_loop.py --compute
```

The computation and replay enforce strictly more than 20% free physical
memory. Live resource telemetry is not part of the sealed result.
