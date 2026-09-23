# Wave 32: an actual-incidence root reduces to a Fano-complement support

```yaml
role: proof_a
date_utc: 2026-07-24T08:20:00Z
git_commit: f0783b82d9b0260f5461cd68c647f62f646cdd81
claim_label: DERIVED
scope: >-
  Necessary rooted-vector reduction under the full actual vertex-triangle
  incidence and n3=708 projector/Schur endpoint package. Every norm-two root
  has the unique triangle-coordinate count pattern (+1)^21,0^189,(-1)^21.
  Its transported vertex vector is three times a signed characteristic
  vector whose 14-vertex support induces the bipartite complement of the
  Fano incidence graph. This is not a root exclusion.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/2026-07-22-n3-side-incidence-audit.md: 9b6ff3cc9ec8bec13ffd93a8abe0bf0f35398c99f676d00064d6bf5fe6db6787
  verification/2026-07-23-wave20-global-schur-audit.md: 6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3
  verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md: 45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268
  verification/wave28-glue-discriminant/audit.md: 5c1dc7978d571a9471837b45a36663c7c457b6434800776501e4967146956b86
  verification/wave31-sign-commutant/audit.md: f6145a3c4f4e787b23440a6ea071d606477821abab0ab8e7e5fe52042d6528a0
method: >-
  Transport the integral root image through the actual vertex-triangle
  incidence map; use primitivity to place it in M Z^231; reduce the
  transported minus-four eigenvector modulo three; force a signed
  seven-plus-seven support by exact norm and local eigenvector sums; use
  lambda=1 and mu=2 to identify the support design; then retain exact
  harmonic-cubic, A4, reflection, and outside-census constraints.
command: |-
  python -B -m unittest discover -s attempts/wave32-rooted-vector -p test_*.py -v
  python -B attempts/wave32-rooted-vector/exact_check.py --output attempts/wave32-rooted-vector/exact-results.json
outputs:
  attempts/wave32-rooted-vector/exact_check.py: c753cbda03f8db54f9ad618040c87084cdafa3ce151a5810f72428815a511642
  attempts/wave32-rooted-vector/test_exact_check.py: 7f0528ab5485d78c33f24d05d9cd773ed5a5951c44052e4a3489075d33d7c7cc
  attempts/wave32-rooted-vector/exact-results.json: 9fa31703b5c4721476b1b88f217d7455615c0d92c0d6db7f150abadfc069c2a0
  attempts/wave32-rooted-vector/input-freeze.sha256: 778473a5e3c872bf2c8d539b165d58d2d1329dd1224b515f6012fd628499b289
  attempts/wave32-rooted-vector/failed-routes.md: 444b36cb1bd3d1f604687b2a7d3d3c855fa1590689d0cc1ff18f9da288f17c19
  attempts/wave32-rooted-vector/correction-ledger.md: dd95a3d5af1156bfbdac89f2eac0decd15426b2a2261ff334a115f72ab69a2ce
limitations:
  - The independent verifier later passed the scoped reduction using a
    clean-room implementation; this discovery report is not that certificate.
  - The verifier caught a nonblocking v1 residual-degree metadata error,
    preserved and repaired in the discovery correction ledger.
  - The 32-to-1 reduction uses actual target incidence, not only the abstract matrix package.
  - The surviving Fano-complement support is a necessary local configuration, not a graph.
  - The hostile partial control leaves every outside-only completion constraint open.
  - Rooted endpoint existence, n3=708, Conway-99, and novelty remain UNKNOWN.
```

## Result and status wall

Let `r` be a norm-two vector of the even positive-definite endpoint form
`S`, and let

```text
y=XSr in Z^231.
```

Wave 28 verified, without an automorphism or splitting assumption, that

```text
y_i in {0,+/-1,+/-2},
sum_i y_i=0,
||y||^2=42,
My=21y,
Gamma y=0.
```

The new actual-incidence reduction is

```text
y has exactly 21 entries +1, 21 entries -1, and 189 entries 0.       (1)
```

More precisely, if `N` is vertex-triangle incidence and

