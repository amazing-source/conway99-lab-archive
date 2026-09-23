# Wave 23 projector-index endpoint attack

```yaml
role: proof_b
date_utc: 2026-07-23T19:15:16Z
git_commit: NOT_USED_PER_TASK_INSTRUCTION
claim_label: DERIVED
scope: >
  Conditional exclusion of the first surviving Wave 20 endpoint n3=705 by
  strengthening the verified projector-lattice determinant argument.
inputs:
  verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md: 45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268
  verification/2026-07-23-wave20-global-schur-audit.md: 6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3
  agents/2026-07-23-wave21-lattice-extension.md: 264027dc534d57aefd8f4d9037d041af2ca8e462efeb9ef22d07de4c40141b3e
method: >
  Exact Smith/rank bookkeeping, modular incidence reductions, an integral
  near-identity trace-square floor, a rigorous two-moment determinant
  optimization with all 38 radical cases certified by rational brackets, and
  an even-unimodular obstruction to h=1.
command: |
  cd attempts/wave23-index-pranks
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
outputs:
  attempts/wave23-index-pranks/exact_check.py: bc8810043de2f27f52186fc19dfae3a4df5231db5dc7fd591ab0a537d6857048
  attempts/wave23-index-pranks/test_exact_check.py: 582022f36784f62c3f95e6da8b7b9ba600d73da2d8adcb65222d42efff131c35
  attempts/wave23-index-pranks/exact-results.json: 64bf8192018376961ec88562d64928f73514697000c73cbf79a4a2a2def923b5
  attempts/wave23-index-pranks/input-freeze.sha256: 4c0492be4fe1c5a1bd6afdc1303e1457b0c92c43ca7ab22366384e469bfeb8b6
  attempts/wave23-index-pranks/failed-routes.md: 1371323a35959482a888fd3eaf226995eaae99e05800cde889ad239dcccabc65
  attempts/wave23-index-pranks/run-report.yaml: 578a1f1c3af25452aaaf675c3b68c762fd6366f3a7b0e66d03361766b6351c72
limitations:
  - This is a discovery-agent derivation pending independent adversarial verification.
  - No actual 231-by-231 M or 99-vertex graph is instantiated.
  - Neither rank_F3(M), rank_F7(M), nor h is determined away from the rejected endpoint.
  - Target existence and literature novelty remain UNKNOWN.
```

## Result

The independently verified Wave 21 lattice package can be strengthened enough
to reject its last two endpoint index values.  Conditional on a putative
`srg(99,14,1,2)`, the Wave 20 count therefore satisfies

```text
n3 != 705.
```

Since the audited combinatorics already gives `3 | n3` and `n3>=705`, the
new discovery-agent bound is

```text
n3 >= 708,
induced_C6 >= 209994.
```

This is not yet `VERIFIED`.  The two-moment extremum and the `h=1` lattice
step need a genuinely independent adversarial reconstruction before any
central status is promoted.  The result remains conditional on target
existence and does not resolve Conway-99.  Novelty is `UNKNOWN`.

## 1. Frozen verified lattice input

Use the notation already audited in Wave 21:

```text
U = im(M) over Q,
L = U intersect Z^231,
h = [L:21L*],
W = M o M,
A4 = M W M,
B = A4/21 on U.
```

The verified facts used here are:

```text
rank(L)=44;
L is even;
MZ^231=21L*;
h=21^44/det(L);
B is a positive-definite integral self-adjoint endomorphism of L;
B=I mod 2 End(L);
tr(B)=4 Delta;
det(B)=h det(Q);
Q=X^T W X is even, integral, and positive definite;
det(B)=1 mod 4.
```

At the endpoint `n3=705`, `Delta=12`, hence

```text
tr(B)=48.
```

The Wave 21 verifier also supplied the exact even-Gram congruence

```text
det(Q)=1 mod 4.
```

Since an even positive-definite unimodular lattice cannot have rank 44,
`det(Q)` is not one.  It is odd, so

```text
det(Q)>=5.
```

The previously verified endpoint reduction was

```text
h in {1,9}.                                      (1)
```

