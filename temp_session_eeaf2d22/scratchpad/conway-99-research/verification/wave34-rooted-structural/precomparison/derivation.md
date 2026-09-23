# Clean-room projector and pair-structure derivation

## Claim and domain

Conditional on the independently verified Wave 33 six-block criterion, this
report derives consequences that hold for **every** unrestricted binary pair
`(D,B)`. It does not construct such a pair and does not exclude all such
pairs.

Use the following notation:

```text
A_S : fixed 14 x 14 signed-Fano support adjacency;
F   : fixed 14 x 70 support-to-O incidence;
D   : arbitrary symmetric hollow binary 70 x 70 O adjacency;
B   : arbitrary binary 70 x 15 O-Q incidence;
T   := F^T F;
R   := B B^T;
J   := J_70;
P_0 := J/70.
```

The imported exact blocks used below are

```text
A_S F+F D = 2J-F,
F B       = 2J,
T+D^2+R   = 12I-D+2J,
D B       = 2J-B,
B^T B     = 12I+2J.
```

The known row and column weights are

```text
F 1=10 1,  F^T 1=2 1,
B 1= 3 1,  B^T 1=14 1,
D 1= 9 1.
```

All divisions below are divisions by displayed nonzero integers over
`Q`. No without-loss-of-generality step is used.

## Lemma 1: the two Gram algebras meet only on the constant line

From `B^T B=12I+2J`,

```text
rank(B)=15,
R^2=12R+18J,
spec(R)=42^1,12^14,0^55.
```

From `FB=2J`,

```text
TR=RT=12J.                                          (1)
```

The fixed Fano support gives

```text
rank(F)=13,
spec(T)=20^1,(10-sqrt(2))^6,(10+sqrt(2))^6,0^57,
T(T-20I)(T^2-20T+98I)=0.                           (2)
```

Therefore the exact orthogonal projectors onto `im(F^T)` and `im(B)` are

```text
P_F = T(T^2-40T+498I)/1960,                         (3)
P_B = R/12-J/28.                                    (4)
```

Exact substitution at every root of (2), together with (1), gives

```text
P_F^2=P_F,  P_B^2=P_B,
P_F P_B=P_B P_F=P_0.                               (5)
```

Thus the two images intersect exactly in `span(1)`. Their sum has dimension

```text
13+15-1=27.
```

Its orthogonal complement is

```text
W = ker(F) intersect ker(B^T),
E = I-P_F-P_B+P_0,
dim(W)=43,                                          (6)
```

where `E` is the orthogonal projector onto `W`.

The checker constructs the fixed labeled `F` directly and evaluates (3)
entry by entry. Its leverage values are not assumed from an orbit argument:

```text
O label type                    count   (P_F)_ii
support-edge completion            28      97/490
support-nonedge copy               42      87/490. (7)
```

## Lemma 2: only a 43-dimensional residual action remains

Transpose the S-O block. On `im(F^T)`, use the exact support eigenvalues
`4,-4,+sqrt(2),-sqrt(2)` and `ker(F^T)=span(k)` to obtain

```text
D P_F=T-11P_F.                                      (8)
```

The O-Q block gives

```text
D P_B=-P_B+10P_0,   D P_0=9P_0.                    (9)
```

Equations (8)-(9) are symmetric, so `D` commutes with all four projectors
`P_F,P_B,P_0,E`. Define

```text
L := D(I-E)=T-11P_F-P_B+P_0,
K := DE=ED=EDE.
```

Then every binary solution has the exact decomposition

```text
D=L+K.                                              (10)
```

The action `L` on the 27-dimensional combined row space is fixed once `B`
fixes its Gram projector `P_B`; every surviving linear degree of freedom is
confined to the 43-dimensional space `W`.

Projecting the O-O block with `E` kills `T,R,J` and yields

```text
K^2+K-12E=0.                                       (11)
```

Also

```text
tr(L)=tr(T)-11tr(P_F)-tr(P_B)+tr(P_0)
     =140-143-15+1=-17.
```

Since `D` is hollow, `tr(K)=17`. Hence the two roots of (11) have forced
multiplicities

```text
K eigenvalue  3: 27,
K eigenvalue -4: 16.                               (12)
```

The exact residual spectral projectors are

```text
E_3  =(K+4E)/7,
E_-4 =(3E-K)/7.                                    (13)
```

Expanded in criterion data,

```text
E_3  =P_F+(D-T+4I)/7-R/28+3J/140,
E_-4 =(-D+T+3I)/7-2P_F-R/21+J/35.                 (14)
```

They are orthogonal projectors of ranks 27 and 16. Because `D_ii=0`,
`T_ii=2`, `(P_B)_ii=3/14`, and `(P_0)_ii=1/70`, (7) and (13) force:

```text
label type              E_ii   K_ii  (E_3)_ii  (E_-4)_ii
support edge            59/98  37/98    39/98       10/49
support nonedge copy    61/98  15/98    37/98       12/49. (15)
```

Thus even the coordinate leverage of each residual eigenspace is fixed by
the labeled support type; it is not a free spectral multiplicity statement.

## Lemma 3: the global projectors have exact O-block ranks

For a putative `srg(99,14,1,2)`, the global primitive projectors are

```text
Pi_3  =(A+4I)/7-2J/77,
Pi_-4 =(-A+3I)/7+J/63.
```

Their O principal blocks are therefore

```text
Pi_3[O,O]  =(D+4I)/7-2J/77,
Pi_-4[O,O] =(-D+3I)/7+J/63.                        (16)
```

Evaluating (16) on the six invariant summands in the exact spectrum gives

