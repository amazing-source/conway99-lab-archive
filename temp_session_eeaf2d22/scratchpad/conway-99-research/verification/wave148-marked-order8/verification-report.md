# Wave148 independent marked-row verification

Verdict: `PASS_WITH_SCOPE`.

The verifier froze and checked both chronology boundaries before opening the
sealed data:

```text
preparation manifest: d28805adb6a6353430ab0630832a08b3ba74aa72fece7c6cedd8f2ffd6b9449d
discovery manifest:   3b937619d251f99999b6c4ebfb6e8a13de869417bbe2b03047efa259aaf71344
```

All five preparation entries and all twelve discovery entries pass their
recorded hashes. The independent checker imports only the clean-room module
frozen in the preparation manifest. It never imports or executes Wave148
discovery code.

## Complete independent reconstruction

The verifier independently reconstructed all rooted order-seven types and
all coefficients obtained by deleting one unmarked vertex from an order-eight
graph. Roots are fixed pointwise; ordered-pair roots are not interchangeable;
and no graph automorphism is assumed.

For a vertex-rooted type `tau`, it checked the integer equation

```text
m_tau * (14 - d_tau) * x_H7
    = sum_K e_vertex(tau,K) * x_K8.
```

For an ordered-pair-rooted type, it checked

```text
m_tau * (lambda_or_mu - c_tau) * x_H7
    = sum_K e_pair(tau,K) * x_K8,
```

using `lambda=1` for an edge root and `mu=2` for a nonedge root. Here `m_tau`
is the number of rooted realizations inside the source graph, `d_tau` is the
root's internal degree, and `c_tau` is the roots' number of common neighbors
inside the source graph.

The complete exact comparison covers:

```text
vertex-rooted rows:                     944
ordered-pair-rooted rows:             4,440
vertex nonzero coefficients:         10,872
ordered-pair nonzero coefficients:   17,782
zero-capacity ordered-pair rows:        893
```

Every semantic key, multiplicity, relation, internal count, residual, left
coefficient, order-eight support key, and support coefficient matches exactly.
All 893 zero-capacity pair rows have empty support.

## Row-order translation

The two independent producers use different harmless enumeration layouts.
The discovery artifact sorts by `(source order-seven mask, rooted key)` and
then assigns sequential row IDs. The clean-room builder initially sorts
globally by rooted key. Therefore their raw JSON bytes are not expected to be
identical.

The verifier separately establishes that the discovery IDs are sequential,
its semantic keys are unique, and its rows follow its documented sort. It then
drops the non-mathematical row ID, keys every row by
`(order-seven mask, rooted key)`, sorts canonically, and compares the complete
row dictionaries. Both normalized payloads have SHA-256

```text
4b9a67d3b00db65b486f33172416be72ad740ebfbd1e8dd7180c5dd4e30d3e8f
```

The sealed discovery bytes remain independently fixed:

```text
gzip bytes / SHA-256:
122,626
e7a39699584fe60ff251119063d66d8eed2a14a69d671c183533806cddc92aa1

canonical JSON bytes / SHA-256:
1,685,154
3bdfdafa7e1675bf1fe160f44f1fea0e53792b5c2e87e0bfb529a15bd1cc2a8f
```

## Independent controls

For all 916 order-eight classes, the rebuilt columns satisfy:

```text
sum of vertex-mark coefficients = 2 * number of edges
sum of pair-mark coefficients   = sum_v degree(v)*(degree(v)-1).
```

All 208 source-class vertex left aggregates also match
`7*14 - 2*edges(H)`.

Three hand-sized coefficient controls reproduce `2`, `2`, and `6` for the
empty-to-one-edge degree row, empty-to-path nonedge common-neighbor row, and
edge-to-triangle common-neighbor row. Every realized marked row also passes
on the independently constructed `3 x 3` rook graph:

```text
order-seven subsets: 36
order-eight subsets:  9
vertex failures:      0
pair failures:        0
```

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave148-marked-order8\independent_verify.py

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave148-marked-order8 -p "test_*.py" -v
```

Fifteen preparation and hostile post-handoff tests pass. Free physical memory
was 41.4% after the run, above the 20% verifier floor.

## Scope wall

This verifies the complete marked vertex-degree and pointwise ordered-pair
common-neighbor order-seven-to-eight row artifact. These equations are
necessary consistency conditions, not sufficient conditions for a
99-vertex graph.

The combined Wave147/Wave148 semidefinite program has not been run. There is
no rational dual certificate and no strict `n3` upper bound from this wave.
Conway-99 and external novelty remain `UNKNOWN`.
