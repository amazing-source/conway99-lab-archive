# Wave 94 protocol: norm-14 count as a function of prism count

Claim label: `DERIVED`.

## Scope

Assume a hypothetical `srg(99,14,1,2)` and the verified Wave 71
complementary-Fano description of every norm-14 integer `-4` eigenvector.
Let:

- `P` be the number of induced triangular prisms;
- `n3` be the parameter in the previously verified identity
  `n3+3P=4158`; and
- `N14` count every norm-14 eigenvector, including both `t` and `-t`.

No prism-free, rank-28, or automorphism hypothesis is imposed.

## Target

Prove

```text
7*N14 <= 38808+12*P
N14 <= floor((38808+12*P)/7)
     = floor((55440-4*n3)/7).
```

Wave90 remains immutable. This package must independently expose the extra
prism multiplicity needed for the interpolation.

## Nonpromotion

Discovery does not verify itself. This is an `N14` bound only; it does not
bound `N16` or `N18` and does not resolve Conway-99.

