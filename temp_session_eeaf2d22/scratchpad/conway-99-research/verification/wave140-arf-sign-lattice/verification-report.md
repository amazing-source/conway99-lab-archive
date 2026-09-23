# Independent verification of Wave 140

Verdict: `PASS_WITH_SCOPE_CORRECTION`.

The frozen discovery manifest has SHA-256
`934bbbd1818536af3786b9cb8b2f6bc48481d8bda3824328a266d5b3544ffd58`.
All eight listed payloads reproduced their sealed hashes.  The discovery
checker and its 11 tests pass; the clean-room checker and its 10 hostile tests
also pass.

## Verified claims

| claim | verdict | exact boundary |
|---|---|---|
| ambient even hyperplane has Arf sign `-1` | `VERIFIED` | exact binomial Gauss sum and rank-98 polar form |
| `epsilon(U)=(2/det(U))` | `VERIFIED` | for an even unimodular `Z_2` lattice with `q=(x,x)/2 mod 2` |
| opposite-sign binary projections | `VERIFIED` | symmetric, rank 54, idempotent mod 2, zero diagonal mod 2, and kill `1` |
| opposite-sign local `2`-adic allocations | `VERIFIED` | abstract even-unimodular spectral lattices with ranks `(54,44)` |
| full Smith list | `VERIFIED_CONDITIONAL` | follows from the previously verified modular ranks, determinant, and denominator-84 bound |
| same discriminant group, different discriminant forms | `VERIFIED_LOCAL` | standard even-lattice finite quadratic-form convention stated below |
| target Arf sign | `UNKNOWN` | neither control is an integral SRG adjacency |
| Conway 99 | `UNKNOWN` | no graph or nonexistence certificate |

## Clean-room derivation

Let

```text
K={x in Z_2^99 : x dot 1=0}.
```

In the basis `e_i-e_98`, its Gram matrix is `I+J`, so it is even,
unimodular over `Z_2`, has rank 98, and has determinant `99=3 mod 8`.
Reduction modulo two is the even-weight hyperplane.  Its polar form has
rank 98.  Independently summing by weights gives

```text
sum_(x even) (-1)^(wt(x)/2)
  = sum_(w even) (-1)^(w/2) binom(99,w)
  = -2^49.
```

The two even unimodular planes have:

```text
H_2: Gram [[0,1],[1,0]], det=7 mod 8, Gauss sign +1;
E_2: Gram [[2,1],[1,2]], det=3 mod 8, Gauss sign -1.
```

For an orthogonal sum with `e` copies of `E_2` and `h` copies of `H_2`,
the Gauss sign is `(-1)^e`, while

```text
(2/det)=(2/(3^e 7^h))=(-1)^e.
```

This proves the bridge under the stated lattice assumptions.  The verifier
checked it for every plane count through rank 98, not only the two selected
allocations.

On `K`, the roots `3` and `-4` differ by the two-adic unit seven.  Hence the
self-adjoint spectral projectors are integral, and an actual target would
split as

```text
K=U orthogonal_sum W,
rank(U)=54, rank(W)=44.
```

The two exact allocations reconstructed independently are

```text
plus:  U=4 E_2 + 23 H_2, det(U)=7, det(W)=5, epsilon(U)=+1;
minus: U=3 E_2 + 24 H_2, det(U)=3, det(W)=1, epsilon(U)=-1.
```

The two independently generated binary projectors reproduce the discovery
packed-matrix hashes exactly.

## Smith and discriminant checks

The denominator bound makes each invariant factor divide
`84=2^2*3*7`.  Divisibility ordering, determinant
`14*3^54*4^44`, and ranks `(54,45,98)` modulo `(2,3,7)` force

```text
1^45, 3^9, 6, 12^43, 84.
```

This reconstruction is exact but conditional on the already verified modular
rank inputs; Wave 140 does not newly derive those ranks.

For `L=A Z_2^99` with its inherited form, the local image decomposition has
one scale-2 line and 44 scale-4 directions.  Therefore both controls have
the abelian discriminant group

```text
Z/4 + (Z/16)^44.
```

Use the standard even-lattice convention

```text
q_L(x+L)=(x,x)/2 mod Z_2.
```

The exponent-16 Jordan block comes from `4W`, so its determinant unit records
`det(W)` modulo odd squares.  The two values `5` and `1` modulo eight differ,
and consequently the finite quadratic forms differ even though their groups
are isomorphic.  With the relevant Jordan block identified, the full form
would recover `det(W)`, hence `det(U)=det(K)/det(W)` and the Arf sign.

## Hostile scope check

The reconstructed binary matrices are not graph controls:

- their integer row sums are not all 14;
- treating their bits as integers fails
  `P^2=12I-P+2J`;
- idempotence holds only over `F_2`;
- no 99-by-99 integral local operator realizing the entrywise adjacency
  conditions is supplied.

Accordingly, the controls refute sign determination by the matched binary
projection data and local two-adic coarse invariants.  They do **not** refute
a proof using an actual integral zero-one, zero-diagonal, 14-regular SRG
adjacency, nor do they independently provide a global control matching
unconstructed odd-primary discriminant-form data.

This is the required scope correction to the broadest reading of
`derivation.md` section 5.  The narrower labels and limitations in
`exact-results.json` and `README.md` are accurate.  No discovery file was
silently repaired.

## Reproduction

```powershell
python -B attempts\wave140-arf-sign-lattice\exact_check.py
python -B -m unittest discover `
  -s attempts\wave140-arf-sign-lattice -p "test_*.py" -v
python -B verification\wave140-arf-sign-lattice\independent_verify.py
python -B -m unittest discover `
  -s verification\wave140-arf-sign-lattice -p "test_*.py" -v
```

The target sign and Conway-99 status remain `UNKNOWN`.
