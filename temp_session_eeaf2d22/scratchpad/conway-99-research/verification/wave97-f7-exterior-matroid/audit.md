# Wave 97 independent exterior/matroid audit

Date UTC: 2026-07-28

## Verdict

**`VERIFIED_WITH_PROVENANCE_CORRECTION`.**

Every substantive mathematical formula in the Wave 97 discovery package
passes independent reconstruction. In particular, the initially suspicious
terminal Smith factor is correct:

```text
SNF(C2(S)) at r=28
 = diag(
     1^378,
     7^1204,
     49^1687,
     343^1204,
     2401^280,
     24010^98
   ).
```

The correction concerns repository provenance, not the formula. Verified
Wave 51 had already established that the 99 quadratic pure-square images
have rank 98 and the unique all-one relation. Consequently:

- `R*R=1_perp` was already an immediate Wave 51 consequence, even though
  Wave 97 gives a cleaner code-product proof;
- the 99 quadratic images forming a circuit was already an immediate
  Wave 51 consequence; and
- every 98 being independent and the degree-two Cayley--Bacharach property
  are equivalent restatements of that same prior result.

The genuinely later repository consequences include the full Schur cube,
`C*C`, the second-compound code and Smith form, its row geometry and
spectrum, the generalized-weight intervals, and the exact orthogonal
embedding/orbit reduction. Literature novelty remains `UNKNOWN`.

Rank 28 is not excluded. No strict `n3` upper bound, graph construction, or
Conway-99 resolution follows.

## Freeze and independence

All 11 discovery files were frozen by path, byte length, and SHA-256 before
the derivation was inspected. The discovery manifest hash is

```text
dd7869bd8f9041014087cac1e1840763794a4e8d52f2c701262d7ec009515bec
```

and all ten entries validate. The seven imported Wave 46, Wave 51, Wave 80,
and `AGENTS.md` hashes also match the discovery input freeze.

`independent_verify.py` imports no discovery code. It uses separate
finite-field elimination, compound matrices, local-prime Smith assembly,
determinantal divisors, small-dimensional quadratic-form enumeration, and
exact integer arithmetic.

## 1. Schur powers and Hilbert function

Put `R=row_F7(S)`. Since `S` is symmetric and `S^2=0 mod 7`, all rows of
`S` are mutually orthogonal. Thus for `x,y in R`,

```text
sum_i (x_i*y_i) = x dot y = 0,
```

so `R*R` lies in the coordinate-sum-zero hyperplane `1_perp`.

The diagonal of `S` is zero and every off-diagonal entry is `+1` or `-1`.
For row `s_i`,

```text
s_i*s_i = 1-e_i.
```

These are the rows of `J-I`. Over `F7`, `99=1`, so `J-I` has kernel
`<1>`, rank 98, and row space `1_perp`. Therefore

```text
R*R = 1_perp.
```

This direct equality is correct, but it is prior-implied by Wave 51:
polarization in odd characteristic turns the verified rank-98 pure-square
span into the full quadratic Schur product.

The cube is a genuinely stronger consequence. For `i!=j`,
`e_i-e_j` lies in `R*R`, and

```text
s_j*(e_i-e_j) = S[j,i] e_i.
```

The off-diagonal coefficient is nonzero, so every coordinate vector lies
in `R*R*R`. Hence

```text
R*R*R = F7^99.
```

At `r=28`, the homogeneous evaluation dimensions and first differences are

```text
H(0),H(1),H(2),H(3) = (1,28,98,99),
Delta H                = (1,27,70,1).
```

The symmetric-square and symmetric-cube evaluation kernels have dimensions
`406-98=308` and `4060-99=3961`.

Wave 80 gives a nondegenerate quotient `C/R`. Thus some `c,d in C` satisfy
`c dot d !=0`, and the coordinate sum of `c*d` is nonzero. Since `C*C`
already contains the hyperplane `R*R`, this proves

```text
C*C = F7^99.
```

## 2. Second-compound code

For

```text
E=C2(S),  E[I,J]=det S[I,J],
```

