# Independent count formulas

These counts apply to the clean-room CNF translation in
`cleanroom_encoding.py`.  They are not presumed to match a later candidate's
choice of cardinality encoding.

## Primary and product variables

The unrestricted labeled primary domain has

```text
C(70,2) + 70*15 = 2,415 + 1,050 = 3,465
```

bits.  Symmetry and hollowness do not remove a labeled graph: one bit names
each unordered off-diagonal `D` entry, while every diagonal entry is the
constant zero.

The nonlinear products are:

```text
OO D-products: C(70,2)*68 = 164,220
OO B-products: C(70,2)*15 =  36,225
OQ DB-products: 70*15*69 =   72,450
QQ B-products: C(15,2)*70 =   7,350
total product auxiliaries = 280,245.
```

Each product equivalence contributes two binary clauses and one ternary
clause, hence `840,735` product clauses.

## Exact-count encoder

For `0 < k < n`, the prefix threshold encoder allocates

```text
S(n,k) = sum_{i=1}^n min(i,k+1)
       = (k+1)n - k(k+1)/2
```

states.  Put `c=k+1`.  After simplifying the boundary constants, its clause
count is

```text
C(n,k) = 2c^2 + 2 + (n-c)(4c-1).
```

The first term includes the boundary recurrences and the two terminal units.
For `k=0` or `k=n`, no threshold states are allocated and there are exactly
`n` unit clauses.

Summing `S(n,k)` over all 4,985 exact-count instances gives `946,806`
cardinality auxiliaries.  Summing `C(n,k)` gives `3,478,308` cardinality
clauses.  Together with the product definitions:

```text
variables = 3,465 + 280,245 + 946,806 = 1,230,516
clauses   = 840,735 + 3,478,308       = 4,319,043.
```

The independently enumerated clause-length histogram is:

```text
unit:    12,084
binary: 1,823,388
ternary:2,483,571
```

## Constraint-family distributions

The variable equation inventory is:

```text
D row 9:                70
B row 3:                70
B column 14 / QQ diag:  15
SO:                    980
SQ:                    210
OO diagonal:            70
OO off diagonal:     2,415
OQ:                  1,050
QQ off diagonal:       105
total:               4,985.
```

For `OO` off diagonal, two distinct O labels share two, one, or zero support
vertices in respectively `21`, `588`, and `1,806` unordered pairs.  Thus the
84-literal exact-count targets are respectively `0`, `1`, and `2`.

For `SO`, the independently derived `(scope,target,count)` distribution is:

```text
(9,0,56), (9,1,84), (10,1,504), (10,2,336).
```

All other distributions and each deterministic variable range appear in
`count-expectations.json`.
