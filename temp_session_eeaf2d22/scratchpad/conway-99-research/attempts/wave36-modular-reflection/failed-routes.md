# Wave 36 retained modular/reflection limits

These failures are not evidence that the endpoint exists.  They delimit what
the present modular identities prove without importing unverified graph or
incidence assumptions.

## 1. Square-zero row codes do not contradict dimension 44

For `p=3,7`, the image of `C mod p` is totally isotropic because

```text
C^2=0 mod p.
```

The ambient standard quadratic space has dimension 231 and Witt index at
least 115, while `rank_Fp(C)<=44`.  Self-orthogonality alone is therefore far
too weak.  No minimum distance for the row code is known, so standard
self-orthogonal-code bounds cannot be applied as if the displayed row
weight 69 were the code minimum.

## 2. Characteristic three loses the diagonal alphabet

Modulo three, the diagonal value `-13` and the off-diagonal value `+2` are
both `2`.  Also every field element satisfies `x^3=x`.  Thus the successful
characteristic-seven cubic diagonal isolator has no characteristic-three
analogue.  Factoring the symmetric matrix and using integral orthogonality
does prove that the 231 factor rows occupy distinct projective points, and
the 162 orthogonal companions improve the rank floor to eight.  The
dimension-eight finite quadratic space is still large enough; this route
stops without a higher incidence moment.

## 3. Characteristic seven stops at rank eleven

The exact identity

```text
C^(o3)=4(I+C) mod 7
```

makes 231 symmetric cubes independent and forces

```text
binom(r7+2,3)>=231,
r7>=11.
```

But `binom(13,3)=286`, so rank eleven survives the dimension count.  The
argument supplies no reason that an endpoint must have `r7>=45`; hence it
does not contradict the rational rank 44.

## 4. Smith reciprocity still leaves 629 rank pairs

The identity `C^2=441I` and `C mod 2=I` force reciprocal Smith factors, and
the modular bounds plus the verified index parity reduce the possibilities
to 629 pairs `(r3,r7)`.  This is finite bookkeeping, not a classification of
integral matrices.  None of the 629 shapes is realized here, but none is
excluded merely by its invariant factors.

## 5. No determinant contradiction

The reflection spectrum already gives

```text
|det C|=21^231.
```

The reciprocal Smith shapes have exactly this determinant and satisfy all
displayed parity requirements.  Determinant magnitude and sign therefore do
not improve the upper bound.

## Continuation

A useful next modular target would couple a rooted incidence partition to the
factor vectors and force either:

1. at least 45 independent rows modulo 3 or 7, contradicting
   `rank_Q(M)=44`; or
2. an impossible distribution of the 162 orthogonal and 32/36 signed
   companions inside one of the finite quadratic spaces.

No such coupling is established in this lane.
