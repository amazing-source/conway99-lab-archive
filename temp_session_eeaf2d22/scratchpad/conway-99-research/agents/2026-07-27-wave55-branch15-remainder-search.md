# Wave 55 bounded proof-producing remainder search

```yaml
role: proof_a
date_utc: 2026-07-27T20:14:40Z
git_commit: a4a61658356253fb95cf68252c972a4f79df38fe
claim_label: UNKNOWN
scope: "branch 15 of the exact 33-case endpoint cover, additionally conditioned by x187=0"
inputs:
  - "attempts/wave55-branch15-remainder-search/run-input-hashes.sha256 | sha256 bbb04dcf734c5cb75d54e1d618695cc8b5883dfd5924b1b204dab17e3422bef9"
method: "Pinned Exact b921cd1 on the independently byte-checked OPB remainder, with proof logging and a 120-second solver timeout"
command: "wsl bash attempts/wave55-branch15-remainder-search/run_exact.sh"
outputs:
  - "attempts/wave55-branch15-remainder-search/solver.txt | sha256 c89ef24b102e9c2d0f3006f14f96e0e66321bf39b372d2105df12febce21eec5"
  - "attempts/wave55-branch15-remainder-search/result.json | sha256 6451828026bcd11f154f483fa7330cf665c704531a30851f4dea9da7d1decd9b"
  - "attempts/wave55-branch15-remainder-search/package-manifest.sha256 | sha256 4ab349a92de45428071a4f6d12ac64d9c74777079a6e0d0a328f76598f61784e"
limitations:
  - "Exact returned UNKNOWN, so the run closes no branch and certifies no formula consequence."
  - "The timeout option is a solver CPU setting, not a strict process-wall guarantee."
  - "The 488832021-byte partial proof is nonterminal and is excluded from publication evidence."
  - "Only WSL memory snapshots were retained; no continuous host-memory transcript exists."
```

The selected shard is the exact open remainder exported by Wave 53:

```text
branch 15
AND x187=0
formula sha256:
b1681416ee2860c4b40ce854fb533062af8e1c7a9dc0c423ba0c5f0545677d08
```

The pinned solver ran for `120.061` CPU seconds after `3.75835` seconds of
parsing. It reported:

```text
status:        UNKNOWN
conflicts:     112,215
decisions:     807,666
propagations:  140,931,770
solutions:     0
```

The zero solution count is not an UNSAT result. The generated proof stream is
only a prefix because the solver reached its bound before a terminal
conclusion. Its hash and byte count are retained in `result.json`, but the raw
488 MB file is ignored and is not treated as a certificate.

This longer run therefore adds engineering information only: the selected
branch remains difficult for the present encoding. It supplies no complete
case coverage beyond the already verified `0/33`, no endpoint exclusion, no
strict upper bound below `4158`, and no Conway-99 resolution.