the row and column index set has size `C(99,2)=4851`. The verifier
materializes small independent controls and confirms both compound
Cauchy--Binet and

```text
rank_F7 C2(S) = C(rank_F7 S,2).
```

At `r=28`, the rank is `C(28,2)=378`. Symmetry of `S` makes `E` symmetric,
while

```text
E^2 = C2(S^2) = 2401 C2(I+J).
```

Consequently `E^2=0 mod 7`, and its row code is self-orthogonal with
parameters

```text
[4851,378]_7.
```

Wave 80's `d(R^perp)>=6` says every set of at most five columns of `S` is
independent. A compound column is a wedge of two source columns, so it is
nonzero. Two proportional nonzero decomposable wedges determine the same
two-plane. Distinct source pairs would then put a union of three or four
columns in one two-plane, contradicting the five-column independence.
Therefore the 4,851 compound columns are projectively distinct and the
compound dual distance is at least three.

## 3. Distinguished row weight

Fix row pair `{a,b}`.

- Its diagonal compound entry is `-1`.
- Exactly `2*(99-2)=194` columns overlap the pair in one vertex, and every
  such minor is `+1` or `-1`.
- For a disjoint column pair `{c,d}`, the minor is zero precisely when
  `S[a,c]/S[b,c] = S[a,d]/S[b,d]`.

If `a,b` are adjacent, the remaining vertices have intersection profile

```text
(both, a-only, b-only, neither) = (1,12,12,72).
```

If they are nonadjacent, the profile is `(2,12,12,71)`. In both cases the
two ratio classes have sizes 73 and 24. Therefore

```text
disjoint nonzero entries = 73*24 = 1752,
disjoint zero entries    = C(97,2)-1752 = 2904,
row weight               = 1+194+1752 = 1947.
```

The integral row square norm is

```text
1+194+4*1752 = 7203 = 3*2401,
```

matching the diagonal of the compound square identity. Symmetry and
projectivity give 4,851 distinguished projective lines and 29,106 nonzero
scalar multiples of weight 1,947.

## 4. Complete Smith form and the `24010` attack

Wave 51 supplies

```text
SNF(S)=diag(1^r,7^b,49^(r-1),490),  b=99-2r.
```

If `S=UDV` is an integer Smith equivalence, then

```text
C2(S)=C2(U) C2(D) C2(V).
```

The compounds of the unimodular matrices are unimodular, while `C2(D)` is
diagonal with every pairwise product of source invariant factors.

For the prime 7, the source exponents are

```text
0^r, 1^b, 2^r.
```

Their pair sums have multiplicities

| exponent | multiplicity |
|---:|---:|
| 0 | `C(r,2)` |
| 1 | `r*b` |
| 2 | `r^2+C(b,2)` |
| 3 | `r*b` |
| 4 | `C(r,2)` |

The unique source factor 490 is the only factor divisible by 2 or 5.
Exactly 98 raw exterior products use it, so the sorted 2-adic and 5-adic
lists end with 98 ones.

The crucial Smith-normalization point is that invariant factors align the
independently sorted local exponent lists. They are not the raw pair
products in their original positions. For every live rank,
`C(r,2)>=378>=98`, so all 98 terminal 2- and 5-parts align with terminal
7-exponent-four positions. The result is

```text
1^C(r,2),
7^(r*b),
49^(r^2+C(b,2)),
343^(r*b),
2401^(C(r,2)-98),
24010^98.
```

At `r=28,b=43`, the multiplicities are exactly

```text
378, 1204, 1687, 1204, 280, 98.
```

Only 27 raw products are themselves `49*490=24010`; Smith recombination
raises the final `24010` multiplicity to 98. This is not an error.

The verifier independently checks a four-factor toy case:

```text
source Smith: [1,7,49,490]
compound Smith: [7,49,49,3430,3430,24010].
```

Every prefix product equals the gcd of the corresponding diagonal minors.
It also changes the hostile rank to 14, where only `C(14,2)=91` terminal
7-exponent-four slots exist; the result then has seven `3430` factors and
only 91 `24010` factors. This proves the live-rank inequality is essential.

