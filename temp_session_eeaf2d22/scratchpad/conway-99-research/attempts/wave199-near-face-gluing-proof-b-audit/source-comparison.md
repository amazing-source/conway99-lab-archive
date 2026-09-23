# Sealed source comparison

The independent mathematical result and its exact replay were frozen at

```text
9c78ecd7234b402e69e7148f8621031d1463ed2504664cd51ee7af80da8d2494
```

before inspecting proof A.

The sealed proof-A manifest is

```text
1a3aa613b343fa071eee79fc337742f25f0aa949cc141f8da4eca29ecfb72671.
```

The source agrees with the independent audit on the budget 23, the lower
bound of 48 saturated orientations, the strengthened upper bound seven,
and the conditional consequence `Q>=7038`.  Its 10 manifest entries,
exact replay, and 6 tests pass.

The sealed Wave198 proof-A-audit package passes its documented replay and
6 tests.  Generic unittest discovery fails because its test module uses a
relative import without package context.  This is recorded as an
environment/portability limitation only.
