# Wave 33 rooted-construction chronology v2 objections and failures

## V1 is clean-clone independent because its local files were hash-pinned

`REFUTED`. Hash pinning does not make ignored files available. At integration
`74c3725`, after 110 other live tests passed, the detached clone at
`%LOCALAPPDATA%\Temp\conway-wave33-clean-72f81f4afa4f451485eb94936811b407`
failed on missing `.venv/Lib/site-packages/pysat/card.py`. V2 copies and opens
zero solver-environment files.

## Bundle the six solver files

`REJECTED`. Two are platform-specific compiled binaries and all six are
third-party environment files. They are not mathematical certificates and
must not be bundled merely to reproduce a non-evidentiary timeout record.

## Silently skip verifier test 08 and still report 37

`REJECTED`. The exact 37-test identity digest is authenticated, the one
composite test ID is named, and the exact selected 36-test digest is separately
authenticated. V2 reports 14 discovery plus 36 verifier tests, for 50 original
tests total.

## The whole omitted test is nonportable

`REFUTED`. Its source-audit half is portable. V2 independently parses the
hash-pinned `exact_check.py` imports, confirms they are standard-library-only,
and authenticates the full portable source-audit result. Only the half that
opens local `.venv` files is `NOT_REPLAYED_NONBLOCKING`.

## Documentary solver hashes are current observations

`REJECTED`. V2 authenticates six hash strings and three version lines inside
the frozen `solver-inspection.md`. It explicitly records zero observed
environment hashes and zero local environment files opened.

## Run the unchanged comparison CLI anyway

`REJECTED`. `compare()` unconditionally calls
`verify_solver_environment_hashes()`. Claiming its old `7025cc...` stdout hash
as newly reproduced would be false in a clean clone. V2 labels the CLI
`NOT_RUN_BY_DESIGN` and uses chronology-owned calls to the hash-pinned portable
comparison functions.

## Direct function calls weaken comparison coverage

`REJECTED`. The chronology driver calls the manifest, parser, normalized
payload, independent payload verifier, BF metric, assignment encoding, bounded
manifest, recorded-result, source, scope, and hostile-search functions. It
core-binds the accepted summary and reproduces the hostile certificate
byte-for-byte. A hostile test forbids calls to the two local-environment
entrypoints.

## Replace the frozen STRUCTURE hash with the integrated hash

`REJECTED`. The earlier `45640f...` bytes are the historical input. Replacing
them with later central bytes would rewrite chronology. The eight-input archive
remains authenticated at `d62fc4...`.

## A passing clean-clone replay promotes the mathematical status

`REJECTED`. Replay proves bounded reproducibility only. Graph extension, full
rooted endpoint, `n3=708`, Conway-99, and novelty remain `UNKNOWN`; the
complete-domain UNSAT certificate remains `NONE`.