```text
z=Ny,
```

then

```text
z=3k,
k in {0,+1,-1}^99,
|k^-1(+1)|=|k^-1(-1)|=7.                         (2)
```

The support of `k` induces a 4-regular bipartite graph between the positive
and negative seven-sets. Any two vertices in the same sign class have
exactly two common neighbors in the opposite class. Thus, up to relabeling,
the cross-incidence matrix is the complement of the Fano-plane incidence
matrix, a symmetric `2-(7,4,2)` design.

This is a reduction, not a contradiction:

```text
Wave 28 root count patterns:                         32
after matrix-only extreme-fiber positivity:          16
after actual vertex-triangle incidence:               1
rooted endpoint exclusion:                   NOT OBTAINED
n3=708:                                          UNKNOWN
Conway-99 existence/nonexistence:                  UNKNOWN
novelty:                                         UNKNOWN
```

The standard-library checker also builds a 99-vertex partial local control
that realizes every displayed support degree and every `lambda/mu` count for
pairs of support vertices. Its outside-only graph is unfilled. This prevents
the surviving pattern from being mistaken for a contradiction or a graph.

The first frozen discovery JSON misstated the remaining outside degrees as
`8,12,14`.  The verifier reconstructed current degrees
`4^42,2^28,0^15`, so the corrected residual degrees are
`10^42,12^28,14^15`.  The original hashes and repair are retained in
`attempts/wave32-rooted-vector/correction-ledger.md`; the scoped theorem is
unchanged.

## 1. Frozen endpoint identities

Use the actual target-graph package

```text
N N^T=7I+A,
N^T N=3I+Gamma,
M=21E,
E^2=E,
im(E)=ker(Gamma),
P_-4=(27I-9A+J)/63,
NE=P_-4 N.
```

Here `E` has rank 44 and `P_-4` projects onto the adjacency minus-four
eigenspace. Choose an integral basis matrix `X` for the primitive projector
lattice

```text
L=im(E) intersect Z^231.
```

Then

```text
G=X^T X,
S=21G^-1,
M=XSX^T,
M Z^231=21L*.
```

The Schur endpoint data additionally give

```text
W=M o M,
Q=X^T W X,
A4=MWM,
T=sum_i (S^(1/2)x_i)^(tensor 3),
tr(T)=0,
||T||^2=60.
```

The last trace is tensor contraction over any two legs. It vanishes because
all frame rows have norm four and their vector sum is zero.

## 2. The root image and the matrix-only extreme-fiber cap

For a root `(r,r)_S=2`,

```text
y_i=(x_i,r)_S.
```

Integrality is immediate from integral `X,S,r`. The frame identity gives

```text
||y||^2
 =r^T S X^T X S r
 =21(r,r)_S
 =42.                                                   (3)
```

Also `M1=0`, full column rank, and `S` invertible give `X^T1=0`, hence
`sum y_i=0`. Finally, each `x_i` has norm four, so Cauchy gives

```text
|y_i|<=sqrt(8)<3,
y_i in {0,+/-1,+/-2}.                                 (4)
```

There is a useful matrix-only strengthening. If `y_i=2 epsilon_i`, put

```text
u_i=epsilon_i x_i-r.
```

Then `u_i` is a root orthogonal to `r`, and for distinct extreme indices

```text
(u_i,u_j)
 =epsilon_i epsilon_j M_ij-2.                         (5)
```

The off-diagonal alphabet of `M` is `{0,1,-1,-2}`. For equal signs,
root Cauchy reduces (5) to `{-2,-1}`. Exact positive semidefiniteness then
gives:

```text
at most three +2 coordinates,
at most three -2 coordinates.                         (6)
```

If one sign has three, its three `u`-roots have Gram

```text
[[ 2,-1,-1],
 [-1, 2,-1],
 [-1,-1, 2]]
```

and sum to zero. Their three original frame products are one. Every
opposite-sign extreme transformed root has nonpositive product with each
member of this triple; the products sum to zero, so all three vanish.
Equation (5) then makes all three cross-frame products `-2`.

Wave 28 parametrized root patterns by

