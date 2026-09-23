# Independent Wave 28 glue/discriminant audit

```yaml
role: verifier
date_utc: 2026-07-24T02:26:30Z
git_commit: d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b
claim_label: VERIFIED
scope: >-
  Clean-room adversarial verification of the elementary discriminant
  groups and exact levels, the twelve signature-compatible formal finite
  quadratic modules, the scaled-dual local determinant signs, the
  single-root index-two complement theorem, the 46- and 32-pattern
  projector censuses, and the primitive root-closure/glue theorem in the
  frozen Wave 28 endpoint package. The verdict is PASS_WITH_CORRECTION:
  one false statement about cyclic order-21 invariant factors is frozen
  below and does not affect the corrected primary-decomposition claims.
inputs:
  agents/2026-07-24-wave28-orchestrator-brief.md: 6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e
  agents/2026-07-24-wave28-glue-discriminant.md: 3c1354a04f33602c6e339875c8de4f77d1874bd6e8f83dbcb712b91717d6c1ff
  attempts/wave28-glue-discriminant/artifact-manifest.sha256: 5ac509e960c3b2e5e8b949aa88958f9bce6ae7b5b34a7baad140d20d3487bcbb
  attempts/wave28-glue-discriminant/exact-results.json: 13a3bb8f83c56ff899991362736089b772114cff840a2cb20d68845e231b3cf1
  attempts/wave28-glue-discriminant/exact_check.py: 9b58940cf9f3d732593e03bde69974b56145950f28e5012ccc0735082dd2cf51
  attempts/wave28-glue-discriminant/failed-routes.md: a976651e93ab1b4c9e87735fc5a51d22baa79da2259d99e08dfe4334227dd2d0
  attempts/wave28-glue-discriminant/input-freeze.sha256: 505cf42659e61d9340c6191b9a484c7eb064b02a3ecb1be1f8597a245095b7d2
  attempts/wave28-glue-discriminant/run-report.yaml: bb12cb91b9db78231a447c2e3f6adee7d3b4fe3e6e21f96beaa7c3057f0a2a67
  attempts/wave28-glue-discriminant/test_exact_check.py: d2617492eaa41905b72e850e1027db10e32aa04bc92d78e1751271151711676a
method: >-
  Reconstructed every finite computation with a standard-library-only
  implementation written without importing or executing discovery code.
  Enumerated Gauss phases from local signs, derived the scaled-dual ratio
  from local Jordan blocks, used A2 as a hostile non-splitting root
  control, enumerated the coordinate patterns again by a test-side
  four-variable brute force, and proved the glue theorem from primitive
  overlattice correspondence while testing the necessity of its
  hypotheses on small exact countercontrols.
command: |-
  cd verification/wave28-glue-discriminant
  python -B -m unittest -v test_independent_check.py
  python -B independent_check.py --output independent-results.json
outputs:
  verification/wave28-glue-discriminant/independent_check.py: 787884dc0278c1280f236e71783cc883c314e898bcf7ac3c2a3a4aacb361aa4c
  verification/wave28-glue-discriminant/test_independent_check.py: 801bc632810035ac95724866fcaf63fe476a002b617ccc4bb5844b2f7300c4cc
  verification/wave28-glue-discriminant/independent-results.json: 0d15724c772300072c565030e88080c05333af8f75241b633d5801e5c4ac83fe
limitations:
  - The endpoint package is inherited at the frozen public base; this audit
    does not repeat every upstream graph-to-lattice derivation.
  - Milgram's identity, the sign convention for the classical quadratic
    Gauss sum, ADE classification, and the standard even-overlattice
    correspondence are imported mathematical theorems, with their
    hypotheses checked here but without a formal-kernel reproof.
  - The twelve modules are formal local candidates, not realized lattices.
  - The 32 patterns are necessary coordinate-count patterns, not vectors,
    frames, Schur certificates, lattices, or graphs.
  - Root-preserving glue and rootless complements remain unclassified.
  - No determinant row is excluded. n3=708, Conway-99, and novelty remain
    UNKNOWN.
```

## Verdict

The scoped mathematical claims pass after one mandatory prose correction:

| Claim | Verdict |
|---|---|
| elementary 3- and 7-primary decomposition | `PASS` |
| exact levels on all eight determinant rows | `PASS` |
| exactly twelve Milgram-compatible formal modules | `PASS` |
| stale count eleven | `REFUTED` |
| `delta_p(21S^-1)=delta_p(S)` for `p=3,7` | `PASS` |
| primitive root, index-two complement, determinant `2h` | `PASS` |
| complement 2-primary form `<-1/2>` and unchanged odd form | `PASS` |
| projector identities and complete `46 -> 32` censuses | `PASS` |
| hostile scalar-moment survivor | `PASS` |
| primitive root-closure/glue theorem, with all stated hypotheses | `PASS` |
| discovery sentence excluding cyclic order-21 factors | `FAIL`, correction required |
| realization or exclusion of any determinant row | `UNKNOWN` |
| unrestricted endpoint, `n3=708`, Conway-99, novelty | `UNKNOWN` |

The verifier therefore assigns `PASS_WITH_CORRECTION`, not an unqualified
pass and not a rejection of the lane. The defect is representational prose;
the canonical primary decomposition and every downstream calculation remain
correct.

## Frozen defect: cyclic order 21 is allowed

Section 2 of the discovery report says:

```text
There can be no cyclic factor of order 9, 49, or 21:
every invariant factor is killed by 21.
```

The order-21 clause is false. A cyclic group `Z/21` is killed by 21, and

```text
Z/21 is isomorphic to Z/3 direct_sum Z/7.
```

Thus the correct conclusion from `21A_L=0` is:

```text
each p-primary factor is elementary;
no p-primary factor has order 9 or 49;
in invariant-factor notation every factor divides 21,
and factors of order 21 are allowed.
```

The exact recommended replacement is:

> No `p`-primary cyclic factor has order `p^2` or higher. Invariant
> factors divide 21 and may have order 21.

The four mixed rows provide active controls:

| `h` | primary notation | invariant-factor notation |
|---:|---|---|
| 21 | `Z/3 + Z/7` | `Z/21` |
| 189 | `(Z/3)^3 + Z/7` | `Z/3 + Z/3 + Z/21` |
| 441 | `(Z/3)^2 + (Z/7)^2` | `(Z/21)^2` |
| 1029 | `Z/3 + (Z/7)^3` | `Z/7 + Z/7 + Z/21` |

A static dependency search of the discovery checker, tests, JSON, and report
found no computation that assumes the absence of `Z/21`. They store the
canonical primary decomposition and operate independently at 3 and 7.
Accordingly, the error does not change the level table, local quadratic
forms, Milgram count, scaled-dual signs, or glue theorem.

## 1. Elementary groups and exact levels

Let `L=(Z^44,S)`. The frozen relation `G=21S^-1` integral says

```text
21L* is contained in L,
```

so every element of `A_L=L*/L` is killed by 21. Since
`|A_L|=h=3^u 7^v`, primary decomposition gives

```text
(A_L)_3 = (Z/3)^u,
(A_L)_7 = (Z/7)^v.
```

For an odd prime, a nonzero nondegenerate elementary quadratic component
diagonalizes as a sum of `<2a/p>` with `a` a unit. It has exact level `p`;
otherwise its nonzero denominator could not be killed. Orthogonality of
distinct primary components makes the total level their least common
multiple. The independent table is:

| `h` | `(u,v)` | exact level | primary dimensions of `A_G` |
|---:|---:|---:|---:|
| 9 | (2,0) | 3 | (42,44) |
| 21 | (1,1) | 21 | (43,43) |
| 49 | (0,2) | 7 | (44,42) |
| 81 | (4,0) | 3 | (40,44) |
| 189 | (3,1) | 21 | (41,43) |
| 441 | (2,2) | 21 | (42,42) |
| 729 | (6,0) | 3 | (38,44) |
| 1029 | (1,3) | 21 | (43,41) |

The last column follows independently from

```text
det(G)=21^44/h
```

and `21G^-1=S` integral: `A_G` is elementary with dimensions
`(44-u,44-v)`. None of this supplies a strong-modularity or
Atkin--Lehner isometry.