## 2. Smith and modular-rank bookkeeping

The inclusions

```text
21L subset MZ^231=21L* subset L
```

show that the 44 nonzero Smith factors of `M` lie in
`{1,3,7,21}`.  Their product is the top determinantal divisor

```text
Delta_44(M)=[L:MZ^231]=h.
```

Consequently the exact rank formula is

```text
h
 = 3^(44-rank_F3(M)) 7^(44-rank_F7(M)).         (2)
```

In particular, the two old endpoint cases correspond to

```text
h=1: (rank_F3(M),rank_F7(M))=(44,44),
h=9: (rank_F3(M),rank_F7(M))=(42,44).
```

This makes clear what a direct modular-rank proof would have needed.  The
following reductions are parameter-forced but do not determine either rank.

### Characteristic seven

Let `N` be the `99`-by-`231` vertex/triangle incidence matrix and put

```text
R=3I-A+J/9.
```

Then `M=N^T R N`.  Modulo seven, `N` has full row rank.  Indeed,
`N^T x=0` implies

```text
Ax=NN^T x=0.
```

The verified adjacency rank has kernel `<1>`, while
`N^T1=3*1` is nonzero modulo seven.  Thus `N` is surjective and `N^T` is
injective, giving

```text
rank_F7(M)=rank_F7(R).
```

For the Seidel matrix

```text
S=2A-J+I,
```

one has `5R=S mod 7`.  Exact multiplication in the adjacency algebra gives

```text
S^2=49(I+J).                                    (3)
```

Therefore `rank_F7(M)=rank_F7(S)`, but (3) only says that the reduction is
square-zero.  It does not fix its rank.  Treating the rational `+7` and `-7`
eigenspaces as integrally split would beg the index question.

### Characteristic three

The same projector factorization gives the exact rectangular identity

```text
NM=3(3I-A)N+J,
```

and hence

```text
NM=J mod 3.                                    (4)
```

Also

```text
55 <= rank_F3(N) <= 98:
```

the lower bound comes from the verified rank
`rank_F3(NN^T)=rank_F3(A+I)=55`, and the upper bound from
`N^T1=0`.  Equation (4) does not distinguish rank 44 from rank 42 for `M`.
No unproved saturation of the triangle incidence columns is assumed.

## 3. A new exact second-moment floor for B

Write the integral coordinate matrix of the endomorphism as

```text
B=I+2C.
```

At the endpoint,

```text
tr(C)=(48-44)/2=2.                             (5)
```

For every integral square matrix,

```text
tr(C^2)=tr(C) mod 2,                           (6)
```

because the off-diagonal contributions to `tr(C^2)` pair and
`C_ii^2=C_ii mod 2`.

The endomorphism `C` is self-adjoint for the positive Gram form of `L`.
It is therefore diagonalizable over the reals with real eigenvalues.
Equation (5) makes it nonzero, so `tr(C^2)>0`.  Equations (5)--(6) force

```text
tr(C^2)>=2.
```

Expanding the square now gives the exact floor

```text
tr(B^2)
 =44+4tr(C)+4tr(C^2)
 >=44+8+8
 =60.                                          (7)
```

This uses only the already-verified near-identity endomorphism, not a local
diagonal profile or a putative matrix instance.

## 4. Rigorous two-moment determinant cap

Let `x_1,...,x_44` be the positive real eigenvalues of `B`.  Equations (5)
and (7) give

```text
sum_i x_i=48,
sum_i x_i^2>=60.                               (8)
```

We claim

```text
product_i x_i < 13.                            (9)
```

Here is a complete extremum argument, including the inequality boundary.
Take the compact closure of the feasible region defined by (8) and
`x_i>=0`.  A point with spectrum

```text
3,3,1^42
```

is feasible and has positive product nine.  Hence a product maximizer is not
on a coordinate boundary; every `x_i` at the maximizer is positive.

If its square sum were strictly greater than 60, the inequality constraint
would be inactive.  Lagrange multipliers for the sum constraint alone would
make all 44 coordinates equal.  That equal point has square sum

```text
44(48/44)^2=576/11<60,
```

