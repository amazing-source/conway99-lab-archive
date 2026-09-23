# Wave 36 modular-reflection adversarial audit

Verdict: **PASS for every scoped modular claim, with a survivor-wording
qualifier**

Conditional on the independently verified `n3=4158` reflection package, the
submission correctly proves

```text
8 <= rank_F3(M) <= 44,
11 <= rank_F7(M) <= 44,
rank_F3(M)+rank_F7(M) is even,
```

and the Smith form of `C=2M-21I` is fixed by those two modular ranks.  Exactly
629 rank pairs satisfy these displayed floors, ceilings, and parity
condition.  They are arithmetic survivors of those conditions only, not
constructed matrices or a complete endpoint realizability classification.

No endpoint contradiction is obtained.  The upper bound remains `n3<=4158`,
and Conway-99 remains `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-26T22:49:38Z
git_commit: 697cc02bcbe16b69aaf08822298e03c66329c64c
claim_label: VERIFIED
audit_verdict: PASS_SCOPED_WITH_SURVIVOR_WORDING_QUALIFIER
scope: >-
  Conditional n3=4158 reciprocal Smith, mod-three projective,
  mod-seven symmetric-cube, index-parity, and 629-pair census claims only.
inputs:
  agents/2026-07-26-wave36-modular-reflection.md: 1a66e4acae92993f547c74745cfe6da7e53dfc185cf37da31d2590edcb6b558c
  attempts/wave36-modular-reflection/exact_check.py: e31b19e0252f4da323ec123b1b0cc70e9e10dd1cdc2278a7858288aae137289c
  attempts/wave36-modular-reflection/test_exact_check.py: 28db660565a301a8132b98b62f326f7677a17704931bb0d89cc40dd34cb8e323
  attempts/wave36-modular-reflection/exact-results.json: 5efcd507565a55fcdc3323448bf123ebec31ddc6eb9506a83258eff3c1468607
  attempts/wave36-modular-reflection/run-report.yaml: 64f8f8da46c34f070fb5e0fc9122747cf9d438121541ac1b01881612ba1127ed
  verification/wave36-modular-reflection/input-freeze.sha256: 701764efedbb5ae6bb302d1ed7acfd9c30b5a29f75deeb931d65b29f566fbd0d
method: >-
  Independent reconstruction of the human algebra plus a separately written
  standard-library checker and eleven hostile tests. The discovery module was
  not imported. Candidate inspection and replay followed the independent
  implementation.
command: |-
  .\.venv\Scripts\python.exe -B -m unittest -v verification/wave36-modular-reflection/test_independent_check.py
  .\.venv\Scripts\python.exe -B verification/wave36-modular-reflection/independent_check.py --verify verification/wave36-modular-reflection/independent-results.json
  .\.venv\Scripts\python.exe -B -m unittest -v attempts/wave36-modular-reflection/test_exact_check.py
  .\.venv\Scripts\python.exe -B attempts/wave36-modular-reflection/exact_check.py --output verification/wave36-modular-reflection/submitted-regenerated.json
outputs:
  verification/wave36-modular-reflection/independent_check.py: 3ecc0fbb52b326f4e496300d02ba97759f0deb738e49b85f0122052d1ca7f243
  verification/wave36-modular-reflection/test_independent_check.py: bd45721652bd059658e9a63054d7ded05d83d9095ff6fb2eba261b3f32331b78
  verification/wave36-modular-reflection/independent-results.json: 290d908ba2dbf70a411a432c0384ba98317dbe868c0177c721617bdad52eff23
  verification/wave36-modular-reflection/submitted-regenerated.json: 5efcd507565a55fcdc3323448bf123ebec31ddc6eb9506a83258eff3c1468607
limitations:
  - The graph-to-reflection bridge is inherited from the verified Wave 35 package.
  - No endpoint matrix, graph, or finite-field factor configuration is supplied.
  - The finite script accompanies rather than replaces the general linear-algebra proofs.
  - The 629 pairs are not asserted realizable.
  - No endpoint exclusion, upper-bound improvement, or novelty conclusion follows.
```

## 1. Frozen conditional premises

The verified Wave 35 package supplies, at the hypothetical prism-free
endpoint,

```text
C=2M-21I,
C^2=441I_231,
diag(C)=-13,
C_ij in {0,+2,-2},
(+2,-2,0) off-diagonal row counts=(32,36,162),
rank_Q(M)=44.
```

