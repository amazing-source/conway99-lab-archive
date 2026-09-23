# Wave 46 clean-room F7 code verification

Status: **scoped derivations and generic controls VERIFIED; null result
retained**.

The verifier froze its protocol, finite-field implementation, derivation
output, and tests before opening the Wave 46 discovery code or result. It
then reconstructed every archived positive control without importing the
discovery checker.

## Conditional projector-code consequences

At the conditional `n3=4158` endpoint, the supplied integral object is

```text
M=21E_0, order 231,
M^2=21M, M=M^T, M1=0,
M_ii=4, M_ij in {0,+1,-1}.
```

Modulo seven, `M^2=0`. Thus the row code `C=row_F7(M)` satisfies

```text
C subset C^perp,
C subset 1^perp.
```

Every column is nonzero because of its diagonal four. If two columns were
proportional, their two diagonal coordinates and common off-diagonal entry
would force `4=2x^2 mod 7` for `x in {0,+1,-1}`, which is impossible.
Consequently all 231 generator columns are projectively distinct and

```text
d(C^perp) >= 3.
```

These are conditional consequences; no concrete endpoint matrix or graph is
constructed.

## Compositions, weights, and moments

One distinguished row has composition

```text
(n0,...,n6)=(162,32,0,0,1,0,36).
```

Its six nonzero scalar multiples have six distinct compositions. Symmetry
and column projectivity put the 231 rows on distinct projective lines, so

```text
A69 >= 6*231 = 1386.
```

An independent residue dynamic program for coordinate sum and squared norm
zero excludes exactly weights `1,2,4`; all other weights through 231 are
congruence-compatible.

At rank 28, every conventional degree-zero, degree-one, and degree-two
complete-enumerator moment has strict slack after reserving the 1,386 known
words:

```text
minimum first slack:  15179555705976418712009901
minimum second slack: 498756830339225186222981718
```

The second value uses the falling diagonal moment `n_a(n_a-1)`, as complete
enumerator derivatives require. The pre-discovery freeze recorded the
equivalent raw-monomial basis `n_a^2`, whose minimum was
`498756830339225186256549252`. Both bases pass strictly; the distinction is
preserved rather than silently overwritten.

Passing degree two does not provide a complete enumerator.

## Schur cube

Entrywise cubing gives

```text
M^(o3)=M+4I.
```

Since `M^2=0 mod 7`,

```text
(M+4I)^(-1)=2I+3M.
```

The third Schur power therefore has full rank 231. Since
`dim Sym^3(C)<=binom(r7+2,3)`, this yields `r7>=11`. That floor is valid but
weaker than the previously verified endpoint floor `r7>=28`.

## Positive controls

The local `[21,4]_7` block consists of three affine lines:

```text
e0+t e1,
e2+t e3,
e0+e2+t(e1+e3),  t in F7.
```

Independent enumeration reproduces

```text
W21(z)=1+126z^12+18z^14+1470z^18+756z^19+30z^21.
```

The verifier rebuilt every archived projection and generator for
`r=28,...,44`. All 17 controls have:

- exact shape `[231,r]_7` and row rank `r`;
- zero Gram matrix and zero row sums;
- 231 nonzero, pairwise nonproportional columns;
- exact archived projection and generator-column hashes;
- inherited `A69>=668653683264`;
- zero matches among their generator-row scalar compositions to the six
  endpoint compositions.

The local-column SHA-256 is
`c663813eef11abeecae24cb3b1ac48cf774e7037b814d5333d1f307a815037a2`.
The aggregate projection-matrix SHA-256 is
`9bc5d02ba9c4a522a1ac8355002e3229ead59e166ea7a8fccbddab8ce45342e1`.

These are genuine generic ordinary-code controls, not endpoint projector
candidates.

## Prompt-error quarantine

The `99 x 99` object `A+3I` is different from `M`. Its eigenvalues are
`17,6,-1` with multiplicities `1,54,44`; its determinant is `3 mod 7`, so
its row code is all of `F7^99`. This calculation is correct and remains
explicitly unused by the live endpoint conclusion.

## Verdict

```text
projector-code implications:             VERIFIED, conditional
17 generic positive controls:            VERIFIED
ordinary-enumerator contradiction:       NONE
degree-two complete-enumerator conflict: NONE
new rank floor beyond 28:                 NONE
endpoint n3=4158:                         UNKNOWN
strict upper bound below 4158:            NOT PROVED
Conway-99 and novelty:                    UNKNOWN.
```

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave46-f7-code\independent_algebra.py `
  --verify verification\wave46-f7-code\independent-results.json

.\.venv\Scripts\python.exe -B `
  verification\wave46-f7-code\compare_sealed.py `
  --verify verification\wave46-f7-code\comparison-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave46-f7-code -p "test_*.py" -v

.\.venv\Scripts\python.exe -B `
  verification\wave46-f7-code\manifest_check.py
```