a contradiction.  Thus the square-sum constraint is active.

The gradients of the sum and square-sum constraints are independent because
the coordinates are not all equal.  Lagrange stationarity for the logarithm
of the product gives

```text
1/x_i = alpha + beta x_i.
```

Therefore every `x_i` is a positive root of one fixed quadratic and the
stationary spectrum has at most two values.  If the larger value `a` occurs
`k` times and the smaller `b` occurs `44-k` times, solving the two moments
gives

```text
a = [12+sqrt(21(44-k)/k)]/11,
b = [12-sqrt(21k/(44-k))]/11.                 (10)
```

Positivity of `b` is exactly

```text
144(44-k)>21k,
```

so the complete list is `k=1,...,38`.

The checker certifies all 38 cases without floating point.  For every
radicand it records

```text
floor(10^12 sqrt(r))
```

using integer `isqrt` and checks the two exact squared inequalities.  It
uses an upper radical bracket for `a` and a lower radical bracket for `b`,
then raises the resulting rational upper bounds to the exact integer powers.
Every rational product upper bound is strictly below 13.  The largest
certified upper case is `k=1`, below

```text
12.211911548... < 13.
```

The displayed decimal is informational; the stored rational comparison
decides (9).  A hostile mutation from square sum 60 to 59 no longer
certifies the cap.

Since `B` is an integral endomorphism, its determinant is a positive integer.
Together with `det(B)=1 mod 4`, (9) leaves only

```text
det(B) in {1,5,9}.
```

But `det(B)=h det(Q)` and `det(Q)>=5`, so in fact

```text
det(B) in {5,9}.                               (11)
```

Combining (1), (11), and `det(Q)>=5` eliminates `h=9`, which would require
`det(B)>=45`.  The only arithmetical endpoint survivor is now `h=1`.

## 5. The index h=1 is impossible

This last step is independent of the determinant optimization and is exact.
Choose an integral basis of `L` with Gram matrix `G`.  In those coordinates,
the equality `h=1` means

```text
L=21L*,
21G^(-1) Z^44=Z^44.
```

Thus `21G^(-1)` is an integral unimodular matrix.  Its inverse

```text
H=G/21
```

is also integral and unimodular.

The matrix `G` is positive definite and even.  Since 21 is odd and `H` is
integral, every diagonal entry of `H` is even.  Therefore `H` is the Gram
matrix of an even positive-definite unimodular lattice of rank 44.

The van der Blij signature obstruction requires the signature of an even
unimodular lattice to be divisible by eight.  Positive rank 44 has signature
44, not divisible by eight.  Hence

```text
h != 1.                                       (12)
```

Equations (1), (11), and (12) leave no endpoint index at all.  This proves
the stated discovery-agent exclusion of `n3=705`.

## 6. Exact replay and hostile checks

The standard-library checker uses only integers and `fractions.Fraction`.
Its 15 tests cover:

- all 38 exact square-root brackets and product caps;
- the complete positive multiplicity interval `1,...,38`;
- the fact that square moment 59 does not certify the result;
- the parity and positivity route to `tr(B^2)>=60`;
- Smith/rank bookkeeping and malformed Smith counts;
- the exact Seidel and `R` adjacency-algebra identities;
- both the old cap-45 and new cap-12 endpoint enumerations;
- restoration of the spurious `h=3` case if the even-Gram residue is removed;
- the rank-44 `h=1` signature obstruction and a rank-40 hostile control; and
- separation of exact rational decisions from displayed decimals.

The replay is:

```text
Ran 15 tests
OK
```

## 7. Boundary

This lane did **not** determine `rank_F3(M)`, `rank_F7(M)`, or the value of
`h` for a hypothetical target away from the rejected endpoint.  It produced
no graph, no target nonexistence proof, and no literature-novelty result.

The exact candidate conclusion is only

```text
conditional on target existence:
  n3>=708,
  induced_C6>=209994.
```

It remains `DERIVED` until an independent verifier freezes this submission,
reconstructs the moment extremum and lattice rescaling without discovery
internals, runs hostile cases, and explicitly confirms that no status beyond
this conditional bound is warranted.
