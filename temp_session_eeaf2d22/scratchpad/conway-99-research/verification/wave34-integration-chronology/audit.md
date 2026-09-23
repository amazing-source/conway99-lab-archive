# Wave 34 integration-chronology audit

Date: 2026-07-24

Verdict: **VERIFIED HISTORICAL-INPUT REPLAY**

```text
integrated commit:
0e11485de2ccdf0c1f2aa1c3e2d53a3413d9b6ea

frozen STATUS commit:
0fa5b8161baf8b2a5404a67051b7d61cbc906da3

frozen STATUS SHA-256:
feda17934162602804015e17130c029ffdba7bf0307cdf234f4a7d8979298864

unchanged structural comparison tests: 11 PASS
full census:                           ENABLED
source checkout changed:               NO
rooted solution / exclusion:           UNKNOWN
Conway-99 / n3=708 / novelty:          UNKNOWN
```

## Why an isolated replay is required

The rooted structural comparison verifier freezes the continuation-base
`STATUS.yaml`. Central Wave 34 integration necessarily changes that file.
The direct integrated-root run therefore rejected the initial integration
draft before executing a test. The exact failure is retained in
`failed-integrated-root-replay.md`.

This is the intended behavior of a fail-closed input gate. Updating the
verifier's expected hash would erase the discovery/verification chronology
and was not permitted.

## Exact replay

`chronology_replay.py`:

1. resolved exact integration commit
   `0e11485de2ccdf0c1f2aa1c3e2d53a3413d9b6ea`;
2. exported its tracked tree with `git archive`;
3. exported only `STATUS.yaml` from
   `0fa5b8161baf8b2a5404a67051b7d61cbc906da3`;
4. verified that replacement byte's frozen SHA-256;
5. changed no other archived path;
6. enabled `WAVE34_FULL_CENSUS=1`;
7. ran the unchanged `test_static_compare.py` suite; and
8. confirmed that the source checkout's Git status was unchanged.

The replay returned exit zero and exactly 11 passing tests. The portable
machine result is `chronology-results.json`, SHA-256:

```text
b18a3e402a23f39924dd282482a64404443b8aaa2f1fbfcfb32cec09a2d59cb4
```

The eight chronology protocol tests independently check the frozen Git blob,
the current/frozen distinction, exact requested-commit status hashing, exact
test-count parser, failure parser, the one-path substitution rule, and
portable command serialization.

## Retained operator and packaging failures

The first wrapper invocation supplied a guessed 40-hex expansion of the
short commit instead of the actual Git commit:

```text
invalid:
0e11485b1f548fe8242f34f5f4ff851e4b52b82a

actual:
0e11485de2ccdf0c1f2aa1c3e2d53a3413d9b6ea
```

`git rev-parse` rejected it before any archive or test. No mathematical
replay occurred in that invocation.

The first successful replay draft serialized the host's absolute Python
executable path. That draft is not published. Its SHA-256 was:

```text
ef7eed35236fe5b75696564d85a08d7f6f95826f2dabdbb535c71564158c8aa1
```

The serializer was repaired to publish the portable command only, a
regression test was added, and the complete 11-test replay was rerun. No
mathematical field changed.

A later clean-clone invocation from a post-integration checkout exposed a
second serialization defect: `current_status_sha256` was read from the
caller's worktree instead of the exact requested commit. The 11-test
historical replay still passed, but the rejected draft JSON had SHA-256
`d6012b69516ab927f831ddc7088982fa20983bc13dd54062b5a14f5002621d1b`.
The wrapper now hashes `STATUS.yaml` from the resolved requested commit,
cross-checks it against the exported archive, and has a dedicated regression
test. The accepted result again reproduces byte-identically at
`b18a3e402a23f39924dd282482a64404443b8aaa2f1fbfcfb32cec09a2d59cb4`.

## Scope wall

This package proves that the frozen rooted structural comparison remains
reproducible after central integration when its exact historical input
contract is restored in an isolated archive. It does not verify later central
prose, solve the rooted criterion, or promote any endpoint.

Binary rooted existence/exclusion, `n3=708`, Conway-99, novelty, and priority
remain `UNKNOWN`.
