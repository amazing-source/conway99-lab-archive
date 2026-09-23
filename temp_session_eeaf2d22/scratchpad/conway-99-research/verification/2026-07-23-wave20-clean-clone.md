# Wave 20 detached clean-clone replay

```yaml
date_utc: 2026-07-23T17:37:22Z
commit: 442671d6926ade4ffde2754f804f34b6fbd7ee16
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
workspace-only or untracked Wave 21 file was copied into it. The Python
executable came from the orchestrator workspace's ignored virtual environment;
the Wave 20 checkers themselves use only the standard library.

## Commands and outcomes

From the detached clean clone:

```powershell
python -B -m unittest discover `
  -s attempts\wave20-global-obstruction `
  -p test_exact_check.py -v
python -B -m unittest discover `
  -s attempts\wave20-global-obstruction\independent-verifier `
  -p test_independent_check.py -v
python -B -m unittest -v `
  attempts\wave20-n3-63-structural\test_exact_check.py

python -B attempts\wave20-global-obstruction\exact_check.py `
  --output <temporary-submitted.json>
python -B `
  attempts\wave20-global-obstruction\independent-verifier\independent_check.py `
  --output <temporary-independent.json>
python -B attempts\wave20-n3-63-structural\exact_check.py `
  --output <temporary-n3-63.json>
python -B attempts\wave20-n3-63-structural\exact_check.py `
  --verify <temporary-n3-63.json>

git diff --exit-code
git status --porcelain
git fsck --full
```

Results:

- submitted global-Schur suite: `18/18 PASS`;
- independent global-Schur suite: `16/16 PASS`;
- archival `n3=63` arithmetic suite: `14/14 PASS`;
- regenerated submitted JSON SHA-256:
  `6aea5c4688880a33d358ccc8992ef3aa63d40be70b5c450a8a39bf83b4878dc2`;
- regenerated independent JSON SHA-256:
  `575939f9abe19e5578a2efd1155495877c2080944c75cc0db6702c21a9ce2637`;
- regenerated archival JSON SHA-256:
  `cd55e820f87501a9e1c6644462aaf114f2b2b8c91438c328146efdf6d8c001da`;
- all three regenerated JSON files were byte-identical to their committed
  counterparts;
- all three YAML ledgers parsed, all IDs were unique, and target, resolution,
  and novelty labels remained conservative;
- every claim and obligation evidence path existed, including intentional
  directory-valued evidence;
- every Wave 20 path/hash pair and referenced commit in `STATUS.yaml` matched;
- the independent global manifest, status-search manifest, and archival
  `n3=63` manifest matched exact committed bytes;
- all local Markdown links in the integration documents resolved;
- all scoped Wave 20 text/code/data artifacts used LF-only bytes;
- the scoped credential and local-path scan passed;
- tracked diff: clean;
- porcelain status: clean; and
- `git fsck --full`: `PASS`.

## Retained gate failures and repairs

The first pre-integration oversized-file scan traversed the entire working
directory and therefore flagged old ignored files under `logs/local/`. It did
not identify a tracked or staged Wave 20 artifact. The publication scan was
corrected to the staged/tracked scope.

The first detached clone passed all 48 tests and all three regenerations but
failed its metadata harness because the harness required every evidence path
to satisfy `is_file()`. The valid evidence path `formal/opb-calibration` is a
directory. No repository byte was changed. The failed gate was discarded, a
second fresh `--no-local` clone used the correct `exists()` predicate, and the
complete gate above passed.

Before this replay, an independent integration reviewer also rejected two
instances that called `M=21E` a projector rather than the integral scaling of
the projector, an orphaned status hash without its path, and wording that
overstated retained source bytes. Those uncommitted defects were corrected and
the reviewer returned `PASS`.

## Scope

This replay supports the internally verified conditional necessary bound

```text
n3 >= 705,
induced_C6_count >= 209991.
```

It does not instantiate a 231-vertex triangle graph or a 99-vertex target
because target existence is unknown. It is not a construction, nonexistence
proof, formal-kernel proof, peer review, or novelty certificate. The separate
`n3=63` derivation remains discovery-only and is replayed here solely as a
transparent, numerically superseded archive. Conway-99 and novelty remain
`UNKNOWN`.