The previously verified projector-lattice package supplies

```text
h=3^(44-r3) 7^(44-r7),   h=1 mod 4,
```

where `r_p=rank_Fp(M)`.  Since `21=0` and `2` is a unit in
characteristics three and seven,

```text
rank_Fp(C)=rank_Fp(M)=r_p.
```

Every `45`-minor of `M` is zero over the integers because its rational rank
is 44.  Reduction modulo either prime therefore gives `r3,r7<=44`.

The audit treats these as frozen premises; it does not claim a second
independent reconstruction of the graph-to-reflection bridge.

## 2. Symmetric rank factorization

Let `A` be symmetric of rank `r` over a field of odd characteristic.  Choose
a full-column-rank matrix `V` spanning its column space.  Rank factorization
and symmetry give

```text
A=V H V^T
```

for an invertible symmetric `r`-by-`r` matrix `H`.  If `A^2=0`, then

```text
0=V H (V^T V) H V^T.
```

Multiplication by a left inverse of `V` and a right inverse of `V^T`, then by
`H^-1`, gives `V^T V=0`.  The rows `v_i` of `V` have Gram matrix `A` for
the nondegenerate bilinear form with matrix `H`.

Only the Gram interpretation is needed for the two rank floors.  No
positivity statement is made over a finite field.

## 3. Characteristic three

Modulo three, the factor rows have

```text
(v_i,v_i)=C_ii=2.
```

Thus all 231 rows represent anisotropic projective points.  They represent
distinct projective points:

- If `v_i=v_j`, rows `i,j` of `C` are congruent modulo three.  The residues
  of `{0,+2,-2}` are distinct, while `-13` has the residue of `+2`.
  Therefore the integer difference is exactly
  `-15(e_i-e_j)`, of squared Euclidean norm 450.
- If `v_i=-v_j`, the same residue check makes the integer sum exactly
  `-15(e_i+e_j)`, again of squared norm 450.
- But distinct rows of the symmetric matrix `C` are orthogonal and have
  squared norm 441 because `C^2=441I`.  Either their sum or difference has
  squared norm 882, contradicting 450.

Over `F_3`, equality and antipodality are the only possible nonzero
projective scalings.

The independent checker enumerates canonical representatives, with first
nonzero coordinate one, in both nondegenerate determinant classes.  The
numbers of norm-two projective points are:

| dimension | square determinant | nonsquare determinant |
|---:|---:|---:|
| 1 | 0 | 1 |
| 2 | 2 | 1 |
| 3 | 6 | 3 |
| 4 | 12 | 15 |
| 5 | 36 | 45 |
| 6 | 126 | 117 |
| 7 | 378 | 351 |

Dimension at most six cannot contain the 231 distinct points, giving
`r3>=7`.  If `r3=7`, the orthogonal complement of any norm-two point is a
nondegenerate six-space.  The row profile supplies 162 distinct norm-two
points in that complement, but the table permits at most 126.  Hence

```text
r3>=8.
```

The strict inequality `162>126` is active; the hostile equality threshold
does not certify rank eight.

## 4. Characteristic seven and the symmetric tensor cube

Here `C_ii=1` and every off-diagonal entry lies in `{0,+2,-2}` modulo seven.
For clarity, this audit uses

```text
Sym^3(V) = the symmetric tensors inside V tensor V tensor V.
```

It contains every pure cube

```text
w_i=v_i tensor v_i tensor v_i
```

and, because the tensor degree is three in characteristic seven, has the
usual monomial dimension

```text
dim Sym^3(V)=binom(r7+2,3).
```

Under the tensor-product bilinear form,

```text
(w_i,w_j)=(v_i,v_j)^3,
```

so the Gram matrix of the cubes is the entrywise cube `C^(o3)`.  For the
off-diagonal alphabet, `t^3=4t mod 7`.  On the diagonal,

```text
1^3=1=4(1+1) mod 7.
```

Therefore

```text
C^(o3)=4(I+C) mod 7.
```

Since `C^2=0 mod 7`,

```text
(I+C)(I-C)=I,
```

and the displayed Gram matrix is invertible.  If a linear combination of
the `w_i` vanished, pairing it with all `w_j` would put its coefficient
vector in the kernel of this Gram matrix.  Thus all 231 cubes are linearly
independent.  This implication does not require the bilinear form restricted
to all of `Sym^3(V)` to be nondegenerate.

