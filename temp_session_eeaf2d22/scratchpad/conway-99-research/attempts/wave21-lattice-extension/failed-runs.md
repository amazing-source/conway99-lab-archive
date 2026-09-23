# Retained Wave 21 harness failure

The first 12-test run had one stale hostile-test expectation.  It expected
`h=21` to survive after imposing `det(Q)>=3` when the mod-four determinant
filter was removed.  This was arithmetically wrong for a simpler reason:
`21*3=63` already exceeds the endpoint AM--GM cap 45.  The implementation and
the mathematical endpoint list were correct.

The test was repaired to use the genuinely mod-four-sensitive tuple
`(h,det(Q),det(B))=(3,5,15)`: it lies below the cap and is removed exactly
because `det(B)` must be `1 mod 4`.  No candidate artifact or frozen Wave 20
input was changed.

After the repaired suite passed, a surrounding PowerShell metadata command
failed because Windows PowerShell 5.1 does not support `Get-Date -AsUTC`.
The hashes had already printed and all 12 tests had passed.  Replacing that
metadata-only call with
`[DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')` succeeded.

An attempted call to the desktop workspace-dependency locator hung and was
externally aborted.  No dependency was installed and no file was written by
that call.  The lane therefore stayed on the standard library and did not run
the proposed numerical three-point SDP.  This is a tooling failure and an
explicit limitation, not mathematical negative evidence.

The first final-gate command invoked `python -m unittest` from the repository
root even though the documented command first changes into the attempt
directory.  Import consequently failed before any test ran.  Repeating the
documented command from `attempts/wave21-lattice-extension` ran all 12 tests.
