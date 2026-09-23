# Wave159: fifteen-cut four-root checkpoint

Status: `CANDIDATE` discovery package with a same-lane `DERIVED` exact replay.
It is not independently `VERIFIED`.

## Result

The exact Wave152 thirteen-cut endpoint pseudowitness was separated by fresh
four-root covariance cuts from the two exact negative blocks, root masks 3
and 12. Retaining all thirteen earlier cuts and adding both new cuts gives a
fifteen-cut pair-root-zero-face system.

A tight-tolerance HiGHS scout found a credible numerical feasible point.
Exact reconstruction then produced a rational pseudowitness with:

- order-seven/order-eight supports `204 / 887`;
- all `10,313` replayed rows and all `10,274` restricted rows passing exactly;
- modular rank `887 / 887`;
- all fifteen exact cut values nonnegative;
- exactly three active cuts, with hashes beginning `68a099dd`, `93c3dceb`,
  and `8fc95276`.

This establishes only that this finite fifteen-cut relaxation is exactly
rational feasible. It does not construct a graph.

## Four-root feedback

Reevaluation of all nine four-root blocks again found exact negative integer
quadratic-form certificates only at root masks 3 and 12:

| root | flags | scaled negative quadratic value | numeric minimum |
|---:|---:|---:|---:|
| 3 | 155 | `-27011041286703517116394938226429083495309284913470656030516224` | `-0.000585914` |
| 12 | 178 | `-88438068438190522607991067007701768100527095926734078733792256` | `-0.000583266` |

The other seven blocks have no exact negative certificate in this run.
Near-zero floating eigenvalues are not exact positive-semidefinite proofs.

Thus the new pseudowitness fails the full four-root covariance conditions.
The fresh cuts are effective locally, but the relaxation moves to another
point that violates the same two block families. A seventeenth-cut solve was
deliberately not started.

## Interpretation and next strategy

Repeated one-direction cuts are exposing a cutting-plane loop: each finite
selection of scalar inequalities leaves freedom to evade them elsewhere in
the root-3 and root-12 covariance matrices. The prudent next move is a
different representation of the whole matrix constraint, rather than another
blind pair of eigenvector cuts. Candidate alternatives are:

1. a proof-producing semidefinite or sum-of-squares certificate that treats
   an entire covariance block at once;
2. an exact low-dimensional facial reduction of the root-3/root-12 blocks,
   using the three persistent active cut directions to identify a common
   nullspace or forced face;
3. a symmetry/isotypic block decomposition, if it can be derived without
   imposing an unproved automorphism on the sought graph;
4. a dual infeasibility search coupling both root families and the deletion
   equations, with rational certificate recovery.

Any symmetry restriction must be stated explicitly and cannot support an
unrestricted nonexistence claim by itself.

## Reproduction

The exact replay is lightweight:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe attempts\wave159-four-root-cut-loop\replay_fifteen.py
.\.venv\Scripts\python.exe -m unittest attempts\wave159-four-root-cut-loop\test_wave159.py -v
```

The scout remains diagnostic. The exact witness and covariance certificates
are the mathematically relevant artifacts. `input-freeze.sha256`,
`wave152-before.sha256`, and `wave152-after.sha256` record the immutable
top-level dependency boundary. Wave152's four pre-existing `__pycache__`
files were outside the original inventory and all predate Wave159; no new
bytecode was written during this lane.

## Evidence boundary

- Discovery cannot independently verify itself.
- Solver status, residuals, and numerical eigenvalues are not certificates.
- The exact witness is a count pseudowitness, not a graph.
- The inherited witness `scope` and conclusion key still say `after two
  cuts`; that is stale metadata in the frozen reconstruction script. The
  actual retained cut count is fifteen and is exactly replayed here.
- Endpoint feasibility at `n3 = 4158`, a strict upper bound below `4158`,
  and Conway-99 all remain `UNKNOWN`.