```text
rank Pi_3[O,O]  =54,  nullity=16=im(E_-4),
rank Pi_-4[O,O] =43,  nullity=27=im(E_3).          (17)
```

Their diagonals are respectively `6/11` and `4/9`. The missing forty-fourth
global minus-four direction is the signed root supported entirely on `S`.

## Lemma 4: all unordered O-pairs fall into nine states

For distinct `i,j in O`, define

```text
g_ij := T_ij       = number of shared support neighbors;
r_ij := R_ij       = number of shared Q neighbors;
h_ij := D_ij       = adjacency indicator;
c_ij := (D^2)_ij   = number of shared O neighbors.
```

The O-O block is entrywise

```text
g_ij+r_ij+h_ij+c_ij=2.                             (18)
```

All four terms are nonnegative integers, with `g,r in {0,1,2}` and
`h in {0,1}`. Thus exactly nine states are possible:

```text
(g,r,h,c) =
(0,0,0,2), (0,0,1,1), (0,1,0,1), (0,1,1,0),
(0,2,0,0), (1,0,0,1), (1,0,1,0), (1,1,0,0),
(2,0,0,0).                                         (19)
```

In particular, a pair sharing two support neighbors or two Q neighbors is
nonadjacent and has no common O neighbor.

For each row, the fixed support labels give

```text
support-edge label:       #g=1 is 18, #g=2 is 0;
support-nonedge copy:     #g=1 is 16, #g=2 is 1.
```

The simple `2-(15,3,2)` design gives, for every row,

```text
#r=2 is 3, #r=1 is 33, #r=0 is 33.                 (20)
```

The diagonal entries of the commuting product identities give

```text
(DT)_ii = 0 for a support-edge label, 2 otherwise;
(DR)_ii = 3;
(TR)_ii =12.                                        (21)
```

Since `T_ii R_ii=2*3=6`, equations (18) and (21) force every vertex to have
exactly six partners with `g=r=1`. Combining (18)-(21), degree nine, and
the two support-label types gives a full-rank `9 x 9` integer system. Its
unique row distributions are:

```text
(g,r,h,c)       support edge row   support nonedge-copy row
(0,0,0,2)             15                       18
(0,0,1,1)              6                        4
(0,1,0,1)             24                       24
(0,1,1,0)              3                        3
(0,2,0,0)              3                        3
(1,0,0,1)             12                        8
(1,0,1,0)              0                        2
(1,1,0,0)              6                        6
(2,0,0,0)              0                        1. (22)
```

Aggregating 28 rows of the first type and 42 of the second, then dividing
ordered counts by two, partitions all `C(70,2)=2415` pairs:

```text
(g,r,h,c)   unordered pairs
(0,0,0,2)        588
(0,0,1,1)        168
(0,1,0,1)        840
(0,1,1,0)        105
(0,2,0,0)        105
(1,0,0,1)        336
(1,0,1,0)         42
(1,1,0,0)        210
(2,0,0,0)         21.                            (23)
```

## Corollary: six forced relation graphs

The pair partition is equivalent to the following unrestricted labeled
constraints:

1. The graph `X_11` of pairs sharing exactly one support neighbor and one Q
   neighbor is 6-regular on all 70 vertices, has 210 edges, and is disjoint
   from both `D` and the off-diagonal support of `D^2`.
2. The graph of pairs sharing two Q neighbors is 3-regular on all 70
   vertices, has 105 edges, and is likewise disjoint from `D` and `D^2`.
3. The 21 fixed duplicate-support-label pairs form a matching on the 42
   support-nonedge-copy vertices; paired B rows are disjoint, nonadjacent,
   and have no common O neighbor.
4. The D-edges whose unique common neighbor lies in `S` form a 2-factor on
   those same 42 vertices, with 42 edges.
5. The D-edges whose unique common neighbor lies in `Q` form a 3-regular
   spanning graph with 105 edges.
6. The remaining 168 D-edges form 56 edge-disjoint O-triangles. Every
   support-edge completion lies in three such triangles and every
   support-nonedge copy lies in two.

These are consequences for the complete labeled domain, not a search over
one design or one symmetry class.

## Machine replay

Environment and command:

```text
Python 3.13.14
standard library only
seed: none

python -B -m unittest discover -s verification/wave34-rooted-structural/precomparison -p test_*.py -v
python -B verification/wave34-rooted-structural/precomparison/exact_check.py --output verification/wave34-rooted-structural/precomparison/exact-results.json
```

The suite has 13 tests. It reconstructs the canonical fixed support, checks
all frozen hashes, evaluates the 70-by-70 rational projector exactly,
checks all formulas on the six exact invariant summands in
`Q(sqrt(2))`, solves the full-rank pair-state systems, checks every global
count, rejects a bad projector division, and checks a hostile mutation of
`TR=12J`.

## Failed routes and strongest objection

- The projector split does not make the residual `K` binary. Its entries are
  affine shifts of the binary entries of `D`, and `E` itself depends on the
  unknown B Gram matrix.
- Positive-semidefinite diagonal checks for `E_3` and `E_-4` are feasible;
  they do not give a contradiction.
- The nine pair states and their exact census substantially constrain the
  labeled domain but do not enumerate compatible global placements.
- No Smith-normal-form claim is made: rational rank and orthogonal projection
  do not by themselves determine the integral lattice of solutions.

The strongest self-objection is that (10)-(23) are exact consequences and
structural reductions, but remain repackagings of necessary conditions from
the complete criterion. They neither exhibit a binary pair nor prove that
none exists.
