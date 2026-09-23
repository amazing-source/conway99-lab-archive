# Wave 28 theta/modular lane: exact restrictions and a rootless hostile control

```yaml
role: proof_b
date_utc: 2026-07-24T02:14:12Z
git_commit: d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b
claim_label: DERIVED
scope: >-
  Exact discriminant-group, level, scalar/vector theta-transformation,
  Sturm-bound, frame-visible shell, and strong-modularity restrictions for
  the eight n3=708 endpoint determinants; plus a candidate exact rootless
  h=729 bare-lattice hostile control. No S,Q,B endpoint package, projector,
  Schur certificate, graph, endpoint exclusion, or novelty claim is made.
inputs:
  agents/2026-07-24-wave28-orchestrator-brief.md: 6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e
  K12 catalogue page: 163e03dfa9a4ab07675daa6e97a371bcfdb38f6195c311c63c699872b3e486c9
  LAMBDA(F) catalogue page: bb1db4504d7010dc093b24a8bcb00b042ea3879a220d669e8190d02abb6468ac
method: >-
  Smith-normal-form consequences of SG=21I; exact level and character
  derivation; Poisson summation and the finite discriminant Weil law;
  determinant obstruction to modular self-duality; scalar Sturm bounds;
  exact Cartan and published-Gram arithmetic; complete reverse-LDL norm
  enumeration; finite-field discriminant-form comparison; a fresh
  17-case ADE census; and frame-shell antipodal accounting.
command: |-
  cd attempts/wave28-theta-modular
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
outputs:
  attempts/wave28-theta-modular/exact_check.py: 8185f7c483dc5dfa7ca31dd60058ee48ef6cdf8b29074c4f02f9dfcccdb095e1
  attempts/wave28-theta-modular/test_exact_check.py: 16dff2aa4c122e818c0898f604e12b2a67967591f528d048ccfe312f7bc4e1bc
  attempts/wave28-theta-modular/exact-results.json: 9d7b1ffcc0cef2441aa6dd381228abaa1018f721594e930cdd7227c0647470d6
  attempts/wave28-theta-modular/input-freeze.sha256: 42dda26e43b0512c9d929cae9877fbee9befb647450604d735d3ad5205cadcc8
  attempts/wave28-theta-modular/source-freeze.sha256: cad0b503878708bbaf49041b0325e54abe7a5180e05e3387c6e98e5f51bb555a
  attempts/wave28-theta-modular/failed-routes.md: 75e6bdbc7840f02c7a50497cf028144d76dd2e2a4f2b24d24fa83625477c49b9
limitations:
  - The h=729 object is a candidate bare S/G lattice control, not a full endpoint package.
  - General even rank-44 lattices are not classified.
  - Mixed-level partial-dual cusp leading terms are not determined.
  - Ordinary scalar and vector-valued elliptic theta series do not encode the 231-row pairwise Gram constraints or selected orientation.
  - No primitive embedding, X, M, Q, B, Schur-square origin, graph, formal-kernel proof, endpoint exclusion, target resolution, or novelty result is supplied.
```

## Result and status wall

The inherited lattice premises have sharp generic theta consequences, but
they do not contradict any endpoint determinant.  The exact implications are

```text
SG=21I with S,G even integral
  ==> A_S is 3,7-elementary,
  ==> level(S) is exactly 3, 7, or 21,
  ==> scalar and vector-valued theta transformation laws,
  ==> a finite scalar Sturm bound.
```

They do **not** imply modular or strongly modular self-duality.  In fact, the
endpoint determinants prove that such self-duality is impossible.

The strongest hostile control in this lane is

```text
S0 = K12 orthogonal_sum LAMBDA(F),
rank(S0)=44,
det(S0)=729,
min(S0)=4,
21 S0^-1 even integral with minimum at least 14.
```

Thus the bare endpoint lattice premises do not even force a root.  Moreover,
`S0` has the same discriminant quadratic form, hence the same Weil
representation, as the rooted control

```text
S1 = E6^6 orthogonal_sum E8,
root_count(S1)=672.
```

Both have a rootless `21`-scaled dual.  Therefore the full discriminant-form
transformation law and that scaled-dual gap still do not determine the root
coefficient.

The status boundary is strict:

```text
exact level/character/Poisson/Weil restrictions:       DERIVED
strongly 21-modular endpoint shortcut:                 REFUTED
root forced by bare lattice or theta premises:         REFUTED
rootless h=729 bare S/G hostile control:                CANDIDATE
compatible 231-row projector/Schur origin for S0:       NOT CONSTRUCTED
n3=708 or Conway-99:                                   UNKNOWN
novelty:                                               UNKNOWN
```

