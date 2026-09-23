# Wave 20 global-obstruction run failures

## Stale test expectation after the mod-four strengthening

The first test run after replacing the even-diagonal trace bound by the
stronger mod-four trace bound had:

```text
17 tests passed
1 test failed
```

The failing hostile-mutation test still expected the old trace minima `462`
and `460` for 231 and 230 indices. The checker correctly returned the new
minima `924` and `920`. The stale test expectation was changed; no
mathematical code or output formula changed in response. The subsequent full
18-test replay passed.

This was an implementation-test bookkeeping failure, not evidence for or
against the conditional mathematical claim.