```text
a=#(+2), e=#(-2),
b=#(+1)=21-3a-e,
d=#(-1)=21-a-3e,
zero=189+3(a+e).
```

Its cubic-energy test left 32 patterns. Equation (6) leaves exactly 16.
This part uses the endpoint Gram alphabet but not actual vertex incidence.

## 3. The integral-image bridge

The actual-incidence step begins with a lattice fact that must not be
skipped. Since the columns of `X` form a basis of the primitive sublattice
`L`, the homomorphism

```text
X^T: Z^231 -> Z^44
```

is onto. Choose `c in Z^231` with

```text
X^T c=r.
```

Then

```text
y=XSr=XSX^T c=Mc.                                    (7)
```

Thus `y` is not merely an integral vector in `im(E)`; it lies in the exact
integral image `M Z^231=21L*`. This distinction powers the congruence below.

## 4. Actual incidence makes `Ny` constant modulo three

The spectral transport has an entrywise integral form:

```text
NM
 =21 P_-4 N
 =(9I-3A+J/3)N
 =(9I-3A)N+J_(99 x 231),                            (8)
```

because every triangle column of `N` has sum three. Hence every column of
`NM` is the all-ones vector modulo three. From (7),

```text
z=Ny=NMc
```

has all 99 coordinates congruent modulo three.

The usual incidence transport separately gives

```text
Az=-4z,
sum_v z_v=0,
||z||^2=3||y||^2=126,
N^Tz=3y.                                            (9)
```

The scale in (9) is exact because `N^TN=3I+Gamma` and `Gamma y=0`.

## 5. Nonzero residues are impossible

Choose the common residue in `{-1,0,1}`. Suppose first it is
`epsilon=+/-1` and write

```text
z=3k+epsilon 1.
```

The sum and norm in (9) give

```text
sum_v k_v=-33 epsilon,
sum_v k_v^2=25.                                    (10)
```

But integer coordinates satisfy

```text
sum k_v^2 >= sum |k_v| >= |sum k_v|=33,
```

contradicting (10). Therefore the common residue is zero:

```text
z=3k,
Ak=-4k,
sum k_v=0,
sum k_v^2=14.                                      (11)
```

This is where both primitivity and the actual incidence transport enter.
The abstract `X,M,S,Q,B` package alone does not imply (11).

## 6. The minus-four eigenvector has seven signs of each kind

Fix a vertex `v` and write `a=k_v`. From (11),

```text
sum_(u adjacent v) k_u=-4a.
```

The sum over the nonneighbors of `v`, excluding `v`, is therefore

```text
0-a-(-4a)=3a.
```

The neighbor and nonneighbor sets partition the other 98 vertices. Since
integer squares dominate absolute values,

```text
14-a^2
 =sum_(u!=v) k_u^2
 >=sum_(u!=v)|k_u|
 >=|-4a|+|3a|
 =7|a|.                                           (12)
```

The inequality `14-a^2>=7|a|` permits only

```text
a in {0,+1,-1}.
```

Equation (11) now forces exactly fourteen nonzero coordinates, with seven
of each sign. Denote the sign classes by `P` and `R`, each of size seven.

The checker also exhausts the twelve raw integer distributions of length 99,
sum zero, and squared norm 14. Only the balanced `1^7,0^85,(-1)^7`
distribution passes the minus-four neighbor-sum bound. Mutating the
eigenvalue magnitude from four to three leaves three distributions, so the
spectral value is active.

## 7. `lambda=1` and `mu=2` force the Fano-complement support

For `p in P`, let `d_P(p)` and `d_R(p)` be its support degrees into the two
sign classes. The eigenvector equation says

```text
d_P(p)-d_R(p)=-4,
d_R(p)=4+d_P(p).                                  (13)
```

The analogous equation holds with signs reversed on `R`.

Let `t_P,t_R` be the same-sign edge counts and `c` the cross-edge count.
Summing (13) over each side gives

```text
c=28+2t_P=28+2t_R.
```

Hence

```text
t_P=t_R=t.                                        (14)
```