All eight live rows pass. Their determinant valuations are uniformly

```text
v2=98, v5=98, v7=9702.
```

## 5. Spectrum and square identity

The corrected Wave 51 spectrum is

```text
-70^1, 7^54, (-7)^44.
```

Pairwise products independently give

```text
490^44, (-490)^54, 49^2377, (-49)^2376.
```

The multiplicities sum to 4,851 and the trace is `-4851`, agreeing with the
constant compound diagonal `-1`. The same spectrum reproduces the three
determinant valuations above. Also

```text
SNF(C2(I+J)) = diag(1^4753,100^98),
```

consistent with the square identity.

## 6. Generalized Hamming weights

At rank 28, `R^perp` is `[99,71]_7`. A coordinate set supporting a
`j`-dimensional subcode has matroid nullity at least `j`. It contains a
circuit; five-column independence makes every circuit size at least six
and rank at least five. Therefore the support size, rank plus nullity, is
at least

```text
d_j(R^perp) >= j+5.
```

Generalized Singleton gives `d_j<=j+28`. All 71 intervals have slack. Since
`C` lies in `R^perp` and Wave 80 forces a word of weight 14, 16, or 18,
only the first interval improves to

```text
6 <= d_1(R^perp) <= 18.
```

No matroid contradiction follows.

## 7. Orthogonal orbits

Wave 80 already fixes the types

```text
O^-(42,7) = O^-(16,7) perpendicular O^+(26,7).
```

Witt extension makes the ambient orthogonal group transitive on
nondegenerate minus-type 16-subspaces with this complement. The stabilizer
is the product of the two factor orthogonal groups, so the orbit size is

```text
|O^-(42,7)| / (|O^-(16,7)| |O^+(26,7)|),
```

the same 352-digit integer archived by discovery.

For a minus-type `2m`-space over an odd field of order `q`, the nonzero
isotropic-vector count is

```text
(q^(m-1)-1)(q^m+1),
```

and every fixed nonzero norm has `q^(2m-1)+q^(m-1)` vectors. At
`m=8,q=7`, the projective orbit sizes are

```text
isotropic             791259428114
square anisotropic   2373781166743
nonsquare anisotropic 2373781166743
total                5538821761600.
```

The verifier brute-forces an independent four-dimensional minus-type form
over `F7` and exactly reproduces the same formulas in the smaller case.

Self-dots 4 and 1 differ by the square 4, so the norm-16 and norm-18 classes
belong to the same square-anisotropic projective orbit. Self-dot zero is
either the zero quotient class or a nonzero isotropic line.

Hostile sign changes expose an important limitation: replacing the ambient
or complement sign still produces integral order ratios. Divisibility alone
does not certify the signs. The verified Wave 80 discriminant and Witt-index
calculation is essential.

## Hostile controls and boundary

Fifteen independent tests pass. They cover:

- order 98 instead of 99 in the Schur-square rank;
- small exact compound Cauchy--Binet and every source rank zero through four;
- all eight live Smith rows;
- raw pair products versus true invariant factors;
- determinantal divisors and the hostile rank-14 alignment;
- adjacent and nonadjacent row-weight tables;
- corrected versus transposed spectral multiplicities;
- projective wedge collisions;
- every generalized-weight interval;
- small brute-force minus-space point counts;
- wrong orthogonal signs;
- prior-versus-new repository provenance;
- canonical replay and frozen-input drift; and
- fail-closed target status.

The mathematical comparison has zero mismatches. The final outcome is a
provenance correction with verified mathematics:

```text
rank 28 excluded:                    NO
strict n3 upper bound below 4158:   NOT PROVED
Conway-99:                          UNKNOWN
literature novelty:                 UNKNOWN
```

## Reproduce

```powershell
python -B verification/wave97-f7-exterior-matroid/independent_verify.py `
  --verify verification/wave97-f7-exterior-matroid/independent-results.json
python -B -m unittest discover `
  -s verification/wave97-f7-exterior-matroid `
  -p "test_*.py" -v
```