## 1. Frozen endpoint premises

The lane froze
`agents/2026-07-24-wave28-orchestrator-brief.md` at SHA-256
`6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e`.
The public base commit is
`d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b`.

No premise defect was found.  The theta lane uses only

```text
rank(S)=44,
S positive definite, even, and integral,
G=21 S^-1 positive definite, even, and integral,
min(G)>=4,
h=det(S) in {9,21,49,81,189,441,729,1029},
```

plus, where explicitly stated, the full frame facts

```text
M=XSX^T,
diag(M)=4,
offdiag(M) in {0,1,-1,-2},
M 1=0,
X has 231 rows and full column rank,
||sum_i (S^(1/2)x_i)^(tensor 3)||^2=60.
```

No root-lattice decomposition, automorphism, modular self-duality, or
partial-dual isometry is assumed.

## 2. Smith groups and exact levels

Choose Smith bases for the integral matrix `S`.  From

```text
S G=21 I
```

and integrality of `G`, every Smith invariant of `S` divides `21`.  Write

```text
h=3^a 7^b.
```

Because `21` is squarefree,

```text
A_S=S*/S = (Z/3Z)^a orthogonal_sum (Z/7Z)^b.       (1)
```

Its exponent is the product of the primes that occur.  Conversely, the
exponent `e` makes `e S^-1` integral.  Since

```text
21 S^-1=(21/e)(e S^-1)
```

is even and `21/e` is odd, `e S^-1` has even diagonal.  Hence the theta
level is exactly the discriminant-group exponent:

| `h` | `(a,b)` | exact level `N` | scalar character |
|---:|---:|---:|---|
| 9 | (2,0) | 3 | trivial |
| 21 | (1,1) | 21 | `chi_21` |
| 49 | (0,2) | 7 | trivial |
| 81 | (4,0) | 3 | trivial |
| 189 | (3,1) | 21 | `chi_21` |
| 441 | (2,2) | 21 | trivial |
| 729 | (6,0) | 3 | trivial |
| 1029 | (1,3) | 21 | `chi_21` |

The scalar character is

```text
chi_S(d)=(h/d),
```

the Kronecker symbol, because the weight is `44/2=22`.  The five square
determinants give the trivial character; the three values `21` times a
square give `chi_21`.

The complementary Smith factors of `G=21S^-1` are `21/d_i`.  Therefore

```text
A_G = (Z/3Z)^(44-a) orthogonal_sum (Z/7Z)^(44-b). (2)
```

Both exponents are positive in all eight rows, so `G` itself always has
exact level `21`.

## 3. Transformation laws that are actually justified

Use

```text
q=exp(2 pi i tau),
theta_gamma(tau)=sum_(x in S+gamma) q^((x,x)/2),
gamma in A_S.
```

Evenness gives the `T` law directly:

```text
theta_gamma(tau+1)
 = exp(pi i (gamma,gamma)) theta_gamma(tau).       (3)
```

Poisson summation on each coset gives the finite Fourier transform

```text
theta_gamma(-1/tau)
 = (-i tau)^22 / sqrt(h)
   * sum_(delta in A_S)
       exp(-2 pi i (gamma,delta)) theta_delta(tau). (4)
```

Equations (3)--(4), rather than any self-duality assertion, are the
vector-valued Weil transformation law used here.  Evaluating the same finite
Gauss sums on the zero component gives

```text
theta_S in M_22(Gamma_0(N),chi_S).                 (5)
```

The scalar Sturm bound

```text
floor((22/12) [SL_2(Z):Gamma_0(N)])
```

is exactly

| level | index | Sturm bound |
|---:|---:|---:|
| 3 | 4 | 7 |
| 7 | 8 | 14 |
| 21 | 32 | 58 |

Thus a future scalar-theta candidate is determined after coefficients
through norms `14`, `28`, or `116`, respectively.  This is a finite
restriction, not a classification or contradiction.

Ordinary Poisson summation also gives, without modular self-duality,

```text
theta_S(-1/(21 tau))
 = (21 tau/i)^22 / sqrt(h) * theta_G(tau).         (6)
```

For the natural level-`N` Fricke partner put

```text
K=N S^-1.
```

Then

```text
G=(21/N)K.                                        (7)
```

