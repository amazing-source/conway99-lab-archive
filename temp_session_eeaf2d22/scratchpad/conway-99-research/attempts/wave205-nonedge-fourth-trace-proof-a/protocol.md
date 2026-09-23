# Wave 205 proof A protocol: nonedge fourth trace

Claim labels in this discovery package are limited to `DERIVED`,
`CANDIDATE`, `REFUTED`, and `UNKNOWN`.

## Frozen target

Assume the conditional branch

```text
G is srg(99,14,1,2),
n3=4158, equivalently P=0,
rank_F3(D)=11.
```

Use the verified centered triangle realization and star projectors.  For a
nonedge `x,y`, let

```text
C_xy=(z_T dot z_U)_(T contains x, U contains y),
h_xy=tr(P_x P_y P_x P_y).
```

The discovery target is to determine `h_xy` from actual two-center SRG
geometry, or else to isolate the first exact target premise that is missing.

## Permitted derivations

- Use `lambda=1`, `mu=2`, the seven edge-triangles at each center, and the
  endpoint prohibition on two disjoint triangles with three cross edges.
- Use `D=B^T A B` over `F_3`, the verified simplex star Grams, and the
  verified projector formula.
- Treat a Gram-kernel vector only as a restricted-form radical vector unless
  an actual column relation is separately proved.

## Control standard

A hostile local control must be an explicit finite graph on the union of the
two centers and their neighborhoods.  It must:

1. have the exact two seven-triangle stars and exactly two common neighbors;
2. give every exclusive neighbor exactly two common neighbors with the
   opposite center;
3. obey the SRG upper bounds of one local common neighbor for an edge and two
   for a nonedge;
4. obey the endpoint cross-edge cap for all selected disjoint star blocks;
5. reproduce its claimed centered cross Gram and fourth trace exactly; and
6. list every omitted global target premise.

No solver exit code is evidence.  A solver may discover a control, but the
sealed package must contain the complete adjacency certificate and verify it
without a solver.

## Reproduction

```powershell
.\.venv\Scripts\python.exe -B attempts\wave205-nonedge-fourth-trace-proof-a\exact_check.py --verify attempts\wave205-nonedge-fourth-trace-proof-a\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave205-nonedge-fourth-trace-proof-a\test_exact_check.py
```

