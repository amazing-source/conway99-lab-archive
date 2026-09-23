---
role: proof_a
date_utc: 2026-07-28T10:06:09Z
git_commit: 0a15bfe548e301ea98c83e292ba8931322e39945
claim_label: DERIVED
scope: exact rational Wave137 plus S6 projection optima, rational target witnesses at n3 708 and 4158, integral equality-lattice residue, and hard-bounded integral telemetry
inputs:
  - attempts/wave132-distinguished-biweight/discover_rational.py sha256=5873b38468e008452307b9e77bdf963ee7e86935008c94acab295b981ecae1bf
  - attempts/wave132-distinguished-biweight/exact_check.py sha256=347b89017e69a65be5f72f405344ea8bb849c603dfa1795de61064732ba39564
  - attempts/wave137-z4-arf-branches/binary_branch.py sha256=0b77a2cf41998a36cff364eede61cb07f41c4f41686d0960469f1556db0bc126
  - attempts/wave141-bivariate-graph-code/exact-results.json sha256=351857e985a871e6d69c5662f90ad5cd6a608f92b1703e84ffb549a753cc8b2e
method: exact Z3 rational linear optimization and target feasibility; independent Fraction replay; elementary active-shadow optimality; exact FLINT HNF with transform; hard-walled Z3 integer scout
command:
  - python -B -m unittest discover -s attempts/wave143-binary-s6-projection -p "test_*.py" -v
  - .venv/Scripts/python.exe -B attempts/wave143-binary-s6-projection/lattice_certificate.py --verify
  - .venv/Scripts/python.exe -B attempts/wave143-binary-s6-projection/integer_scout.py --timeout-ms 10000 --wall-seconds 15
outputs:
  - attempts/wave143-binary-s6-projection/exact-results.json sha256=25f414e21b4aef22480ccd3922a4c7abab5409c099e4c02d900960a5f28f7dfc
  - attempts/wave143-binary-s6-projection/lattice-certificate.json sha256=4cf4cb54ca424e25130e22ed99adc5a4b9b7dac7dcf27a86548847bf87558db8
  - attempts/wave143-binary-s6-projection/integer-scout.json sha256=c95f41147cb6a33ec4487e3e4c73e5c7030659ee745283326c5ff0a1f9d11303
  - attempts/wave143-binary-s6-projection/witness-plus-n3-708.json sha256=867c18e8fd8c7d5048d3bf84bea33f24916e8eb8e8cdb2591a4d513290bf6ce3
  - attempts/wave143-binary-s6-projection/witness-plus-n3-4158.json sha256=50959897f715be3975e1ec009c965f7f37ef7dfa0b42d7c5498e8722ffe732b5
  - attempts/wave143-binary-s6-projection/witness-minus-n3-708.json sha256=d17d411a2e9425c2cb60be60c827aa191dad53678aade219529690c2772432c6
  - attempts/wave143-binary-s6-projection/witness-minus-n3-4158.json sha256=c34564f04b7d42d08a99be29da652fbbc511e60fe4643bdaaff6babb46d44800
limitations:
  - the rational optimum near 6.55 million is a weak projection optimum, not a graph boundary
  - all four nonnegative integral queries ended UNKNOWN_HARD_TIMEOUT
  - equality-lattice witnesses may have negative coefficients
  - no binary code, graph, adjacency matrix, improved n3 bound, Conway-99 resolution, or novelty determination
---

# Wave143 run report

Both Arf signs admit exact rational witnesses at `n3=708` and `n3=4158`.
They also share the same weak projection range

```text
0 <= n3 <= 838878579/128.
```

The maximum is certified solely by the sixth shadow inequality and is much
weaker than 4,158.

The integral equality lattice has rank 109, nullity 33, and projected
coordinate `n3=3k` with kernel step `delta k=1`.  Thus its exact residue set
is `n3=0 mod 3`, with no stronger equality-only congruence.  Nonnegative
integral feasibility remains unknown after four hard timeouts.
