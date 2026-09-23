# Independent audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Assuming the independently verified Wave 174 endpoint code and the smallest
surviving centered rank `k=11`, all claimed finite-polar identities reproduce.

## Reconstructed polar graph

For the singular points of the parabolic quadric `Q(10,3)`, direct formula
evaluation gives

```text
(v,k,lambda,mu)=(29524,9840,3278,3280),
nonprincipal eigenvalues=80,-82.
```

For a selected set of size 231 with induced degree 32, hence 3,696 internal
edges, the two nonprincipal spectral energies are

```text
37961/732,
532/3.
```

Both are positive, so this test supplies no contradiction.

## Reconstructed outside moments

There are 29,293 outside singular points. If `b_z` is the number of selected
points orthogonal to `z`, the exact first two moments are

```text
sum b_z   = 2265648,
sum b_z^2 = 176288112.
```

The zero-frame identity implies `b_z=0 mod 3`. Substitution into the
consecutive allowed-value polynomial reproduces

```text
sum (b_z-75)(b_z-78)=1008018>0.
```

Thus the divisibility-refined second-moment test also survives.

## Reconstructed Veronese identities

If `R` is the selected orthogonality graph and `D` the centered ternary Gram
matrix, entrywise squaring gives

```text
D^(o2)=J-I-R.
```

Pure symmetric squares in dimension 11 span at most 66 dimensions. Because
all selected vectors are singular, they lie in the quadratic-form
hyperplane, giving

```text
rank_F3(J-I-R)<=65,
rank_F3(I+R)<=66.
```

No supplied or reconstructed rank floor contradicts either inequality.

## Terminology check

The primary Blokhuis--Moorhouse paper defines a cap on a quadric as a set in
which no two points lie on a line of the quadric. The endpoint set has 3,696
orthogonal selected pairs. Wave 174 forbids three selected projective points
on one ambient line; it does not forbid every orthogonal pair. The paper's
polar-cap size bound is therefore inapplicable.

## Integrity and execution

- all three Wave 175 input hashes matched;
- all nine discovery-package manifest entries matched;
- the exact checker verified its archived result;
- all five focused tests passed.

The tests are narrow exact-regression tests rather than hostile independent
implementations, so the audit separately reconstructed every displayed
formula.

## Status wall

```text
conditional polar parameters and moments: VERIFIED
conditional Veronese rank caps:           VERIFIED
polar-cap terminology quarantine:         VERIFIED
rank k=11 excluded:                       NO
strict upper bound below 4158:            NOT PROVED
external novelty:                         UNKNOWN
Conway-99:                                UNKNOWN
```
