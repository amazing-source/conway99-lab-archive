# Retained verifier failures

## Preinspection hash-display command

The first read-only PowerShell command intended to print candidate hashes
computed the hashes but failed while formatting each path:

```text
The regular expression pattern \ is not valid.
FullyQualifiedErrorId : InvalidRegularExpression
```

Cause: a literal backslash was passed to PowerShell's regex-based `-replace`.
No candidate file was modified, and no candidate content was printed.  Before
any candidate content was inspected, the command was rerun using
`String.Replace` for path separators and the successful output was committed
to `preinspection-freeze.tsv`.

## Generated-cache cleanup

Two attempts to remove the verifier's generated `__pycache__` with
PowerShell `Remove-Item` were rejected by the execution policy before running.
After resolving and checking the exact directory was the direct child of this
verification package, the two `.pyc` files and now-empty directory were removed
with explicit .NET file and nonrecursive directory deletion calls.  No research
artifact was removed.

## Git line-ending normalization correction

The first verifier report hashed `independent-results.json` as generated in
the Windows working tree.  `Path.write_text` had used the platform newline,
so those bytes contained CRLF line endings and had SHA-256
`c8ad850e2bfc17ae72729b4cd7d85397061fe98f54e6d9f3c54e7bc36bcb20c5`.
The repository's `.gitattributes` normalized the committed blob to LF, whose
SHA-256 is
`54a02ffda9fe13293d6732fc6bf51f47e28a876a92ebdece10dea187ae0d020c`.
This made the originally recorded output hash fail against the published
blob even though the parsed JSON and mathematics were unchanged.

The writer now passes `newline="\n"` explicitly.  The result was regenerated
with LF bytes, all dependent verifier hashes were updated, and the complete
26-test independent suite was rerun.  No candidate file or mathematical
claim changed.

## Mathematical and certificate discrepancies

None found.  All candidate claims within the stated aggregate-count scope
reproduced independently.