Finally,

```text
dim Sym^3(F_7^10)=binom(12,3)=220 < 231,
dim Sym^3(F_7^11)=binom(13,3)=286.
```

Hence

```text
r7>=11.
```

## 5. Reciprocal Smith form

The relation `C^2=441I` makes `C` nonsingular, so there are 231 positive
Smith invariant factors and no zero factors:

```text
d1 | d2 | ... | d231.
```

Moreover, `441 Z^231=C^2 Z^231` is contained in `C Z^231`.  Thus every
class in `coker(C)` is killed by 441, the largest Smith factor divides 441,
and hence every `d_i` divides 441.

Now

```text
C=441 C^-1.
```

Starting with a Smith decomposition of `C`, the diagonal entries for the
right side are `441/d_i`.  Their divisibility order is reversed, so
uniqueness of Smith form gives

```text
d_i d_(232-i)=441.
```

For either `p=3` or `p=7`, the number of factors with valuation zero is
`r_p`.  Reciprocal pairing forces the complete exponent profile

```text
0^r_p, 1^(231-2r_p), 2^r_p.
```

The two nondecreasing valuation profiles align uniquely.  If `r3<=r7`, the
full form is

```text
1^r3, 3^(r7-r3), 21^(231-2r7), 147^(r7-r3), 441^r3.
```

If `r7<=r3`, it is

```text
1^r7, 7^(r3-r7), 21^(231-2r3), 63^(r3-r7), 441^r7.
```

The central factor is 21, as reciprocal pairing in odd dimension also
requires.  The independent checker validates ordering, divisibility,
modular ranks, central factor, reciprocal products, and total determinant
`21^231` for every one of the 629 displayed rank pairs.  It also tests both
rank-order cases separately.

## 6. Index parity and census

From the frozen index formula and `h=1 mod 4`,

```text
h=3^(44-r3) 7^(44-r7)
```

has an even total exponent because both bases are `-1 mod 4`.  Therefore

```text
r3+r7 is even.
```

There are 19 even and 18 odd values in `[8,44]`, and 17 even and 17 odd
values in `[11,44]`.  The number of equal-parity pairs is exactly

```text
19*17+18*17=629.
```

The hostile pair `(8,11)` gives `h=3 mod 4` and is correctly rejected.  The
largest permitted index valuations are

```text
v3(h)<=36,  v7(h)<=33.
```

This is a complete census under the four displayed constraints
`8<=r3<=44`, `11<=r7<=44`, and even rank sum.  It is not an existence
theorem and does not assert that other, as-yet-unused endpoint conditions
cannot reduce the list further.

## 7. Executable replay and final boundary

The independent standard-library suite passed:

```text
Ran 11 tests
OK
```

The submitted suite separately passed:

```text
Ran 11 tests
OK
```

Regenerating the submitted JSON produced SHA-256

```text
5efcd507565a55fcdc3323448bf123ebec31ddc6eb9506a83258eff3c1468607,
```

byte-for-byte identical to the submitted result.

| Obligation | Result |
|---|---:|
| Frozen inherited premise hashes | PASS |
| Symmetric rank factorization | PASS |
| Mod-three equal/antipodal row contradiction | PASS |
| Both ternary determinant-class counts through dimension seven | PASS |
| Six-space orthogonal-companion obstruction | PASS |
| Definition and dimension of `Sym^3(V)` | PASS |
| `C^(o3)=4(I+C) mod 7`, including the diagonal | PASS |
| Invertible cube Gram implies 231 independent cubes | PASS |
| Symmetric-cube boundary `220<231<=286` | PASS |
| Nonsingularity and absence of zero Smith factors | PASS |
| Reciprocal Smith pairing and both rank-order formulas | PASS |
| Index parity and exact 629-pair enumeration | PASS |
| Submitted tests and deterministic regeneration | PASS |
| Endpoint exclusion | NOT OBTAINED |
| Upper bound below 4158 | NOT OBTAINED |
| Endpoint matrix or graph | NOT CONSTRUCTED |
| Novelty | NOT ASSESSED |

Final scoped status:

```text
rank_F3(M)>=8: VERIFIED
rank_F7(M)>=11: VERIFIED
full Smith form from (r3,r7): VERIFIED
even rank sum and 629-pair census: VERIFIED WITH SURVIVOR QUALIFIER
endpoint n3=4158: survives
Conway-99: UNKNOWN
```
