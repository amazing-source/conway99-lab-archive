# Wave 165 independent paper verification

Verdict:

```text
VERIFIED_WITH_SCOPE
```

For every hypothetical `srg(99,14,1,2)`,

```text
12*C8 <= 37422 + 3*P = 41580 - n3.
```

Here `C8` counts unlabelled induced cubes, `P` counts unlabelled induced
triangular prisms, and the last equality imports the separately verified
identity `n3+3P=4158`.

Consequences include

```text
C8 <= 3465                      in general,
C8 <= 3118                      when P=0,
C8 <= 3118                      at n3=4158.
```

The verifier used a clean-room paper reconstruction and did not inspect or
execute discovery code. The argument assumes no graph automorphism and no
restricted search domain.

This does not prove a strict upper bound below `n3=4158`, exclude the
endpoint, construct a graph, establish literature novelty, or resolve
Conway-99.
