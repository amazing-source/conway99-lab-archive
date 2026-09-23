# Wave 21 local-diagonal failed runs

One post-generation hash command was launched from
`attempts/wave21-local-diagonal/` while its path list was still written
relative to the repository root.  PowerShell therefore reported five
`Resolve-Path` failures.  No mathematical command depended on that output,
and the hostile test suite in the same invocation passed 15/15.

The hash command was rerun from the repository root with the intended paths
and succeeded.  No test or generated result was changed in response to this
working-directory mistake.
