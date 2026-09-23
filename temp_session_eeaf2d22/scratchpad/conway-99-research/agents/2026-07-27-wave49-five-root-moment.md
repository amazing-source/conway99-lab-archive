# Wave 49 construction report

```yaml
role: construction
date_utc: 2026-07-27T18:20:31Z
git_commit: e4394aa9172fa97a6dafa9158148c2183603a01b
claim_label: CANDIDATE
scope: exact five-root one-free moment layer and numerical endpoint scout
inputs: attempts/wave49-five-root-moment/input-freeze.sha256
method: independent class regeneration, labelled tensor accumulation, S5 congruence, controls, exact witness evaluation, floating SDP scout
command: .\.venv\Scripts\python.exe attempts\wave49-five-root-moment\five_root_moment.py
outputs: attempts/wave49-five-root-moment/{coefficients.json,results.json,combined-sdp-result.json,compact-handoff.json}
limitations: discovery is not verification; numerical status is not a certificate; endpoint remains UNKNOWN
```

Exact discovery facts:

- class streams `21/62/208`; 683 labelled admissible five-root masks;
- 21 canonical root families with the frozen requested dimensions;
- 2,520 exact `S5` permutation-congruence mappings and 680,400 class-record
  comparisons, with no target-graph automorphism assumed;
- 42 of 42 Petersen/Clebsch direct-vs-expansion controls passed;
- all 357 matrices on the 17 immutable witnesses are exactly indefinite, with
  stored integer negative directions.

The combined Wave48+Wave49 Clarabel scout is `optimal_inaccurate` near the PSD
boundary. Its negative common margin is not an exact infeasibility result; no
rational dual certificate was extracted. The endpoint `n3=4158` remains
`UNKNOWN`.
