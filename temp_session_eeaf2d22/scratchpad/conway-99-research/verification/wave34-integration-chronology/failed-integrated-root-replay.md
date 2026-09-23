# Retained direct integrated-root failure

Date: 2026-07-24

Command:

```powershell
$env:WAVE34_FULL_CENSUS = '1'
python -B -m unittest discover `
  -s verification\wave34-rooted-structural `
  -p "test_static_compare.py" -v
```

The unchanged verifier stopped before its tests because the central status
file had changed during Wave 34 integration:

```text
AssertionError: hash drift for STATUS.yaml:
b2224b3c71e8b5d578bd2571584ca71f40c2f8e2856b5834a8e6f7d1edf0b0f2
!=
feda17934162602804015e17130c029ffdba7bf0307cdf234f4a7d8979298864

Ran 0 tests
FAILED (errors=1)
```

The first hash is the initial uncommitted integration-draft byte observed by
the failed run. It is retained only as failure evidence and need not equal a
later integrated `STATUS.yaml`.

The other two structural suites completed before this stop:

```text
Stage 1 precomparison: 13 tests PASS
candidate full census:  7 tests PASS
```

No frozen input was changed to make the direct run pass. The exact replay
route is frozen in `protocol.md`.
