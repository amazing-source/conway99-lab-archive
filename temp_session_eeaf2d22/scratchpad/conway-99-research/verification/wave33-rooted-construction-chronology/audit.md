# Wave 33 rooted-construction chronology v2 audit

## Verdict

`VERIFIED` only for the clean-clone-independent historical reproducibility
described below.

The repair preserves every original discovery and verifier byte. Their four
authenticated roots remain:

```text
candidate freeze:      441465c157f28e658afde31e6ca0cff49ccb5841a001150bd3e3af616c5bf63a
candidate manifest:    0cd192c0182506b3c901806cc96abb9fe53f04dc906b0b5cd73bc9b602558ff4
precomparison freeze:  4ccbbad9c01eab764d9aa6fb207114e43f8c5a36bec3ec5bf0d161708ce0360d
verifier manifest:     20c27560bdf9720cd1cf043b11c218130cd2891a2d3c874f9dbc9bce2f27fbbf
```

No third-party source file or binary is bundled. No candidate, discovery,
precomparison, comparison, existing verifier, or central-document byte was
changed.

## Retained detached-clone failure

Chronology v1 incorrectly assumed six ignored solver-environment files were
portable package inputs. The first detached-clone failure is retained exactly:

```text
integration: 74c3725
detached root: %LOCALAPPDATA%\Temp\conway-wave33-clean-72f81f4afa4f451485eb94936811b407
prior live tests passed: 110
chronology failure: missing .venv/Lib/site-packages/pysat/card.py
```

This was a real reproducibility blocker. The other five files would have had
the same untracked/local status. V2 removes the copy/read requirement instead
of hiding it.

## Historical-input chronology

The discovery input ledger froze the pre-integration `STRUCTURE.md` at
`45640fecaa5834b24063c682c7edd0898f2746253a7708a2c70c3610e4bcb99a`.
Later central integration changed the live document. V2 retains the immutable
eight-input structured snapshot:

```text
d62fc4311577d56cbf34f8bd4e63aefb3b796457b3d020f4322324073d82f7dd
```

Every decoded path, size, and SHA-256 must match the original input ledgers.
All 17 candidate-freeze entries, 16 nested candidate-manifest entries, 14
verifier-manifest entries, and five precomparison entries are independently
validated before copying.

## Clean-clone replay boundary

The synthetic historical root contains the eight archived inputs and only
hash-accepted candidate/verifier artifacts. It contains no `.venv` and copies
zero solver files.

The original verifier has 37 tests. Exactly one composite test is not run:

```text
test_candidate_comparison.CandidateComparisonTests.test_08_source_and_solver_provenance
```

That test combines two distinct assertions:

1. The portable source half checks that `exact_check.py` uses only the Python
   standard library. V2 reperforms this independently and also authenticates
   the original `static_source_audit()` result at
   `d7f45c6931fe10062321f2349e2c64aec0806e3258f0fdc4368a837bf0c023f5`.
2. The environment half opens six ignored `.venv` files. V2 records this half
   as `NOT_REPLAYED_NONBLOCKING`, with zero observed environment hashes and
   zero local files opened.

The frozen `solver-inspection.md`, SHA-256
`345e5976222b950b7bb9d3805f7cef0836cbbdff9e9abf2ec85454b28eada342`,
still authenticates six documentary path/hash records and three version
lines. Those records are not reported as current file observations. The
document itself says the solver exit status is not a certificate and no
nonhit or UNSAT response is promoted.

Exact test identity is fail-closed:

```text
discovery 14 IDs: 1c8b91a4ee799f4c0cb336bc48ffd4a2f2b010a0860a53157dd6adae33adc784
verifier all 37 IDs: ab8dea45aa3a32d4df0758dd9fe142c2fa6fecb815693085027e17313202d9e1
verifier selected 36 IDs: 185da0159a5f9689b2a60a830d9c78be9ea0d7c14c3535dd9ce992dc69542389
```

The unchanged historical tests pass:

```text
construction discovery: 14
construction verifier:  36
embedded original total: 50
```

This is 50 original test cases, plus a separately executed portable
source-provenance gate. It is not 51 unchanged verifier/discovery tests.

## Exact and comparison reproduction

The standard-library exact checker runs under isolated Python and regenerates
`exact-results.json` byte-for-byte:

```text
ba6640eacd041bc8349024a1d3f13e3d74bd67cdad64d2d78c9a94927319c496
```

V2 does not invoke the unchanged comparison CLI, because that CLI
unconditionally opens the six local solver files. Its prior stdout hash
`7025cc...` is retained only as historical metadata with status
`NOT_RUN_BY_DESIGN`.

Instead, chronology-owned code imports the hash-pinned standard-library
comparison modules from the synthetic root and directly calls the portable
verification functions. The deterministic projection has SHA-256:

```text
446beb4ddd2a51194315954d7005cb01d90ff8643a64c78801d93524d65e7818
```

It core-binds the authenticated accepted summary
`c0476fb877e0e7d6a6fc63b1a4c72bda0d7804a18a4e4b2b6d5a1bcbc4b6b459`
and reproduces the hostile certificate byte-for-byte at
`340e5df716ad63bceba25c745ab04c22ea1a3dca01e939072f09775a5fc5f634`.

## Hostile chronology tests

Twenty current-tree chronology tests pass. In addition to the v1 archive,
manifest, traversal, symlink, mutation, status, and no-write gates, v2:

- performs its full replay from a minimal source tree with no `.venv`;
- poisons `PYTHONPATH` and `VIRTUAL_ENV` while subprocesses use `-I -B`;
- authenticates the complete and selected test-ID lists;
- distinguishes documentary hashes from observed environment hashes;
- rejects promotion of `NOT_REPLAYED_NONBLOCKING`; and
- proves the clean comparison driver calls neither `compare()` nor
  `verify_solver_environment_hashes()`.

Canonical command:

```powershell
python -B -m unittest discover `
  -s verification/wave33-rooted-construction-chronology `
  -p "test_*.py" -v
```

Regeneration command:

```powershell
python -B verification/wave33-rooted-construction-chronology/chronology_replay.py `
  --output <scratch>/chronology-results.json
```

The v2 machine-readable result SHA-256 is
`b2f0b872221a3fd9f41d6a88637be21034b70e8c8129fe57617115548b425957`.

## Scope wall

This verifies chronology and bounded reproducibility only. It does not turn
the timeout into evidence, supply an O-O layer, construct or exclude a graph
extension, close the rooted endpoint, exclude `n3=708`, resolve Conway-99, or
establish novelty. Those statuses remain `UNKNOWN` or `NONE`.
