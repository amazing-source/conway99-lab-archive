# Retained failures and non-closures

## Tool-wrapper parse failure

The first read-only PowerShell wrapper intended to hash allowed inputs failed
before execution:

```text
At line:16 ... An empty pipe element is not allowed.
```

The wrapper piped a `foreach` block directly into `Format-Table`. It read no
file, ran no checker, and produced no evidence. The corrected wrapper first
assigned the loop output to `$rows`, then formatted `$rows`; all pinned hashes
matched.

## Independent test-fixture arithmetic failure

The first full independent unit-test run had 14 passes and one failure:

```text
test_integer_square_minimum_two_methods ... FAIL
AssertionError: 798 != 786
```

The failing row was an auxiliary hostile control with 70 integers summing to
234. Exact division gives 46 threes and 24 fours, hence

```text
46*3^2 + 24*4^2 = 798.
```

The test fixture had incorrectly written `786`. This control is not one of the
candidate's exclusion rows: the candidate's `m=29` totals 226 and 228 remained
742 and 756 throughout. The fixture expectation was corrected to 798, after
which all 16 independent tests passed. The failed output is retained here
rather than silently omitted.

Exact failed command:

```text
.venv\Scripts\python.exe -B -m unittest -v verification\n3-60-structural\global\test_independent_global_check.py
```

## Mathematical non-closures

This subtask deliberately does not attempt to close the two advertised
`r=20` residual regimes at `m=27` and `m=30`. Reproducing the exclusions in
scope leaves the conditional `n3=60` status at
`UNKNOWN_FINITE_RESIDUAL`; an absence of a constructed object is not used as
evidence.

No unexpected semantic or arithmetic failure was found in the requested
global reductions. Hostile moment collisions were retained when they really
satisfied the tested moments, and the disconnected double-Petersen cubic
control was retained because connectivity is not a premise.
