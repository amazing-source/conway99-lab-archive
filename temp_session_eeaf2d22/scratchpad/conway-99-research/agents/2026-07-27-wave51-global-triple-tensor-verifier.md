# Wave 51 global triple tensor: independent verifier

```yaml
role: verifier
date_utc: 2026-07-27T19:03:51Z
git_commit: e4394aa9172fa97a6dafa9158148c2183603a01b
claim_label: VERIFIED
scope: exact arithmetic and positive-control interpretation of the aggregate Wave 51 ordered-triple relaxation only
inputs:
  verification/wave51-global-triple-tensor/preinspection-freeze.sha256: 3b1f8815203f6914eb0bba73113436ad8e5640db674e8c87044cbabadce2e474
  attempts/wave51-global-triple-tensor/exact-result.json: 8d42c51b5e6b5137466a4adf95442f4d67cf2708c29ac134f7972b8cfbc16d1e
method: clean-room SRG/incidence derivation plus independent integer reconstruction of the normalized tensor, local tables, algebra equations, balances, and association diagnostic
command: python -B verification/wave51-global-triple-tensor/independent_check.py --input attempts/wave51-global-triple-tensor/exact-result.json --output verification/wave51-global-triple-tensor/independent-result.json
outputs:
  verification/wave51-global-triple-tensor/independent_check.py: 27e9c4f5ba966028015425a7caf8b2711f1ab716509cf5dc8e464a8f0a4c1cc3
  verification/wave51-global-triple-tensor/independent-result.json: e119fec0ff61e79539c3f34c2a17119511f9c4d78e399fe37df061d43529fb27
limitations: aggregate triples only; no association scheme, graph realization, quadruple consistency, endpoint resolution, Conway-99 resolution, or novelty determination
```

## Verdict

The exact tensor arithmetic and the interpretation as a positive feasible
point of the stated aggregate relaxation are `VERIFIED`. The displayed
average tables are `REFUTED` as association-scheme intersection numbers.
The prism-free endpoint, Conway-99, and novelty remain `UNKNOWN`.

The verifier froze all discovery artifacts before inspection and imported no
discovery code. It independently recovered:

```text
231 graph triangles;
local triangle-intersection graph 3K6;
spec(K)=18^1,7^54,0^44,(-3)^132;
prism-free q distribution (32,144,36);
S=B-D, spec(S)=4^187,(-17)^44;
S^2+13S-68I=0 and 4I-S=21E_0.
```

The frozen 21-entry tensor reconstructs five nonnegative integral local
tables. All margin, identity, `K^2`, `KS`, `SK`, `S^2`, local-row,
divisibility, and 125 global balance checks pass. All 625 ordered
association-algebra checks were evaluated independently: exactly 100 fail,
starting with `81 != 153` at `(1,1,2,2)`.

The mutation suite has one valid baseline and ten hostile cases; all 11 tests
pass. Free physical memory remained about 57%, above both the user's 15%
reserve and the verifier's 20% start floor.

This result is a rigorous null result for this relaxation. It neither
constructs nor excludes the endpoint graph. No automorphism is assumed.
