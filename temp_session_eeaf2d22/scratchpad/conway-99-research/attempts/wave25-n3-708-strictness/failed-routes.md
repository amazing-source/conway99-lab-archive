# Wave 25 retained hostile, incomplete, and non-excluding routes

None of the items below is evidence that Conway-99 exists or does not exist.
They delimit the strict `n3=708` refinement and prevent its hypotheses from
being silently weakened.

## 1. The strict determinant refinement does not exclude `n3=708`

The equality obstruction improves

```text
tr(C^2) >= 8   to   tr(C^2) >= 10
det(B) <= 6561 to   det(B) < 6561.
```

After all inherited factorization and congruence conditions are imposed, the
largest arithmetically allowed product becomes

```text
det(B)=h det(Q) <= 9*725 = 6525.
```

There are still 323 arithmetic `(h,det(Q))` pairs over the same eight values
of `h`.  These are necessary arithmetic survivors, not lattice or graph
constructions.

## 2. `S=Q^-1` is false globally

In an integral basis of `L`,

```text
S=21G^-1,
Q=GB/21,
S Q=B.
```

Only on the hypothetical equality kernel `K=ker(C)`, where `B|K=I`, does
the restricted identity become

```text
S_K Q_K=I_K.
```

The frozen Wave 24 survivor is an explicit hostile control.  It has

```text
det(S)=9, det(Q)=9, det(B)=81,
S Q=B!=I.
```

Any proof that replaces the global product by `S=Q^-1` is rejected.

## 3. Evenness cannot be omitted

The diagonal equality package

```text
C=diag(1^8,0^36),
B=diag(3^8,1^36),
G=21I,
S=I,
Q=B
```

satisfies

```text
SG=21I,
GB=21Q,
SQ=B,
tr(C)=tr(C^2)=8,
det(B)=6561.
```

It survives only because `G`, `S`, and `Q` are odd forms.  It violates the
verified even-lattice premises.  Thus the equality contradiction must retain
the derivation that `S=21G^-1` is even (and, redundantly, the inherited
evenness of `Q`).  Integrality and positivity alone do not activate the
even-unimodular signature theorem.

## 4. A nonintegral idempotent does not split the lattice

Eight copies of

```text
(1/2) [[1,1],[1,1]]
```

together with 28 zero coordinates give a rational symmetric idempotent on
`Q^44` with

```text
rank=8,
tr(C)=tr(C^2)=8.
```

Its real image and kernel are orthogonal, but their integral intersections
sum to a sublattice of index `2^8=256` in `Z^44`.  Therefore real
idempotence does not imply the integral direct sum used in the proof.
Integrality of `C` is active.

## 5. The signature contradiction is rank-sensitive

If the ambient rank were mutated from 44 to 40 while the equality image
remained rank eight, the kernel would have rank 32.  The checker reconstructs
`E8^4`, an even positive-definite unimodular rank-32 form.  Hence the
signature theorem supplies no contradiction in that mutation.  The actual
kernel rank `36=4 mod 8` is essential.

## 6. Congruence omissions inflate the cap

The exact controls give:

| Relaxation | largest enumerated `det(B)` |
|---|---:|
| all verified conditions | 6525 |
| omit `det(Q)=1 mod 4`, retain oddness | 6543 |
| omit all parity/congruence on `det(Q)` | 6552 |
| omit `h=1 mod 4` | 6559 |
| wrongly allow equality `det(B)=6561` | 6561 |

The last mutation restores exactly the three spurious equality pairs

```text
(h,det(Q))=(9,729),(81,81),(729,9).
```

The combined cap `6525` is therefore a factorization-and-congruence cap, not
merely the largest integer below `6561`.

## 7. The abstract Wave 24 survivor remains

The verified `h=9`, `det(Q)=9`, `det(B)=81` coordinate-lattice survivor has
`tr(C^2)=32`, so it passes the new floor and strict determinant bound.  It
still has no proved:

- primitive embedding in `Z^231`;
- 231-vector projector/Hadamard origin;
- `W=M o M` origin; or
- graph realization.

No endpoint exclusion follows.

## 8. Retained harness correction

The first 21-test run had one failure in a string-level test: the certificate
contained the correct identity

```text
<Cx,y>=<x,Cy>=0
```

but the test also required the literal word `orthogonality`.  No arithmetic
or mathematical assertion failed.  The certificate label was made explicit,
and a fresh full run passed all 21 tests.  The failed run is retained here
for auditability and is not used as evidence.