At level `21`, `K=G`, and `min(G)>=4` makes the `q` coefficient at that
cusp zero.  At levels `3` and `7`, however, the factors in (7) are seven
and three.  Even integrality of `K` already forces

```text
N=3: theta_G=1+O(q^7),
N=7: theta_G=1+O(q^3),
```

whether or not `K` has roots.  Treating those automatic rescaling gaps as
natural-Fricke rootlessness would be invalid.

The determinant list and (1) do not fix the leading terms at the `1/3` and
`1/7` partial-dual cusps in the mixed rows.  No transformation or vanishing
order at those cusps is used.

## 4. Strong modularity is not merely unproved; it is impossible

If a rank-44 level-`N` lattice were isometric to its scaled dual,

```text
S isometric to N S^-1,
```

then determinant comparison would force

```text
h=N^44/h,
h=N^22.                                           (8)
```

No endpoint determinant equals `3^22`, `7^22`, or `21^22`.  Therefore none
of the eight rows is modular at its exact level.  In particular, none is
strongly `21`-modular under the standard definition, which includes the
full scaled-dual isometry.

Consequently the following tempting imports are unavailable:

- a Fricke eigenvalue for `theta_S`;
- equality of `theta_S` and a partial-dual theta series;
- strongly-modular theta-ring formulas;
- strongly-modular shadow or extremal minimum bounds; and
- rootlessness at every cusp.

The correct relation is the two-lattice exchange (6), not a one-form
eigenvalue equation.

## 5. What the 231 rows add—and what ordinary theta forgets

Let `x_i` be the 231 rows of `X`.  The diagonal and off-diagonal alphabet
give

```text
x_i^T S x_i=4,
x_i^T S x_j in {0,1,-1,-2} for i!=j.
```

Two rows cannot agree or be negatives, since that would give inner product
`4` or `-4`.  They therefore select 231 distinct antipodal norm-four pairs,
so the scalar theta series must satisfy

```text
r_S(4)>=462.                                      (9)
```

With `y_i=S^(1/2)x_i`, the exact frame identities further give

```text
sum_i y_i=0,
sum_i y_i y_i^T=21 I_44,
||sum_i y_i^(tensor 3)||^2=60.                    (10)
```

The scalar theta series sees only the total shell count (9), not the
pairwise Gram alphabet or the marked subset in (10).  The ordinary
degree-three harmonic theta series is even less useful: the full lattice
sum pairs `v` and `-v`, so for every odd homogeneous polynomial `P`,

```text
P(v)+P(-v)=0.                                     (11)
```

Hence its zero-coset component is identically zero.  The nonzero cubic
quantity in (10) depends on a selected orientation of the 231 pairs and is
discarded by ordinary scalar and vector-valued elliptic theta series.

A theta attack capable of seeing (10) needs additional marked data—at
least Jacobi/Siegel pair coefficients or an explicit orientation/subset
enumerator—not only `theta_S`.

## 6. Exact scalar-theta hostile controls in every determinant row

A fresh recursive census independently recovered 17 rank-44 orthogonal ADE
forms using the five components allowed by `21R^-1` integrality.  At least
one bare lattice exists in every determinant row:

| `h` | one exact bare `S` | `r_S(2)` | `r_S(4)` |
|---:|---|---:|---:|
| 9 | `E6^2 + E8^4` | 1104 | 498204 |
| 21 | `A20 + E8^3` | 1140 | 517590 |
| 49 | `A6^2 + E8^4` | 1044 | 437064 |
| 81 | `A2 + E6^3 + E8^3` | 942 | 356778 |
| 189 | `A2 + A20 + E6 + E8^2` | 978 | 370332 |
| 441 | `A2 + A20 + A6 + E8^2` | 948 | 343092 |
| 729 | `E6^6 + E8` | 672 | 185220 |
| 1029 | `A2 + A6^3 + E8^3` | 852 | 280998 |

For an orthogonal product, the exact first coefficients are

```text
r(2)=sum_i r_i(2),
r(4)=sum_i r_i(4)+sum_(i<j) r_i(2)r_j(2).        (12)
```

The checker obtains the `A_n` coefficients by elementary coordinate
counting and the `E6,E8` coefficients by complete exact reverse-LDL
enumeration through norm four.  Each displayed `21S^-1` is even and has
minimum at least

```text
14,18,20,28,42
```

on `A2,A6,A20,E6,E8`, respectively.  All eight rows therefore satisfy the
bare scaled-dual minimum premise and exceed (9).

