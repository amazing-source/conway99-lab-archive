# Wave 43 all-rank-33 lift reduction

Status: **DERIVED, pending independent verification**. The prism-free
endpoint and Conway-99 remain **UNKNOWN**.

Under the joint assumptions

```text
n3=4158,
rank_F3(M)=12,
every graph edge has local type 2+2+2,
the base-triangle core is one of the 264 canonical rank-33 lifts,
```

this package reconstructs every one of the 264 labelled triangle-free masks
from the frozen Wave 41 generator. No automorphism of a completed graph is
assumed.

For each lift it forms the exact necessary Gram matrix

```text
BB^T = 12I - A_X + 2J - RR^T - A_X^2.
```

## Exact discovery result

All 264 lifts have:

- two core components of sizes `12+24`;
- fibre balances `(4,4,4)+(8,8,8)`;
- nonnegative forced Gram matrix;
- Cauchy equality forcing every outside six-set to meet the small component
  in exactly two points; and
- sixty legal nonmatching pairs in each fibre.

Moreover, the two fibre-indicator differences and the
`2*small-component - large-component` contrast are three independent integer
kernel vectors. Exact rank `33` modulo `1,000,003` proves that they span the
entire rational kernel of every forced Gram matrix. Thus no additional linear
kernel cut exists beyond the already imposed two-per-fibre and two-in-small
component laws.

Thus Wave 42's exact three-way matching reduction is not peculiar to mask
`51739`: it applies to every rank-33 lift. Exhaustive six-set filtering gives
five numerical census classes:

| support / component / mixed candidates | lifts |
| --- | ---: |
| `118718 / 49736 / 45032` | 48 |
| `131908 / 54560 / 49328` | 48 |
| `132196 / 54736 / 49520` | 24 |
| `132250 / 54560 / 49328` | 48 |
| `132402 / 54648 / 49424` | 96 |

The five rows are numerical census classes, not a claim that there are five
isomorphism classes. Every lift survives these necessary filters.

## Boundary

The result supplies neither a complete sixty-column incidence matrix `B` nor
a compatible outside graph `H`. It does not exclude the all-`222`, `r3=12`
branch, the endpoint, or Conway-99. A solver timeout or absence of a found
completion would not change that status.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave43-all-rank33-lifts\exact_check.py `
  --verify attempts\wave43-all-rank33-lifts\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave43-all-rank33-lifts -p "test_*.py" -v
```
