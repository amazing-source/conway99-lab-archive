# Wave 64 independent verification report

## Verdict

**`VERIFIED` in the stated finite scope.**  A clean implementation that
imports no discovery code reconstructed the rooted transition/design space,
validated the explicit 140-block witness, checked the rational control point
row by row with exact fractions, and audited the residual-codegree closure
formula.  Endpoint `n3=4158`, Conway-99, and novelty remain **`UNKNOWN`**.

The discovery package was frozen before inspection.  Its 17-file sealed
manifest and eight-file input freeze both validate exactly, and all 18
substantive preinspection hashes remain unchanged.

## Independently reproduced finite results

- The residual labels are the 84 edges of
  `H = K14 - 7K2 = K_{2,2,2,2,2,2,2}`, each of degree 12 in `H`.
- There are exactly 35,560 candidate three-edge matchings.  Their
  support-union type census is:

  | Type `(union 2, union 3, union 4)` | Count |
  |---|---:|
  | `(0,0,3)` | 6,720 |
  | `(0,1,2)` | 20,160 |
  | `(0,2,1)` | 6,720 |
  | `(0,3,0)` | 280 |
  | `(1,0,2)` | 1,680 |

- There are exactly 840 allowed transition variables, 60 at every base
  point.
- Direct dynamic programming gives exactly 6,040 allowed perfect matchings
  at every base point.
- There are exactly 280 transition-triangle cuts.
- The residual-pair domain splits into 84 prism-forbidden intersecting
  pairs, 840 allowed intersecting pairs, and 2,562 disjoint pairs.  No target
  automorphism was assumed.

## Explicit integral block witness

Every stored block index, label, type, and doubled-support field was checked
against the independently generated canonical list.  The 140 selected blocks
satisfy:

- every one of the 84 labels occurs in exactly five blocks;
- all 420 used disjoint pairs have load one;
- each of the seven support groups is doubled in exactly 12 blocks;
- every support occupancy profile is `(n0,n1,n2)=(32,96,12)`;
- all 84 local dichotomy rows equal two; and
- relation counts for support unions `(2,3,4)` are `(5,74,341)`.

The solver restriction `full_opposite_count=5` is explicitly disclosed in
the witness metadata.  The witness is a valid point of the **block-only
master**, not a graph.

## Exact rational control

The assignment

```text
z = 1/120 on type (0,0,3)
z = 1/240 on type (0,1,2)
z = 0 on the other block types
t = 1/10 on every allowed transition
```

satisfies every declared stronger-linear-master row exactly:

- 84 label-degree rows equal five;
- seven support rows equal 12;
- 84 local dichotomy rows equal two;
- 168 transition matching rows equal one;
- all 1,176 endpoint-profile residuals are zero;
- disjoint pair loads have census
  `0:42, 1/10:840, 1/5:1680`, so all are at most one; and
- every transition-triangle left side is `3/10 <= 2`.

This proves only rational feasibility of the declared linear relaxation.  It
does not supply an integral transition/design or a graph.

## Codegree closure and exact scope

For distinct residual labels `p,q`, let

```text
Q_pq = |label(p) intersect label(q)|.
```

The independently checked closure row is

```text
sum_{r != p,q} x_pr*x_qr = 2 - Q_pq - x_pq.
```

The 3,486 residual pairs have `Q=0` for the 2,562 disjoint pairs and `Q=1`
for the 924 intersecting pairs.  Adding the `Q` already-known common base
neighbors makes the total common-neighbor count `2-x_pq`: two for a
nonedge, one for an edge.  The analogous base/residual identity reproduces
all 1,176 endpoint-profile rows.  The other root/base and base/base pair
classes are already fixed by the rooted scaffold.

Thus binary transition/block variables satisfying pair simplicity and
**all** closure rows yield the full degree and common-neighbor equations of
an `srg(99,14,1,2)`.

Scope clarification: those closure rows do not independently forbid
triangular prisms away from the chosen root.  They complete the strongly
regular graph equations, not a global prism-free endpoint encoding.  The
present block-only and stronger linear masters omit the closure rows and are
strict relaxations.

## Solver and evidence boundary

- The HiGHS infeasibility status for extending one fixed block witness was
  not promoted: there is no exact certificate, and the result concerns only
  that one witness.
- The MiniCard 180-second nonhit remains `UNKNOWN`.
- No integral stronger-master witness or complete residual graph is present.
- The discovery run report records base commit
  `81c8d45426938ea8490af55d81f05b7c2ad99035`; this audit froze the
  uncommitted package against repository HEAD
  `6dba25f93ba8b0375a6d7057eac4c83e58934fb4`.
- Eight independent tests pass, including duplicate-record rejection,
  changed-label rejection, closure-scope checks, and byte-for-byte
  deterministic result replay.

## Reproduce

```powershell
.venv\Scripts\python verification\wave64-rooted-transition-design\verify_wave64.py
.venv\Scripts\python -m unittest verification\wave64-rooted-transition-design\test_verifier.py -v
```