Count unordered pairs of `P` vertices through their common neighbors in
`R`. If the internal degree of `r in R` is `d_r`, its cross degree is
`4+d_r`, so the count is

```text
sum_(r in R) binom(4+d_r,2)
 =42+7t+(1/2)sum_r d_r^2
 >=42+7t.                                         (15)
```

There are `t` adjacent pairs in `P`, each with at most `lambda=1` common
neighbor, and `21-t` nonadjacent pairs, each with at most `mu=2`. Thus the
same count is at most

```text
t+2(21-t)=42-t.                                   (16)
```

Equations (15)--(16) force `t=0`.

Consequently the support is bipartite and 4-regular. The left side of (15)
is now exactly 42. All 21 same-side pairs are nonadjacent and have at most
two common neighbors, so equality forces every pair to have exactly two.
The same holds on the other side. Therefore the 7-by-7 cross-incidence
matrix `C` satisfies

```text
C 1=4 1,
C^T 1=4 1,
CC^T=2I+2J.                                       (17)
```

Its complement has row and column sums three and pairwise row intersection
one, hence is the Fano-plane incidence matrix. The support graph is the
bipartite complement of the Heawood graph. No catalog or automorphism is
used; (17) is forced directly.

The hostile mutation `mu=3` makes `t=1,2` survive the counting screen.
Thus the target value `mu=2` is active.

## 8. Outside census and the unique triangle pattern

For a vertex `w` outside the support, the zero coordinate in (11) gives

```text
number of P-neighbors of w
 =number of R-neighbors of w.                      (18)
```

Either number is at most one. If `w` had two neighbors in `P`, those two
same-sign support vertices would already have their two common `R`
neighbors from (17), and `w` would be a third, contradicting `mu=2`.

Each support vertex has four support neighbors and therefore ten outside
neighbors. There are 140 support-outside incidences. Equation (18) implies

```text
70 outside vertices have one neighbor in each sign class,
15 outside vertices have no support neighbor.       (19)
```

Among the 70:

- Each of the 28 support cross-edges has its unique outside common neighbor
  by `lambda=1`.
- Each of the 21 support cross-nonedges has exactly two outside common
  neighbors by `mu=2`, accounting for the remaining 42.

Now use `N^Tz=3y` and `z=3k`:

```text
y_T=sum_(v in T) k_v.                              (20)
```

A graph triangle cannot contain two same-sign support vertices, because
there are no same-sign support edges. If it contains two support vertices,
they have opposite signs and contribute zero. At a support vertex, four of
its seven triangles contain its four cross-support edges; the other three
contain no second support vertex. Hence (20) yields

```text
21 triangles with y_T=+1,
21 triangles with y_T=-1,
189 triangles with y_T=0.                          (21)
```

This proves the 32-to-1 actual-incidence reduction (1).

## 9. Exact Schur, contraction, and `A4` constraints

For (21),

```text
sum_i y_i^3=0.
```

Put `a=S^(1/2)r`, so `||a||^2=2`, and let

```text
p=y o y,
g=T(a,a,.)=S^(1/2)X^T p,
H=T(a,.,.).
```

Write

```text
g2=||g||^2=p^T M p,
H2=||H||^2=y^T W y=(Sr)^T Q(Sr).                  (22)
```

The tensor `T` is symmetric, trace-free, and has squared norm 60. Set
`e=a/sqrt(2)` and decompose orthogonally into the `e` direction and its
43-dimensional complement. Since `T(e,e,e)=0`, write

```text
w=T(e,e,.) in e_perp,
A=T(e,.,.) restricted to e_perp.
```

Trace-freeness gives `tr(A)=0`; it also forces the trace vector of the
purely complementary cubic block to be `-w`. For symmetric cubics in
dimension 43, the minimum squared norm with prescribed trace vector `w` is

```text
3||w||^2/(43+2)=||w||^2/15.
```

Counting ordered tensor positions gives

```text
60 >= (46/15)||w||^2+3||A||^2.
```

Since

```text
g2=4||w||^2,
H2=4||w||^2+2||A||^2,
```

both contractions satisfy