## 2. Gauss phase and the exact count twelve

For `p=3,7`, write

```text
q_p = direct_sum_i <2a_i/p>,
delta_p = Legendre(product_i a_i,p).
```

Over the odd field `F_p`, dimension and determinant square class classify
nondegenerate quadratic forms. Each nonzero primary dimension therefore
has two possible local classes, while an empty component has sign `+1`.

With the displayed convention,

```text
p^(-1/2) sum_x exp(pi i * 2a x^2/p)
  = i Legendre(a,p)
```

because both 3 and 7 are `3 mod 4`. The checker independently records the
quadratic-residue exponent polynomials. Modulo
`Phi_p=1+x+...+x^(p-1)`, it verifies exactly that the nonsquare sum is the
negative of the square sum and that the square sum is purely imaginary.
The standard Gauss-sum theorem fixes its orientation as `+i`.

Milgram's identity for positive signature 44 requires phase

```text
exp(2 pi i * 44/8) = -1 = i^2.
```

Thus a sign pair survives exactly when

```text
u+v + 2[delta_3=-1] + 2[delta_7=-1] = 2 (mod 4).
```

The independently hard-matched census is:

| `h` | `(u,v)` | allowed `(delta_3,delta_7)` | count |
|---:|---:|---|---:|
| 9 | (2,0) | `(+,+)` | 1 |
| 21 | (1,1) | `(+,+),(-,-)` | 2 |
| 49 | (0,2) | `(+,+)` | 1 |
| 81 | (4,0) | `(-,+)` | 1 |
| 189 | (3,1) | `(+,-),(-,+)` | 2 |
| 441 | (2,2) | `(+,-),(-,+)` | 2 |
| 729 | (6,0) | `(+,+)` | 1 |
| 1029 | (1,3) | `(+,-),(-,+)` | 2 |

Therefore

```text
1+2+1+1+2+2+1+2 = 12,
```

and eleven is actively rejected. The checker constructs canonical
coefficient lists with nonsquares `2 mod 3` and `3 mod 7`, then recomputes
every determinant sign. This is a classification of formal finite
quadratic modules subject to the stated constraints, not a lattice
realization theorem.

## 3. Scaled-dual determinant signs

Fix `p` in `{3,7}`, let `m=v_p(h)`, `ell=21/p`, and `n=44`. Since the
`p`-primary discriminant group is elementary, local Jordan form is

```text
S congruent to U direct_sum pV,
rank(U)=n-m, rank(V)=m,
```

with `U,V` unimodular over `Z_p`. Then

```text
G=p ell S^-1
  congruent to p ell U^-1 direct_sum ell V^-1.
```

Diagonalizing the unit blocks and translating each discriminant
coefficient to the convention `<2a/p>` gives

```text
delta_p(S) = (2/p)^m (det V/p),
delta_p(G) = (2/p)^(n-m) (ell/p)^(n-m) (det U/p).
```

Legendre symbols are their own inverses, so

```text
delta_p(G)/delta_p(S)
 = (2/p)^n (ell/p)^(n-m) (det U det V/p).
```

The change-of-basis determinant is a square and hence

```text
(det U det V/p)=(h/p^m / p).
```

At `p=3`, `(7/3)=+1`, `(2/3)^44=1`, and the unit part is a
power of 7, so the ratio is one. At `p=7`, `(2/7)=+1`,
`(3/7)=-1`, and the remaining exponent is

```text
44-v+u,
```

which is even on every row because `u+v` is even. The independent checker
evaluates all sixteen `(h,p)` cases and obtains ratio `+1` in each.

## 4. A single root and its complement

Let `(r,r)=2`.

1. If `r=ka` with `k>=2`, evenness would make the positive value
   `(a,a)=2/k^2` an even integer, impossible. Thus `r` is primitive.
2. Its divisibility divides two. Divisibility two would put the nonzero
   order-two class `r/2` in `A_L`, impossible because `h` is odd.
   Therefore `div(r)=1`.
