# Wave155 four-root feedback verification

## Verdict

`VERIFIED` within the frozen finite-relaxation scope.

The four stored primitive inequalities were independently reconstructed from
their integer directions and pointwise-labelled four-root flag semantics.  All
stored coefficients, primitive divisors, projected first moments, discovery
input values, and canonical cut hashes match exactly.

The replacement witnesses also replay exactly:

| witness | x8 support | base rows | active cuts | all rows | modular rank |
|---|---:|---:|---:|---:|---:|
| after two cuts | 885 | 10,310 | 1 | 10,311 | 885 / 885 |
| after four cuts | 886 | 10,310 | 2 | 10,312 | 886 / 886 |

Every stored coordinate is nonnegative.  The order-seven and order-eight
totals are respectively `C(99,7)=14887031544` and
`C(99,8)=171200862756`.  The replay includes all 170 Wave44 equalities,
208 deletion equalities, 5,384 marked constraints (including 893 correctly
removed zero rows), and the 2,211 ordered-edge plus 3,828 ordered-nonedge
upper-triangle moment identities.

Therefore:

- the four primitive covariance cuts are valid;
- the retained finite relaxation is exactly rational feasible after two cuts;
- the retained finite relaxation is exactly rational feasible after four cuts;
- no graph was constructed;
- endpoint feasibility at `n3=4158` remains `UNKNOWN`;
- no strict upper bound below 4158 was proved;
- Conway-99 remains `UNKNOWN`.

## What was checked independently

For each root mask 3 and 12, the verifier generates the locally admissible
six-vertex flags while fixing four roots pointwise and identifying only the
two free vertices.  This gives 155 and 178 flags.  For every admissible graph
class of orders 6, 7, and 8 it enumerates ordered root embeddings and
free-pair products.

For an integer flag direction `v`, the raw inequality is

```text
R * sum_H q_H(v) x_H - (sum_H s_H(v) x_H)^2 >= 0.
```

It is a covariance inequality: the quadratic term is a sum of products of
two flag evaluations, while the subtracted square is the fixed first moment.
The verifier derives the order-five and order-six counts by exact deletion
from the order-seven witness and independently recovers
`R=1014552` ordered root embeddings for both root masks.

The two HiGHS JSON files are not used as mathematical evidence.  Their role
was numerical support selection in discovery; the published verification
rests on exact rational witness replay.

## Reproduce

From the repository root:

```powershell
python verification\wave155-four-root-feedback\independent_verify.py
python -m unittest verification\wave155-four-root-feedback\test_independent_verify.py -v
```

The verifier uses only the Python standard library and checks the frozen input
hashes before doing any mathematics.  The successful full run took about
30 seconds and observed a minimum of 27.745% free physical memory.

## Evidence boundary and metadata note

The assigned `attempts/wave155-four-root-feedback` directory did not exist.
The seven named artifacts were located and pre-inspection-frozen under
`attempts/wave152-four-root-order8`; this path discrepancy is recorded in
`protocol.md`.

The after-four witness retains the earlier after-two format, scope, and
conclusion key.  This is stale metadata, not a mathematical failure: its
actual inputs include both cut files, it records four exact cut values, and
the verifier checks the two active cut equalities.

The later `iteration3-mask13-cut.json`,
`zero-face-five-cuts-highs.json`,
`exact-witness-after-five-cuts.json`, and
`four-root-evaluation-after-five-cuts.json` appeared after this protocol was
frozen.  They are outside Wave155's scope and should receive a new
pre-inspection clean-room verification.

