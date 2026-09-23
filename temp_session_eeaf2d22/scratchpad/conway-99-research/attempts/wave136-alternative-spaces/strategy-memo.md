# Wave136 alternative-space strategy memo

Status: strategy assessment only. Every mathematical statement below is
conditional on a hypothetical adjacency matrix

```text
A=A^T, diag(A)=0, A*1=14*1,
A^2=12I-A+2J
```

for an `srg(99,14,1,2)`. No route below constructs or excludes such a
matrix. The ranking is research judgment, not a theorem, and no external
novelty claim is made.

## Executive decision

The cheapest new exact constraint is an **Arf/Gauss two-branch identity**
for the Wave131 binary image code. It should be inserted immediately into
the existing binary enumerator systems. The best new *space* after that is
the **self-dual additive `GF(4)` graph-state enumerator** canonically
attached to `A`.

This translation is unusually attractive here:

1. it adds exact constraints that are not consequences of the Wave134
   `Z4` symmetrized enumerator;
2. after a natural three-class symmetrization it has exactly 5,050 raw
   states, the same scale as Wave134;
3. its character transform is, after permuting variables, the same
   three-variable transform already implemented in Wave134/135; and
4. it couples the Wave131 binary image and dual codes inside one self-dual
   object while retaining new mixed graph data.

The recommended order is:

| rank | space | expected value | first certificate boundary |
|---:|---|---|---|
| 0 | binary Arf/Gauss branch | essentially free and already refutes the Wave131 formal point | exact two-branch rational solve |
| 1 | self-dual additive `GF(4)` graph-state code | high relative to cost | exact rational point or Farkas certificate on 5,050 states |
| 2 | two-root order-eight Terwilliger/flag SDP | best direct route to a general `n3` upper bound | rational PSD/SOS dual |
| 3 | marked genus-two code enumerators | strong but substantially larger | exact partial-Hadamard point or Farkas certificate |
| 4 | `Z8` / two-adic lift | genuinely new arithmetic, high state count | exact algebraic-number LP slice |
| 5 | nonabelian triangle-holonomy cover | potentially sharp, foundational bridge missing | verified overlap cocycle or local obstruction |
| 6 | ordinary Construction A / lattice shadows | presently blocked | first prove a valid integral self-dual lattice/code bridge |

## 0. Binary Arf/Gauss branch

This is the most important low-cost addition found during the strategy
audit.

Let

```text
H={x in F_2^99 : wt(x) is even}=1^perp.
```

Because the length 99 is odd, `1` is not in `H`; consequently the ordinary
dot product restricted to `H` is a nondegenerate alternating form of
dimension 98. Define

```text
q(x)=wt(x)/2 mod 2,  x in H.
```

For even `x,y`,

```text
wt(x+y)=wt(x)+wt(y)-2|supp(x) intersect supp(y)|,
```

so

```text
q(x+y)=q(x)+q(y)+x*y mod 2.                       (0.1)
```

Thus the polar form of `q` is the dot product.

Put `R=im_F2(A)` and `D=ker_F2(A)=R^perp`. Wave131 gives
`R subset H`, `dim(R)=54`, and `R intersect R^perp=0`. Therefore `q|R`
is a nondegenerate quadratic refinement of a 54-dimensional symplectic
space. Inside `H`, its orthogonal complement is

```text
E=D intersect H,  dim(E)=44,
H=R orthogonal_sum E.
```

The elementary Gauss-sum theorem for a nondegenerate quadratic form over
`F_2` now forces, for one sign `epsilon in {+1,-1}`,

```text
G_R=sum_(x in R)(-1)^q(x)
   =sum_(w even)(-1)^(w/2) A_w
   =epsilon*2^27,                                  (0.2)

G_E=sum_(x in E)(-1)^q(x)
   =sum_(w even)(-1)^(w/2) B_w
   =-epsilon*2^22.                                 (0.3)
```

The signs are opposite because

```text
G_H=G_R*G_E
   =sum_(w even)(-1)^(w/2) C(99,w)
   =Re((1+i)^99)
   =-2^49.                                         (0.4)
```

Ordinary binary MacWilliams gives only the ratio

```text
G_E=-G_R/32;                                       (0.5)
```

it does not force the magnitude in (0.2). Hence (0.2) is genuinely stronger
than the 200 ordinary transform rows.