3. The homomorphism `x -> (r,x) mod 2` is onto. Its kernel is
   `Zr direct_sum K_r`, where `K_r=r_perp intersect L`, because for an
   even pairing one subtracts `((r,x)/2)r`.

Consequently

```text
[L:Zr direct_sum K_r]=2,
2 det(K_r)=4h,
det(K_r)=2h.
```

At 2, the glue must cancel the `A1` class of norm `+1/2`, so the
order-two component of `A_Kr` is `<-1/2>`. The index has no odd factor;
therefore the odd discriminant form is unchanged from `A_L`.

The independent hostile control is `A2` with Gram matrix

```text
[ 2 -1 ]
[-1  2 ].
```

For `r=(1,0)`, the complement is generated by `k=(1,2)`. Exact
calculation gives

```text
det(A2)=3, div(r)=1, (r,k)=0, (k,k)=6,
[A2:Zr direct_sum Zk]=2,
q_K(k/2)=3/2=-1/2 mod 2.
```

This actively refutes the tempting but invalid inference
“primitive root implies orthogonal integral summand.”

## 5. Projector identities and complete censuses

For a root define `t=XSr`. The inherited exact identities give

```text
t.t = r^T S X^T X S r = 21(r,r)_S = 42.
```

Since `M1=XSX^T1=0`, while `XS` has full column rank,
`X^T1=0`, and hence `sum_i t_i=0`. Each coordinate is integral, and
Cauchy--Schwarz with `(x_i,x_i)_S=4` yields

```text
|t_i| <= sqrt(8) < 3,
t_i in {0,+/-1,+/-2}.
```

For two roots the same computation gives

```text
t(r).t(s)=21(r,s)_S.
```

Let `(a,b,z,d,e)` count `(+2,+1,0,-1,-2)`. Solving only the coordinate
count, zero-sum, and squared-norm equations gives

```text
b=21-3a-e,
d=21-a-3e,
z=189+3(a+e).
```

Nonnegativity leaves the following complete 46 `(a,e)` pairs; the other
three counts are recovered by the displayed equations:

```text
(0,0) (0,1) (0,2) (0,3) (0,4) (0,5) (0,6) (0,7)
(1,0) (1,1) (1,2) (1,3) (1,4) (1,5) (1,6)
(2,0) (2,1) (2,2) (2,3) (2,4) (2,5) (2,6)
(3,0) (3,1) (3,2) (3,3) (3,4) (3,5) (3,6)
(4,0) (4,1) (4,2) (4,3) (4,4) (4,5)
(5,0) (5,1) (5,2) (5,3) (5,4) (5,5)
(6,0) (6,1) (6,2) (6,3)
(7,0)
```

This production enumeration uses the solved formulas. A separate
test-side enumeration loops independently over all four nonzero counts,
sets only `z=231-a-b-d-e`, and tests the two moments directly. It returns
the identical set of 46.

Now let `y_i=S^(1/2)x_i` and
`T=sum_i y_i tensor y_i tensor y_i`. Then

```text
||T||^2=sum_(i,j) M_ij^3
       =tr(S X^T(M o M)X)
       =tr(SQ)=60.
```

Projection onto the unit root line has squared energy

```text
(sum_i t_i^3)^2/8
 = (6(a-e))^2/8
 = 9(a-e)^2/2.
```

It cannot exceed 60, so `|a-e|<=3`. Exactly these 32 pairs remain:

```text
(0,0) (0,1) (0,2) (0,3)
(1,0) (1,1) (1,2) (1,3) (1,4)
(2,0) (2,1) (2,2) (2,3) (2,4) (2,5)
(3,0) (3,1) (3,2) (3,3) (3,4) (3,5) (3,6)
(4,1) (4,2) (4,3) (4,4) (4,5)
(5,2) (5,3) (5,4) (5,5)
(6,3)
```

The exact hostile survivor is

```text
(a,b,z,d,e)=(0,21,189,21,0),
```

with cubic energy zero. The active mutation

```text
(4,9,201,17,0)
```

passes the first two moments but has cubic energy 72 and is rejected.
The bound is therefore active but is not a root exclusion.

## 6. Primitive root closure and glue

This theorem needs every stated hypothesis.

