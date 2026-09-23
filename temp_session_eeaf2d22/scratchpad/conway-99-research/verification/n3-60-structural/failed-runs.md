# Retained verifier failures

These failures are preserved to prevent silent repair and repeated effort.
Neither produced a mathematical result.

1. Preinspection timestamp command:

   ```text
   Get-Date -AsUTC -Format "yyyy-MM-ddTHH:mm:ssZ"
   ```

   Failed because the installed Windows PowerShell does not support
   `Get-Date -AsUTC`.  The replacement
   `(Get-Date).ToUniversalTime().ToString(...)` succeeded.  No file had yet
   been opened from Wave 19.

2. First independent-checker generation:

   ```text
   .venv\Scripts\python.exe -B verification\n3-60-structural\independent_residual_check.py --output verification\n3-60-structural\independent-results.json
   ```

   Failed at the verifier's own assertion because the expected ordering of
   the two `m=29` point profiles was reversed.  The computed set itself was
   correct; the expected tuple was reordered.

3. Second independent-checker generation:

   The same command failed before output at a verifier vector-construction
   assertion for `Z`: a nested conditional built a vector of the wrong
   length.  It was replaced by an explicit `(T,U)`-to-degree-vector map.

4. Third independent-checker generation:

   The same command reached histogram dynamic programming but divided by
   zero in its pruning bound at the final degree value.  The base case was
   moved ahead of the convex upper-bound call.  The subsequent generation
   completed successfully.

5. A combined prior-audit wrapper invoked
   `verification\n3-48-global-lift\test_independent_check.py` from the
   repository root.  That historical test imports its sibling module by a
   local name, so discovery failed with `ModuleNotFoundError`.  Re-running
   from `verification\n3-48-global-lift\` exactly as its audit specifies
   passed all 11 tests; the analogous Wave 16 replay passed all 24 tests.

6. After adding six more hostile controls, the verifier test expected 18
   mutation-result keys although the dictionary intentionally contained 17.
   The test failed `17 != 18`; manual enumeration confirmed 17 named controls,
   the expected count was corrected, and the suite was rerun.

7. An auxiliary, superseded rectangle-followup suite
   (`rectangle-followup/test_rectangle_check.py`, followed by its certificate
   replay) was given a 60-second bound and timed out without output.  It is not
   used as evidence.  The follow-up's final minimal `check.py` and
   `results.json` instead replayed byte-identically, and the main verifier's
   separate rectangle suite passed 8/8.

8. The first final hash-manifest wrapper used PowerShell `-replace` with an
   invalid single-backslash regular expression and failed before emitting any
   rows.  Replacing it with the literal string method `.Replace('\','/')`
   produced the manifest rows.

These failures were invocation or newly written verifier-test bugs.  They
did not alter a submitted file, and they are not counted as hostile tests or
evidence for/against the candidate.
