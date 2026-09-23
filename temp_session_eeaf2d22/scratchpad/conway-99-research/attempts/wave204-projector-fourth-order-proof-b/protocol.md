# Protocol and frozen scope

## Exact conditional target

Assume only the already exposed branch

```text
n3=4158,
P=0,
rank_F3(D)=11,
```

with 231 centered triangle columns in a nondegenerate 11-space over
`F_3` and 99 rank-six trace-zero star projectors

```text
P_x=-sum_(T contains x) z_T tensor z_T.
```

The positive theorem concerns adjacent vertex pairs and uses Wave176's
complete list of four outer cycle types.  It is not promoted to an
unrestricted Conway-99 statement.

## Method separation

- No graph, code, cover, SAT instance, LP, configuration, isomorphism class,
  or candidate endpoint is enumerated.
- The four adjacent relation types are reduced symbolically to matrices of
  order six and checked by independent exact row reduction.
- The abstract hostile controls are finite-field countermodels only for the
  stated implication from second-order projector data to fourth-order data.
- Failed graph premises of the controls are part of the machine result and
  may not be omitted when quoting them.

## Reproduction

```powershell
.\.venv\Scripts\python.exe -B attempts\wave204-projector-fourth-order-proof-b\exact_check.py --verify attempts\wave204-projector-fourth-order-proof-b\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave204-projector-fourth-order-proof-b\test_exact_check.py
```

The checker verifies the four frozen input hashes before doing any algebra.