Let `R` be generated by **all** norm-two vectors of the positive-definite
even integral lattice `L`.

- Positive definiteness makes the root set finite. Integrality makes the
  reflection `x -> x-(x,r)r` preserve `L`, and Cauchy--Schwarz makes the
  root system simply laced. The finite simply-laced classification gives
  an abstract orthogonal sum of ADE root lattices.
- `Rbar=(R tensor Q) intersect L` is primitive by saturation. Even
  overlattice correspondence identifies `H0=Rbar/R` with an isotropic
  subgroup of `A_R`.
- Every representative of an `H0` coset lies in the even lattice `L`.
  A nonzero coset of minimum two would contain another root of `L`,
  which belongs to `R` by definition, a contradiction. Hence every
  nonzero used coset has minimum at least four.
- `K=Rbar_perp intersect L` is primitive: if a nonzero integer multiple
  of a class is orthogonal to `Rbar`, then the class itself is. If `K`
  contained a root, that root would lie both in `R` and in `Rbar`'s
  orthogonal complement, contradicting positive definiteness. Thus `K`
  is rootless.

The finite-index inclusion

```text
Rbar direct_sum K is contained in L
```

corresponds to an isotropic subgroup

```text
H1=L/(Rbar direct_sum K)
```

of `A_Rbar direct_sum A_K`. Both projections are injective. For example,
if the `A_Rbar` projection of a glue class vanishes, subtract its
`Rbar` representative; the resulting vector lies in
`L intersect (K tensor Q)=K`, so the whole class vanishes. The other
projection is symmetric. Therefore `H1` is the graph of an anti-isometry
between its projected subgroups. Standard overlattice bookkeeping gives

```text
q_L is isometric to H1_perp/H1,
det(L)=det(R)det(K)/(|H0|^2 |H1|^2).
```

For `p` other than 3 or 7, `(A_L)_p=0`, hence
`(H1)_p=(H1)_p^perp`. Nondegeneracy gives

```text
|H1_p|^2=|A_Rbar,p| |A_K,p|.
```

Injectivity gives `|H1_p|` no larger than either factor. These three
relations force

```text
|H1_p|=|A_Rbar,p|=|A_K,p|.
```

Both projections are consequently surjective, and the isotropic graph
condition is precisely

```text
(A_K,q_K)_p isometric to (A_Rbar,-q_Rbar)_p.
```

The determinant valuations agree.

Three hostile controls show the hypotheses are active:

1. If `R` is not generated by all roots, choose only the first `A1` in
   `A1 direct_sum A1`; its complement is the second `A1` and is not
   rootless.
2. If primitivity is dropped, embed `<8>=Z(2e)` in `<2>=Ze`. The
   overlattice quotient has order two while the complement is zero, so
   the projection to the complement has a kernel.
3. Self-duality alone does not force equal discriminant-factor orders:
   `4^2=2*8`. It is the two projection injections that exclude this
   example and force full cancellation.

No step assumes that `R`, `Rbar`, or a single root is an orthogonal
integral summand of `L`.

## 7. Reproduction and status wall

The clean-room suite passed:

```text
Ran 16 tests
OK
```

It uses Python 3.13.14 standard-library integers and `Fraction`, with no
floating-point decisions. The output is deterministic, UTF-8, LF-only
JSON. The tests hard-match all eight levels and sign rows, explicitly
reject eleven, verify both local signs on every determinant row, exercise
the `A2` non-splitting control, compare the two pattern censuses to a
separately written brute-force enumeration, preserve the hostile survivor,
reject the cubic mutation, and attack every primitivity/cancellation
hypothesis.

The verifier did not import or execute the discovery checker. Discovery
JSON was not used as mathematical evidence; after finding the prose defect,
a static text search across the discovery artifacts was used only to
establish whether downstream files relied on the false order-21 sentence.

This audit verifies necessary restrictions only. It constructs no rank-44
lattice, primitive `Z^231` embedding, projector frame, Schur-square
certificate, graph, or Conway configuration, and it excludes no `h` row.
The unrestricted endpoint, `n3=708`, Conway-99 existence, and novelty all
remain `UNKNOWN`.
