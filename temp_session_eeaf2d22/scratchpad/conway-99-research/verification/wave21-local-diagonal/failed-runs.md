# Retained verifier harness failures

These failures occurred before the independent checker was finalized.  Neither
was a mathematical counterexample to the submitted claims.

1. Two exploratory Python profile counters used a broad three-dimensional
   dynamic program and each exceeded the shell's roughly 14-second execution
   limit.  They emitted no result.  The final checker instead eliminates
   `c_2,c_3` algebraically and exhausts only the variables bounded by the
   21-unit diagonal budget.
2. The environment's Windows PowerShell does not support
   `Get-Date -AsUTC`; that metadata command returned a parameter error after
   `git rev-parse` and `python --version` had already succeeded.  UTC metadata
   was subsequently obtained with `[DateTime]::UtcNow`.
3. The first submitted-replay command used PowerShell's generic-method syntax
   for `Enumerable.SequenceEqual[byte]`, which this parser treated as an array
   index and rejected before running any child command.  The replay was rerun
   using independently computed SHA-256 digests and byte lengths.