```text
23g2<=1800,
23H2<=1800.                                       (23)
```

The first contraction has an independent exact congruence. Since

```text
D=(W-M)/2
```

is symmetric integral with even diagonal six, `y^TDy` is even. Therefore

```text
H2
 =y^TMy+2y^TDy
 =882 mod 4
 =2 mod 4.                                        (24)
```

It follows from positivity and (23)--(24) that

```text
H2 in {2,6,10,...,78}.                             (25)
```

Finally,

```text
y^T A4 y
 =y^T MWM y
 =441 H2.                                         (26)
```

Equation (26) is the exact `A4` consequence. The list (25) is nonempty, so
it is not a contradiction.

There is also an incidence interpretation of `g2`. The vector `Np` has:

```text
value 3 on the 14 support vertices,
value 2 on the 42 outside support-nonedge completions,
value 0 on the other 43 vertices.
```

If `f` is the number of graph edges among those 42 value-two vertices, the
projector formula and (17)--(19) give

```text
g2=7 (Np)^T P_-4 (Np)=1134-8f.                    (27)
```

Combining (23) and (27),

```text
g2 in {6,14,22,30,38,46,54,62,70,78},
f in {141,140,139,138,137,136,135,134,133,132}.   (28)
```

These ten exact possibilities are a finite continuation boundary.

## 10. Root reflection and what it does not imply

The lattice root reflection is

```text
rho_r(v)=v-(v,r)_S r.
```

On the 231 frame rows,

```text
x_i -> x_i-y_i r.
```

The induced orthogonal reflection in coordinate space is

```text
H_r=I-yy^T/21.
```

Using `y^TX=21r^T`,

```text
H_r X=X-yr^T,
H_r E=E H_r,
H_r M H_r=M.                                      (29)
```

On the adjacency minus-four space, incidence transports it to

```text
I-zz^T/63=I-kk^T/7.
```

These are exact factorization symmetries. They are not coordinate
permutations and do not make `rho_r` a graph automorphism. In particular,
the reflected norm-four rows are not silently added to the selected 231
rows.

## 11. Hostile partial control and next finite problem

The checker fixes a canonical Fano-plane incidence matrix and complements
it to the 4-regular support design. It then adds:

```text
28 outside vertices, one completing each support edge;
42 outside vertices, two completing each support cross-nonedge;
15 outside vertices with no support neighbor.
```

It also adds the 42 forced edges between nonedge-completion vertices that
form the three one-support triangles at each support vertex. Exact checks
show:

```text
all 14 support degrees are 14;
every support edge has exactly one common neighbor;
every support nonedge has exactly two common neighbors;
the signed support vector has eigenvalue -4 and norm 14.
```

This is a partial local control only. The outside vertices still need their
remaining degrees, and every outside-only adjacency, common-neighbor,
triangle, projector, and Schur condition is unfilled.

The rooted branch is therefore reduced to a concrete exact continuation:

```text
extend or exclude the canonical signed Fano-complement support inside the
full target graph, while imposing (25), (28), and the endpoint Schur data.
```

No failure to extend may be promoted without a complete checked search
certificate.

## 12. Exact replay and boundary

The standard-library-only suite passed:

```text
Ran 14 tests
OK
```

It checks all six frozen hashes, the exact 46-to-32-to-16-to-1 pattern
census, the complete size-at-most-four extreme-root Gram census, the
minus-four projector coefficients, the integral-image modulo-three bridge,
all twelve raw norm-14 integer distributions, the active minus-three
mutation, the Fano-complement design equations, the active `mu=3` mutation,
the outside census, both harmonic contraction bounds, the `A4` identity,
root-reflection scope, the partial 99-vertex local control, and deterministic
LF-only JSON.

The publication-safe status is:

```text
actual-incidence root pattern and support reduction: VERIFIED SCOPED
independent verification:                         PASS WITH V1 CORRECTION
rooted endpoint exclusion:                    NOT OBTAINED
n3=708:                                           UNKNOWN
Conway-99 existence/nonexistence:                  UNKNOWN
novelty:                                          UNKNOWN
```
