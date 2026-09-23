# Independent verification of Wave144

Verdict: `PASS_NULL_BOUNDARY`.

The discovery package is frozen at manifest SHA-256
`b5369353ac6959b0662e3f424cf80e48094ac6bcdb79572bf604632c45509436`.
All ten package entries and all four prerequisite hashes pass.

## Exact local support

The verifier does not import the discovery checker.  It independently
rebuilds the degree and pair-common-neighbor equations for every frozen
Wave21 six-vertex class.  It exhaustively enumerates all size-at-least-three
outside-neighborhood cells, then uniquely reconstructs pair, singleton, and
empty cells.

All 62 exact attainable-weight sets match the sealed result.  In particular,
the only singleton supports are

```text
class 1  -> 66
class 3  -> 56
class 5  -> 46
class 14 -> 36.
```

The verifier also checks all 66 stored integer `z_P` witnesses directly
against the total, six degree, fifteen pair, and output-weight equations.

## Exact aggregate endpoint

The endpoint table has 65 nonzero cells, all positive integers.  It satisfies
every one of the 62 class marginals at `n3=4158`.  Independent Krawtchouk
evaluation gives

```text
t=0:  1120529256
t=1: 12854346120
t=2: 55869122232
t=3: 84712070520.
```

These equal the four right sides independently reconstructed from the frozen
Wave141 low-input rows.  The signed check also gives exactly

```text
S_6 = 2734116.
```

Because the lifted model imports `n3<=4158` and has an exact integral primal
at `4158`, its optimum is exactly `4158`.  It does not improve the known
bound.

## Hostile tests

Six verifier tests pass.  They include rejection of a modified local
profile, rejection of a modified aggregate count, and a fresh check that the
gap at weight `68` in class 36 is real rather than an extrema artifact.

## Evidence boundary

The certificate chooses only aggregate class/weight counts and one local
profile per used cell.  It does not make those profiles compatible across
overlapping six-sets.  Therefore it is not a 99-vertex graph construction
and is not existence evidence.  Conway-99 and novelty remain `UNKNOWN`.

## Reproduce

```powershell
python -B verification\wave144-sixset-odd-profile\independent_verify.py

python -B -m unittest discover `
  -s verification\wave144-sixset-odd-profile -p "test_*.py" -v
```