The sealed Wave131 rational witness illustrates the distinction exactly.
It has

```text
G_R =
246964934998081883385269739380937552159104000
------------------------------------------------
452929323301482718880047428141,
```

which is neither `+2^27` nor `-2^27`, while its even-dual sum is exactly
`-G_R/32`. Thus that formal MacWilliams point is refuted by the Arf branch.
This does not refute a binary code or a graph.

The smallest next computation is two exact rational solves: append
`G_R=+2^27` in one branch and `G_R=-2^27` in the other to the strongest
Wave132 binary split system. Each branch must return either a complete
rational point or a replayable Farkas certificate. The constraint should
also be inserted as a pure-`Y` axis equation in the graph-state system
below.

## 1. Self-dual additive `GF(4)` graph-state code

### Exact map

Represent a Pauli symbol by a binary pair:

```text
I=(0,0), X=(1,0), Z=(0,1), Y=(1,1).
```

Define

```text
S_A = {(x,Ax) : x in F_2^99}.
```

The trace-Hermitian inner product on additive `GF(4)` codes is the binary
symplectic form

```text
<(x,z),(y,t)> = x*t + z*y.
```

Since `A=A^T`,

```text
<(x,Ax),(y,Ay)>
  = x*A*y + x*A^T*y
  = 0 mod 2.
```

