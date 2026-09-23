# Verifier failed runs

These failures are retained so that the audit is reproducible and does not
hide tooling corrections.

1. The first preinspection hash-formatting command used
   `[System.IO.Path]::GetRelativePath`, which is unavailable in the installed
   Windows PowerShell/.NET runtime. It emitted no usable freeze rows and did
   not open candidate contents. The rerun used a checked workspace-prefix
   substring and produced the committed preinspection freeze.
2. `Get-Date -AsUTC` was unavailable in this Windows PowerShell. The timestamp
   was obtained with `(Get-Date).ToUniversalTime()` instead.
3. The first independent-checker run failed before graph enumeration because
   the formula row collector appended `\end{align*}` to the last formula.
   The collector was tightened to stop at `\end{...}`; the corrected run then
   passed, and the hostile suite exercises all parsed tables.
4. One read-only PowerShell hash-display command had an empty pipeline element
   after a `foreach` block. It was rerun using an explicit result array.
5. A combined replay-and-cleanup command was rejected by the shell safety
   policy before execution. The two replays were run separately, their hashes
   were checked byte-identical, and the temporary replay files were removed
   through `apply_patch`.

None of these failures altered the frozen submission, primary-source bytes, or
the preserved raw printed `FAIL_AS_PRINTED` result.
