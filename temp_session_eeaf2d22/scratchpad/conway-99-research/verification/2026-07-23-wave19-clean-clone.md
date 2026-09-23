# Wave 19 detached clean-clone replay

```yaml
date_utc: 2026-07-23T16:39:12Z
commit: e4b86b42c06bf41b8222b8a815d5b85cda4fa2ec
branch: codex/first-research-wave
platform: Microsoft Windows 10.0.26200 x64
python: 3.13.14
git: 2.51.0.windows.1
verdict: PASS
target_result: UNKNOWN
novelty: UNKNOWN
```

The repository was cloned with `--no-local` into a fresh uniquely named
temporary directory. The clone resolved exactly to the commit above. No
workspace-only file was copied into it. The Python executable came from the
orchestrator workspace's ignored virtual environment; both submitted and
independent Wave 19 programs otherwise use only the standard library.

## Commands and outcomes

From the detached clean clone:

```powershell
python -B -m unittest -v `
  attempts.wave19-alternate-frontier.test_exact_frontier
python -B -m unittest discover `
  -s verification\n3-60-closure `
  -p test_independent_baseline.py -v
python -B -m unittest discover `
  -s verification\n3-60-closure `
  -p test_independent_closure_verifier.py -v
python -B verification\n3-60-closure\independent_closure_verifier.py `
  --phase auth
python -B verification\n3-60-closure\independent_closure_verifier.py `
  --phase all --output wave19-clean-full.json
git diff --exit-code
git fsck --full
```

Results:

- submitted focused suite: `7/7 PASS`;
- independent semantic baseline: `27/27 PASS`;
- independent closure-verifier suite: `10/10 PASS`;
- canonical release authentication: `30/30` entries, canonical LF, public
  commit pin `a121e789e03a32c3d29bce8947b16033c0061ce7`;
- complete independent phase: `PASS`, with empty stderr;
- regenerated independent JSON SHA-256:
  `c8fb3af52d5a929d7d88b59ef53b8825a3b2d922fdb3fad1ac4208078a27a2a2`,
  byte-identical to the committed certificate;
- four frozen release/audit hashes checked exactly;
- tracked diff: clean after replay;
- `git fsck --full`: `PASS`.

The only visible untracked file after replay was the deliberately fresh
`wave19-clean-full.json`; redirected process logs matched the repository's
ignored `*.log` policy. No committed file was modified.

## Scope

This replay independently executes the complete connected/disconnected
catalog census, the two-Petersen orbit and all allowed `Z` placements, the
exact Gram systems, and the final Farkas check from clean committed bytes. It
supports the conditional exclusion of `n3=60`, subject to the audited H/L
semantics and the official House of Graphs completeness/nonisomorphism
premise. It does not resolve `srg(99,14,1,2)` and does not establish novelty.
