# Failed routes and exact boundary

## Norm-14 colored-design rediscovery

Starting from the Wave 71 norm-14 vector gives a Fano-complement support,
a colored `2-(15,3,2)` design, and a 9-regular induced graph on 70
vertices.  Exact block equations reproduce the spectrum

```text
9^1, 3^27, (-4)^16, (-1)^14,
(-1+sqrt(2))^6, (-1-sqrt(2))^6.
```

This is not new: it is the verified Wave 33/34 rooted-extension lane.  Two
bounded cyclic-control encodings returned `UNKNOWN` at timeout and are not
evidence about existence or nonexistence.

## Smith profile as an obstruction

The integral orthogonal model determines the complete Smith form of `T`
conditional on `r`, but all eight verified rank rows give valid invariant
factor chains.  Invariant factors alone do not exclude a row.

## Bare integral orthogonality

Hadamard's determinant inequality is an equality because `T^2=3969I`.
Reapplying the determinant bound therefore gives no additional cut.

## Seidel switching as candidate normalization

Switching preserves the Seidel spectrum but does not preserve the regular
all-one eigenvector.  Normalizing a row without carrying the switched
exceptional eigenvector would silently assume extra symmetry.  No such
normalization is used.

## Most precise continuation

Useful next constraints must see the entry alphabet together with the Smith
filtration.  Candidate certificate-producing continuations are:

1. classify the 3-adic lifts forced by `T=7J (mod 9)`;
2. couple the 7-adic image filtration to the fixed diagonal 7;
3. apply exterior-square minors while retaining the `{16,-2}` off-diagonal
   labels;
4. encode one Smith-compatible row basis in proof-producing SAT/PB form.

Conway-99 and novelty remain `UNKNOWN`.

