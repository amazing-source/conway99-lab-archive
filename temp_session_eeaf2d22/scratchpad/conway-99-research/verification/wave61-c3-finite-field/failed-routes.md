# Wave 61 verifier failed attempts

## Initial odd-prime eliminator

The first verifier run stopped before producing a result because the
leading-corner symmetric congruence routine indexed one Schur-complement
tail coordinate relative to the current row rather than the active leading
corner.  Its independently computed congruence rank disagreed with ordinary
row-reduction rank and triggered an assertion.  The index was corrected, and
the fixed routine subsequently agreed with row reduction for all four primes
on every one of the 1,140 targets and on hostile hyperbolic controls.

No result from the failed run was retained as evidence.

## First determinism comparison

Command:

```powershell
python -B verification/wave61-c3-finite-field/independent_check.py `
  --verify verification/wave61-c3-finite-field/independent-results.json
```

The regeneration completed its exhaustive computation but failed the final
object equality assertion.  During that run, a delayed process from an
earlier launch rewrote `independent-results.json` in the superseded schema
with

```text
claim_label = VERIFIED_WITH_CORRECTION
verdict field absent
sha256 = 81f2e7b88858b1fd62bc4b844fc364f262a5042f4ce95d937d46fa566b68a25b
```

The research protocol permits only the base claim labels, so the intended
schema is

```text
claim_label = VERIFIED
verdict = VERIFIED_WITH_CORRECTION
sha256 = a18c6f8343b480a6fd278dc53509aa6f4a85b193aae2400efe1fb151e93a15c1
```

The stale writer was no longer live when this was diagnosed.  The target was
restored and a fresh full comparison was launched only after confirming that
the verifier process was the sole Wave 61 Python process.

The failed comparison is not mathematical evidence and is retained here so
the schema race is not hidden.  The fresh comparison subsequently exited
cleanly against the stable target hash
`a18c6f8343b480a6fd278dc53509aa6f4a85b193aae2400efe1fb151e93a15c1`.
