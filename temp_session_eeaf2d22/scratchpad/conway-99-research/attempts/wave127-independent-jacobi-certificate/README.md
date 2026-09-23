# Wave127: independent level-7 Jacobi certificate audit

**Package status: CANDIDATE.  Conway-99 status: UNKNOWN.  No rank exclusion
or graph construction is claimed here.**

This package independently reconstructs the proposed
index-10/index-70 level-7 Jacobi linear program for the rank-28,
discriminant-16 case.  The Wave126 source was not inspected during the
derivation or initial runs.

The main result is an internally exact-checked correction boundary awaiting
independent verifier promotion:

- the 239-dimensional module and the Fricke factor
  \(h_c=-7^{-3-c}(f_c|W_7)\) have independent derivations;
- exact rational feasible vectors exist at cutoffs 10, 12, 14, and 16;
- each vector was checked against every original rational equality and
  inequality;
- therefore the earlier floating infeasibility reports at cutoffs 10, 12,
  and 16 were conditioning artifacts, not mathematical obstructions.

The verified finite counts are:

| cutoff | equalities | inequalities | tight inequalities |
|---:|---:|---:|---:|
| 10 | 282 | 320 | 263 |
| 12 | 304 | 436 | 300 |
| 14 | 326 | 562 | 332 |
| 16 | 346 | 700 | 344 |

See [DERIVATION.md](DERIVATION.md) for the mathematics.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts/wave127-independent-jacobi-certificate/jacobi_lp.py `
  --cutoff 12 --float `
  --write attempts/wave127-independent-jacobi-certificate/cutoff12.json
```

An exact rational candidate recovery can be reproduced with:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts/wave127-independent-jacobi-certificate/jacobi_lp.py `
  --cutoff 16 `
  --exact-candidate attempts/wave127-independent-jacobi-certificate/exact-candidate-cutoff16.json `
  --columns-cache attempts/wave127-independent-jacobi-certificate/columns-cutoff16.pkl `
  --write attempts/wave127-independent-jacobi-certificate/cutoff16-candidate-run.json
```

The recovery path first removes redundant rows exactly, solves the affine
equalities over \(\mathbb Q\), and recursively identifies lower-dimensional
active faces.  Floating solves guide face selection only.  Every selected
face is parameterized over \(\mathbb Q\), and the final vector is checked
against every original rational row.

Verify the saved cutoff-16 vector with:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts/wave127-independent-jacobi-certificate/verify_candidate.py `
  --cutoff 16 `
  --candidate attempts/wave127-independent-jacobi-certificate/exact-candidate-cutoff16.json `
  --columns-cache attempts/wave127-independent-jacobi-certificate/columns-cutoff16.pkl
```

## Interpretation

This LP is a necessary-condition relaxation.  A feasible Jacobi coefficient
vector need not be a graph, a lattice, or even a complete theta series.
An exact infeasibility certificate at a sufficient cutoff could exclude
this modular profile; a floating infeasibility message cannot.

Accordingly, these exact feasible points do **not** construct the
Conway-99 graph and do **not** prove rank-28 realizability.  They establish
only that this Jacobi relaxation does not obstruct it through cutoff 16.
