# Failed and bounded routes

## Initial full-row-rank assumption

The first rank script asserted that all 161 forbidden rows were independent.
Exact RREF refuted that assertion with rank 143. The corrected route computes
and preserves the 18 dependencies rather than discarding rows silently.

## Process-memory probe

The first row-generator launch failed before solving because a Windows process
memory API call did not return a usable record. The search guard was narrowed
to the reliable host-free-memory query; external monitoring separately
confirmed that each relevant worker stayed far below 3 GiB.

## Unshifted row generation

The first exact run eliminated all 161 forbidden rows together with
normalization and `A_0=1`, before the independent torsion-shell identity was
available. It loaded every positive primal and dual lower row at once.

At a 180-second wall and batch size 24, exact replay recorded:

```text
iteration  active rows  violated rows
0          64           794
1          88           695
2          112          699
3          136          707
4          160          451
```

Classification: `UNKNOWN_WALL`.

This route is retained because it shows that exact reduced-space LP is
computationally viable, but its terminal point violated 451 omitted
inequalities. The nonmonotone violation count is expected: adding cuts changes
the selected feasible point and can expose different omitted rows.

## Dense full-system solve

Wave134 already recorded that direct dense exact and floating-point full-system
formulations were not certificates. Wave135 does not reinterpret those
timeouts or numerical failures as infeasibility evidence.

## Next alternatives if shifted row generation stalls

- Solve the dual separation problem and preserve an exact Farkas certificate.
- Search for additional exact torsion, moment, or split-enumerator identities
  before repeating LP.
- Use sparse exact basis updates so each added character row does not rebuild
  the complete reduced matrix.

None of these alternatives has yet established feasibility or infeasibility.
