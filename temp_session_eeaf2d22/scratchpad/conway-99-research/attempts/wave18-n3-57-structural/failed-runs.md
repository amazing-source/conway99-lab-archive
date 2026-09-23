# Retained failed run

The first execution used:

```powershell
.venv\Scripts\python.exe -B attempts\wave18-n3-57-structural\exact_check.py --output attempts\wave18-n3-57-structural\exact-checks.json
.venv\Scripts\python.exe -B -m unittest -v attempts\wave18-n3-57-structural\test_exact_check.py
.venv\Scripts\python.exe -B attempts\wave18-n3-57-structural\exact_check.py --verify attempts\wave18-n3-57-structural\exact-checks.json
```

It failed before producing the JSON result.  The checker raised:

```text
TypeError: unsupported operand type(s) for +: 'generator' and 'tuple'
```

at `point_size_profiles`, where a generator of positive point-size
increments was concatenated directly with a tuple.  The test run retained
seven passes and three errors, all with that same stack trace:

```text
Ran 10 tests
FAILED (errors=3)
```

The repair materialized the generator as a tuple before concatenation.  It
changed no mathematical formula, expected profile, or claimed status.  The
full command was then rerun: JSON generation succeeded, all ten tests
passed, and byte-for-byte `--verify` replay succeeded.
