# Wave 20 orchestrator corrections and failed invocations

No item in this file is evidence for the mathematical claim.

## Frozen wording correction

The first paragraph of `failed-routes.md` says `n3>=699`. That sentence is a
stale description of the intermediate mod-two endpoint. The same frozen file's
later integral-lattice section, the discovery report, exact checker, result
JSON, run report, independent reconstruction, and final verifier audit all use
the strengthened endpoint

```text
n3 >= 705.
```

The frozen file is intentionally not rewritten. Its SHA-256 remains
`23355b845f17dac5b4ef260544d1664c8943999634ee8d02f63d5a6b0ef048b2`.

## Root replay failures

Before following the package's working-directory instructions, the
orchestrator attempted a module-style unittest invocation from the repository
root. Import resolution failed before any test ran. The exact original command
and raw terminal text were not retained, so they are not reconstructed here.

A separate exploratory invocation supplied a nonexistent `--check` option to
`exact_check.py`; `argparse` rejected it before computation. The command was
conceptually:

```text
python exact_check.py --check <result>
```

The documented invocations were then run from
`attempts/wave20-global-obstruction`:

```text
python -B -m unittest -v test_exact_check.py
python -B exact_check.py --output <fresh-result.json>
```

They passed 18/18 tests and regenerated SHA-256
`6aea5c4688880a33d358ccc8992ef3aa63d40be70b5c450a8a39bf83b4878dc2`.
The independent verifier separately records its own root-directory import
failure and corrected 16/16-test invocation. None of these harness failures
changed proof code or mathematical conclusions.

During the later publication-gate replay, the orchestrator again used the
wrong relative interpreter path from that working directory:

```text
.\.venv\Scripts\python.exe -B -m unittest -v test_exact_check.py
```

PowerShell rejected the path before any test ran. From
`attempts/wave20-global-obstruction`, the repository interpreter is instead
`..\..\.venv\Scripts\python.exe`. With that correction, the submitted suite
passed 18/18, the independent suite passed 16/16, and fresh JSON outputs had
the expected SHA-256 values `6aea5c4688880a33d358ccc8992ef3aa63d40be70b5c450a8a39bf83b4878dc2`
and `575939f9abe19e5578a2efd1155495877c2080944c75cc0db6702c21a9ce2637`.

The first combined publication-hygiene command also failed at PowerShell parse
time because a `foreach` statement was piped directly to `Format-Table`,
creating an empty pipe element. No validator ran. Repeating the read-only
checks after collecting the loop rows in an array passed: the literature
ledger parsed as JSON with 7 query batches, 13 sources, and 3 recorded access
failures; all three frozen status-manifest entries matched; all four status
artifacts used LF-only bytes; and `git diff --check` passed.

The first public-hygiene scan used `private correspondence` as a secret-search
term. It therefore returned two harmless limitations sentences that explicitly
say private correspondence is outside the audit's coverage, and exited one;
the subsequent `git diff --no-index` also has a normal exit-one convention for
new content. Neither was a content failure. A corrected credential/local-path
scan omitted that prose phrase and treated diff exit codes separately.

In the first uncommitted `STATUS.yaml` integration patch, the orchestrator
expanded the known short status-audit commit label into an unverified
40-character string. Before staging, `git rev-parse` exposed the mistake and
the field was replaced with the actual commit
`21f53fb6314b7c1a704694a9b38f3a18292b769d`; the replay-notes field was likewise
expanded from Git rather than guessed. The incorrect metadata was never
committed or used as mathematical evidence.