These are controls for scalar-theta reasoning only.  The Wave 26--27
projector/tensor results exclude their full endpoint origins.  They must not
be presented as compatible `S,Q,B` packages.

At `h=9` there is already vector-valued nonuniqueness.  The discriminant
forms of

```text
E8^5 + A2^2,
E8^4 + E6^2
```

are isometric: over `F_3`,

```text
P=[[1,1],[1,-1]],
P^T (2/3 I) P=4/3 I,
det(P)=1 mod 3.
```

Nevertheless their root coefficients are `1212` and `1104`.  The
discriminant module and Weil law do not select the zero-component theta
coefficient.

## 7. A rootless `h=729` control with the same Weil representation

The stronger control uses two published integral Gram matrices:

- the rank-12 Coxeter--Todd lattice `K12`;
- the rank-32 Koch--Venkov extremal even unimodular lattice `LAMBDA(F)`.

The matrices were transcribed from the
[Nebe--Sloane K12 catalogue](https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/K12.html)
and
[LAMBDA(F) catalogue](https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/KV32F.html).
The exact retrieved HTML hashes and embedded canonical matrix hashes are
recorded in `source-freeze.sha256` and `exact-results.json`; no live page
claim is trusted in place of the arithmetic checks.

The standard-library checker proves:

```text
det(K12)=729,
3 K12^-1 integral and even,
no nonzero K12 vector has norm <=2,
exactly 756 K12 vectors have norm 4;

det(LAMBDA(F))=1,
LAMBDA(F)^-1 integral and even,
no nonzero LAMBDA(F) vector has norm <=2.
```

Both displayed matrices have diagonal four.  Therefore

```text
S0=K12 orthogonal_sum LAMBDA(F)
```

is even, positive definite, rank 44, determinant 729, and has minimum four.
Furthermore,

```text
21 S0^-1
 =7(3K12^-1) orthogonal_sum 21 LAMBDA(F)^-1
```

is even integral.  Every nonzero vector of either even positive-definite
block has norm at least two, so the additional factors give the safe
minimum lower bound

```text
min(21 S0^-1)>=14.                                (13)
```

Thus `S0` is a rootless bare endpoint lattice control.

For an even unimodular rootless rank-32 lattice, the weight-16 level-one
theta space is spanned by `E4^4` and `E4 Delta`.  Cancelling the root
coefficient gives

```text
theta_L=E4^4-960 E4 Delta,
r_L(4)=146880.
```

Together with the exact K12 enumeration,

```text
r_S0(2)=0,
r_S0(4)=756+146880=147636,                        (14)
```

so even the frame-visible count (9) survives.

Now compare

```text
S1=E6^6 orthogonal_sum E8.
```

It has the same rank, determinant, exact level, and scalar character, while

```text
r_S1(2)=6*72+240=672.
```

The checker constructs quotient bases for both 3-primary discriminant
forms.  Each is a nondegenerate six-dimensional quadratic form over `F_3`
with determinant square class one.  Nondegenerate quadratic forms over an
odd finite field are classified by dimension and determinant square class,
so

```text
(A_S0,q_S0) isometric to (A_S1,q_S1).             (15)
```

The signatures are also the same.  Hence the two vector-valued theta
functions transform under the same Weil representation, yet their zero
components begin

```text
theta_S0=1+0 q+147636 q^2+...,
theta_S1=1+672 q+185220 q^2+....
```

Both `21`-scaled duals are rootless: (13) handles `S0`, while the `E6,E8`
dual minima give `min(21S1^-1)=28`.

This is the sharp blocker:

```text
same rank + determinant + discriminant form + Weil representation
+ rootless 21-scaled dual
does not determine the root coefficient.
```

It does not say that `S0` admits the 231 rows or any `Q,B` extension.

## 8. Finite next problem

Scalar theta theory alone has reached a genuine boundary.  A productive
continuation must add data that distinguishes the endpoint frame from the
controls above.  Three rigorous options remain:

1. compute the partial-dual discriminant forms and all coset leading terms,
   then impose positivity through the appropriate vector-valued Sturm
   range;
2. encode the required pairwise norm-four Gram coefficients in a
   degree-two Siegel or Jacobi theta series before attempting a coefficient
   contradiction; or
3. enumerate marked norm-four subsets satisfying (10), rather than treating
   the full lattice shell as the frame.

The first needs local quadratic-form data not fixed by `h`.  The second and
third need substantially more than ordinary theta coefficients.  Until one
of those bridges is supplied, `n3=708`, Conway-99 existence, and novelty
remain `UNKNOWN`.
