# Failed and superseded routes

## Dense enumeration of all all-odd pairs

There are `12! * 10,395 = 4,979,221,632,000` labelled `(F,R)` pairs per
all-odd type. Dense rank evaluation is not a practical certificate format.
The exact first-nonzero-diagonal pivot CSP in `proof.md` replaces it without
an automorphism restriction.

## Full dense rank distributions for the even types

The continuation target is rank-26 equality, so a complete distribution of
all higher residual ranks would do substantially more work than the theorem
requires. The checker uses a mathematically necessary diagonal filter and
then exact rank on every survivor. This proves absence or finds complete
rank-26 witnesses, but it does not claim the exact minimum above one.

## Abandoned Wave 41 endpoint artifact

The untracked file under `attempts/wave41-endpoint-evenpart/` was explicitly
treated as an untrusted lead and was not read, imported, overwritten, or used
as an input. Wave 42 reconstructs the equality test from the frozen verified
Wave 41 formulas.

## First background-launch command

The first Windows `Start-Process` attempt did not quote the workspace path,
so Python parsed the path prefix ending in `math` as a script and exited with
a syntax error. No mathematical output was produced. The corrected launch
quoted the script and output paths. The raw launcher logs were not retained
because they contained the local absolute workspace path; this record
preserves the failure mode without publishing that path.
