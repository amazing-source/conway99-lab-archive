# Wave51 independent audit

## Status decision

`VERIFIED` applies only to exact rational feasibility of the frozen 174-cut
relaxation.

The source package's self-assigned verified status is procedurally defective:
the same source agent chose the bundle, built the witness, and checked it.
The source is therefore classified as `CANDIDATE` before this independent
replay. No source file was edited.

## Exact replay

| Check | Independent result |
|---|---:|
| Frozen byte hashes | 14/14 |
| Nested manifests | 4/4 valid |
| Wave44 equations | 170/170 zero residual |
| Wave45 cuts | 17/17 nonnegative |
| Wave47 selected cuts | 136/136 nonnegative |
| Wave49 selected cuts | 21/21 nonnegative |
| Wave49 tensor evaluations | 5,691 exact |
| Nonnegative order-seven coordinates | 208/208 |
| Witness support | 136 |
| `h11/4` | 4158 |
| Tight cuts | 66 |
| Positive cuts | 108 |
| Minimum positive slack | 133056 |
| Maximum denominator digits | 272 |
| Active coefficient rank | 209 |

The exact cut catalog SHA-256 is
`cca9a430f3ab2f8a771177215024b6b97319ab620aa6d74fc4e8b2ae29ffa2de`.
The exact witness-vector SHA-256 is
`ab70b66bf5d0b436fc42d7cb5446aa42d228c5b19b2051c6f1c4384412da2f6e`.
The exact slack-catalog SHA-256 is
`7b1a282726b1ea0260b930a471a32db4570a4c1a0c98f3a77420e4001b8727a7`.

## Interpretation

Exact feasibility refutes an infeasibility or Farkas certificate from this
fixed finite system. It says nothing by itself about omitted directions,
full PSD constraints, integer counts, or graph realizability. The endpoint
and the global Conway-99 problem remain `UNKNOWN`.
