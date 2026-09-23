# Verifier harness failures

## 2026-07-23T18:42:04Z — preinspection inventory command

The first read-freezing PowerShell command failed at parse time with
`An empty pipe element is not allowed.` because a `foreach` statement was piped
without first assigning its output. No candidate file content was emitted or
read. The corrected command assigned the loop output to an array and produced
`preinspection-freeze.sha256`.

## 2026-07-23T18:42:04Z — timestamp command

`Get-Date -AsUTC` failed because this PowerShell version lacks `-AsUTC`.
The verifier used `(Get-Date).ToUniversalTime()` instead.

## 2026-07-23T18:49:26Z — first manifest draft

The first `artifact-manifest.sha256` draft contained a truncated SHA-256 on
the `preinspection-freeze.sha256` line.  It was caught before manifest
validation and replaced with the actual 64-hex digest.  No candidate or
mathematical artifact changed.