The map `x -> (x,Ax)` is injective, so `|S_A|=2^99`. It is therefore a
self-dual additive `GF(4)` code of length 99. This is the standard graph-code
correspondence; see Danielsen--Parker's primary graph-code papers
([2006](https://arxiv.org/abs/math/0504522),
[2009](https://arxiv.org/abs/0801.3773)).

For one codeword put

```text
nY = |supp(x) intersect supp(Ax)|,
nR = |supp(x) symmetric_difference supp(Ax)|,
nI = 99-nY-nR.
```

Equivalently, `nR=nX+nZ`. Because `A` is alternating over `F_2`,

```text
nY = x^T A x = 0 mod 2.                         (1)
```

Define the symmetrized complete enumerator

```text
P_A(u,v,w)
 = sum_x u^nI(x) v^nY(x) w^nR(x).
```

Self-duality gives the exact MacWilliams identity

```text
P_A(u,v,w)
 = 2^-99 P_A(u+v+2w, u+v-2w, u-v).             (2)
```

After ordering the variables as `(u,w,v)`, the substitution matrix in (2)
is exactly

```text
(x,y,z) -> (x+2y+z, x-z, x-2y+z),
```

the Wave134 symmetrized `Z4` transform. Thus the sparse Krawtchouk machinery
can be reused, although the mathematical object and normalization are
different.

There are

```text
C(101,2)=5050
```

raw compositions. Equation (1) leaves exactly

```text
sum_(j=0)^49 (100-2j) = 2550
```

allowed even-`nY` states and forces 2,500 coefficient rows to zero.

### Exact coupling to the binary codes

Over `F_2`, `A^2=A`. Let

```text
C=im(A), D=ker(A).
```

If `x in C`, then `Ax=x`; hence the corresponding graph-code word is
pure `Y`. If `x in D`, then `Ax=0`; hence it is pure `X`. Therefore

```text
[u^(99-t) v^t] P_A = A_t(C),                    (3)
```

and the fully refined four-variable enumerator has

```text
[u^(99-t) X^t] CWE(S_A) = B_t(D).               (4)
```

The three-variable projection retains (3) exactly and retains (4) as a
lower bound inside the `v=0` shell. This puts both binary weight
distributions inside one self-dual transform instead of treating them as
separate marginals.

### Forced mixed coefficients through three vertices

For a vertex set `T`, the graph-code support is

```text
T union Odd(T),
Odd(T)={z : |N(z) intersect T| is odd}.
```

The Wave131 exact three-set census gives the following new lower
coefficients. Here `c` is the number of vertices adjacent to all three
members of `T`.

| input `T` | count | `nY` | `nR` |
|---|---:|---:|---:|
| one vertex | 99 | 0 | 15 |
| edge | 693 | 2 | 24 |
| nonedge | 4,158 | 0 | 26 |
| independent triple, `c=0` | 70,686 | 0 | 33 |
| independent triple, `c=1` | 27,720 | 0 | 37 |
| one-edge triple, `c=0` | 41,580 | 2 | 31 |
| one-edge triple, `c=1` | 8,316 | 2 | 35 |
| induced path | 8,316 | 2 | 33 |
| triangle | 231 | 0 | 39 |

The input map is injective, so there is no collision among these words.
In addition, the pure-`Y` and pure-`X` axes inherit all Wave131/132
binary lower bounds.

### What is new relative to Wave134

Wave134 concerns

```text
row_Z4(A), of order 2^109,
and its dual, of order 2^89.
```

It has two paired enumerators and only one-word composition data. In
contrast, (2) is one **self-dual** enumerator of fixed order `2^99`.
It has the 2,500 structural zero rows (1), contains both binary axes
(3)--(4), and contains the mixed `T/Odd(T)` table above. None of those
facts follows from feasibility of the Wave134 scalar `Z4` enumerator.

The standard Hamming specialization can also receive Rains's shadow
inequalities. If `H_t` is the graph-code Hamming distribution, the
shadow coefficients have the form

```text
S_j = 2^-99 sum_t (-1)^t K_j^(4)(t) H_t >= 0,   (5)
```

with the convention independently checked before use. Rains proved
nonnegativity of quantum shadow and higher polynomial invariants
([quantum shadows](https://arxiv.org/abs/quant-ph/9611001),
[polynomial invariants](https://arxiv.org/abs/quant-ph/9704042)).

### Smallest experiment and certificates

Build a 5,050-variable exact rational feasibility system:

1. self-duality (2);
2. normalization `P_A(1,1,1)=2^99` and zero-word coefficient one;
3. nonnegativity;
4. all odd-`nY` coefficients zero;
5. the pure-axis Wave131/132 bounds; and
6. the mixed lower table above.

Then add the 100 shadow inequalities (5) as a separately audited layer.
Reuse the Wave135 exact-face representation only after that package seals;
do not import an unfinished result.

A rational feasible vector is a null control, not a code. Exact
infeasibility requires a complete rational Farkas certificate whose row
combination can be replayed using integer arithmetic. Integral feasibility
is a later, stronger question.

The main bottleneck is likely not matrix size but a subtle undercount in
the forced mixed table or an incorrect shadow convention. The Wave134
experience makes independent regeneration mandatory.

## 2. Two-root order-eight Terwilliger / finite flag SDP

### Exact map

For a pointwise-labelled root `sigma` on two vertices (edge and nonedge
handled separately), take all admissible five-vertex flags consisting of
the root plus three free vertices. For a root embedding `theta`, let
`c_F(theta)` count extensions realizing flag `F`. Then

```text
M_sigma(F,F')
 = sum_theta c_F(theta)c_F'(theta)
```

is a sum of integer outer products and hence

```text
M_sigma >= 0.                                    (6)
```

Two such flags unite on at most eight vertices. Every entry of (6) is
therefore a linear combination of labelled induced-subgraph counts through
order eight.

This is the finite exact analogue of the Terwilliger/SDP refinement of a
Bose--Mesner linear program. Schrijver's primary paper shows how triple
data and a Terwilliger algebra produce SDP constraints stronger than the
ordinary Delsarte LP
([paper](https://homepages.cwi.nl/~lex/files/codes.pdf),
[DOI](https://doi.org/10.1109/TIT.2005.851748)). The use here is a direct
finite graph moment identity, not a claim that Schrijver studied
Conway-99.

### What is new relative to existing waves

Waves45, 47, and 49 exhaust all presently constructed PSD families that
close in order-seven variables:

```text
one/two-root four-vertex flags,
three-root five-vertex flags,
five-root one-free flags.
```

They are near a degenerate numerical boundary and do not emit a rational
dual. The two-root five-vertex family is the smallest flag product that
introduces order-eight compatibility. Wave134 has no overlap PSD
constraint at all.

For a **general** upper bound, retain `n3` as an objective variable instead
of imposing `n3=4158`, append the order-eight deletion/extension identities,
and maximize `n3`.

### Certificate form and bottleneck

An exact bound `n3<=U` should be published as an identity

```text
U-n3
 = sum_H alpha_H*(exact count identity H)
   + sum_sigma <Q_sigma,M_sigma>
   + sum_H beta_H*x_H,
```

where every `Q_sigma` is rational PSD, every `beta_H>=0`, and every term
is replayed exactly. A rational LDL decomposition or integer Gram
factorization of each `Q_sigma` is the certificate.

The bottleneck is the complete order-eight admissible-class stream and
exact rationalization of a highly singular SDP dual. A floating negative
margin is not evidence.

## 3. Marked genus-two code enumerators

### Exact map

For a code over a finite Frobenius ring, the genus-two complete enumerator
records ordered pairs:

```text
J_CC^(2)(X_ab)
 = sum_(c,d in C) product_i X_(c_i,d_i).
```

A Fourier transform in the second coordinate gives the `C x Cperp`
enumerator, and a second transform gives `Cperp x Cperp`. This is the
pairwise analogue of MacWilliams and retains intersections that scalar
weight enumerators discard.

For the binary codes, Wave132 already identified the exact finite target:

```text
171,700 raw states,
42,925 even/even states,
7,803 GL(2,2) orbits.
```

For the Wave134 `Z4` code, the full 16-symbol composition space is much
larger. The sensible first object is the distinguished-row Jacobi slice

```text
J_r = sum_(u,c in C)
      product_(i in N(u)) X_(c_i)
      product_(i notin N(u)) Y_(c_i),
```

using the three symmetrized `Z4` symbol classes in each of the 14 and 85
coordinate blocks. Its raw state count is

```text
C(16,2)*C(87,2)=448,920,
```

before parity and torsion symmetries.

### What is new and how to certify it

Wave134 fixes only one-word marginals and aggregate lower coefficients.
Genus two forces all pair marginals to arise from the same labelled code
and applies partial Fourier transforms between `C x C`, `C x Cperp`, and
`Cperp x Cperp`. That is not implied by scalar MacWilliams feasibility.

A certificate is either:

- a complete rational joint enumerator whose every partial transform and
  forced distinguished pair is replayed; or
- an exact Farkas combination of joint-transform, zero, and lower-bound
  rows.

The bottleneck is state growth and integrality. General Clifford--Weil
invariant-ring theorems do not remove this bottleneck here: their strongest
form assumes self-dual isotropic codes
([Nebe--Rains--Sloane](https://arxiv.org/abs/math/0311046)), whereas the
Wave134 `Z4` code is neither self-dual nor self-orthogonal. The additive
`GF(4)` code in Section 1 is the cleaner way to gain self-dual invariant
constraints first.

## 4. `Z8` and the next two-adic layer

### Exact map

The verified Smith form

```text
SNF(A)=diag(1^45,3^9,6,12^43,84)
```

implies

```text
row_Z8(A)  ~= Z8^54 + Z4 + Z2^44,
row_Z8(A)^perp ~= Z4^44 + Z2.                    (7)
```

This is new lift information: reduction modulo four forgets the distinction
between coefficients `1` and `5`, `2` and `6`, and so on.

For `q_u=e_u+r_u`, the exact integral identity is

```text
A q_u = 12e_u + 2*1.
```

Thus for `alpha in Z8^99`, with `s=sum alpha_u`,

```text
A(sum_u alpha_u q_u)=0 mod 8
iff 6 alpha_i+s=0 mod 4 for every i.             (8)
```

For a sparse coefficient vector, some coordinate has `alpha_i=0`, so
(8) reduces to

```text
s=0 mod 4 and every alpha_i is even.
```

In particular `4q_u` and `2(q_u+q_v)` are exact `Z8`-dual words. Some of
these reduce to zero or to already-known words modulo four; their `Z8`
symbol compositions are not fixed by Wave134.

### Certificate form and bottleneck

Under sign symmetrization, the five symbol classes are

```text
{0}, {+/-1}, {+/-2}, {+/-3}, {4}.
```

The corresponding character transform is exact over `Q(sqrt(2))`. A full
length-99 composition table has

```text
C(103,4)=4,421,275
```

states, so a full solve is not the first experiment. Start with a
single-row or two-row Jacobi slice and the sparse dual criterion (8).

A valid negative certificate is an exact Farkas relation over
`Q(sqrt(2))`, represented as pairs of rationals and replayed symbolically.
The bottleneck is the four-million-state full transform, not the Smith
calculation.

## 5. Nonabelian triangle holonomy and covers

### Exact map

Wave133 assigns to each graph triangle a conjugacy class of a permutation

```text
h_T in S_12,
```

whose fixed points are triangular prisms. At the endpoint every `h_T` is a
derangement. The sign character gives only

```text
product_T sign(h_T)=+1,
```

and the Wave133 nonorientable surface control shows that this abelian
parity cannot exclude the endpoint.

The stronger possible translation is a permutation-voltage cover. If the
12-element fibres for overlapping triangles can be coherently identified,
the transition maps define a nonabelian `S_12` cocycle. Every irreducible
representation `rho` of `S_12` then gives a twisted boundary/Laplacian
complex. Face relations, twisted determinants, and character traces
`chi_rho(h_T)` retain much more than the sign.

Permutation voltages do encode arbitrary graph covers; this is the
Gross--Tucker theorem
([primary paper](https://doi.org/10.1016/0012-365X(77)90131-5)).

### Exact boundary

The current data do **not** prove that triangle-star fibres belonging to
different triangles form one global covering. Without that bridge, applying
voltage-cover identities would be invalid.

The smallest experiment is therefore local: take two triangles sharing an
edge or vertex, derive all canonical identifications of their 12-fibres,
and decide whether the resulting transition maps satisfy a gauge-invariant
cocycle equation. The certificate is either an explicit compatible
permutation cocycle or an exhaustive local contradiction with all fibre
labels replayed. Do not begin with global `S_12` character tables.

## 6. Why ordinary Construction A / shadow modular forms are not ready

The standard modular and shadow theorems for `Z4` Construction A concern
self-dual, and often Type II, codes; see Bannai--Dougherty--Harada--Oura
([primary paper](https://sphere.w3.kanazawa-u.ac.jp/BannaiTypeII.pdf)) and
Rains's self-dual `Z4` bounds
([primary record](https://authors.library.caltech.edu/records/tmpmt-dt788)).

The Wave134 code fails the hypotheses sharply:

```text
|C|=2^109, whereas a self-dual length-99 Z4 code has size 2^99;
one adjacency row has self-dot 14=2 mod 4,
so C is not self-orthogonal.
```

Consequently

```text
L(C)=(1/2){z in Z^99 : z mod 4 in C}
```

is not integral: the lifted adjacency row has norm `14/4=7/2`.
Its covolume is `2^99/|C|=2^-10`, also making clear that it is not the
unimodular lattice supplied by a self-dual code. Type I/II shadows,
unimodular theta series, and Clifford--Weil invariant rings cannot be
imported.

One could search for a doubled hyperbolic or discriminant-glued object, but
it must preserve the 99 distinguished rows and have a positive-definite
integral form before modular theta theory becomes relevant. No such bridge
is currently available. The graph-state code in Section 1 captures the
useful self-duality and shadow machinery without asserting a false lattice
construction.

## Literature/status boundary

The searches for this memo checked the current Conway-specific SAT paper
([Keramatipour, 2026](https://arxiv.org/abs/2604.23037)) and targeted
combinations of `srg(99,14,1,2)` with Terwilliger, additive `GF(4)`, and
higher-genus enumerators. No exact hit for the Section 1 construction
combined with the Conway parameters was found. A search no-hit is not a
novelty proof, so external novelty remains `UNKNOWN`.

The sources above establish general methods only. They do not establish
that any ranked route resolves Conway-99, and they do not promote any
repository-derived claim to `VERIFIED`.

## Recommended handoff

Assign three cleanly separated tasks:

1. **Discovery:** first run the two Arf branches against the strongest
   Wave132 system; then derive the 5,050-state graph-code system and every
   forced coefficient through input support three.
2. **Verifier:** independently reconstruct self-duality, the parity-zero
   rows, the coefficient table, and the transform without importing
   discovery code.
3. **Orchestrator:** accept only a full exact rational point or a replayable
   Farkas certificate; treat timeouts and floating solver statuses as
   `UNKNOWN`.

If the graph-code base relaxation is rationally feasible, add in order:
Rains shadow inequalities, the fully refined pure-`X`/pure-`Z` axis split,
and then selected genus-two slices. If it is exactly infeasible, the
certificate excludes the hypothetical graph directly and should be
independently replayed before any status change.
