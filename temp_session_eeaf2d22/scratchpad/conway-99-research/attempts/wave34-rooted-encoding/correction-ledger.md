# Wave 34 rooted-encoding packaging correction ledger

## 2026-07-24: raw Windows stream preservation

The pre-publication Git audit found that three checksum-pinned outputs contain
CRLF bytes:

```text
compression-audit.json
dimacs-audit.json
test-results.txt
```

The repository-wide rule `* text=auto eol=lf` would normalize those bytes in
the Git object database, so their working-tree SHA-256 values would not match
the published manifests after a clean clone.

No formula, clause, variable, mapping, gzip, witness checker, mathematical
claim, or output content changed. The correction adds path-specific
`-text -diff` rules in `.gitattributes`, following the repository's existing
pattern for checksum-pinned raw Windows process streams. Git now retains the
three exact discovery bytes.

The original and retained hashes are:

```text
compression-audit.json
  df6bcc6077480ff5348357a51b471862ad82c2d1088a561d1dabd1c96664746c
dimacs-audit.json
  da267da5708f50a0eb46f2c511318e99797ef8a6a9c5f4537db91fef5d5ff1ab
test-results.txt
  98b747fc36cd3e9552af131445d6f596ebc0b7c82cfcca5672bcbdff80e7b99a
```

Both the 16-entry publication manifest and the 18-entry complete local
manifest continue to validate unchanged after the attribute correction.
