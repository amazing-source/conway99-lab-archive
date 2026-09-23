# Wave 191 proof A: exact-three exclusion and joint residual amplification

## Verdict

`DERIVED_INDEPENDENT_AUDIT_PASS_PENDING_SEALED_VERIFICATION`.

Under the frozen prism-free rank-11 endpoint assumptions, the number `Q` of
projective short circuits cross-realizing graph nonedges satisfies

```text
Q >= 6237.
```

The result is analytic. It uses the two local star modules at a private
nonedge, the verified conic/complement companion involution, and
label-capacity bookkeeping. It does not enumerate graphs, covers, codes,
configurations, or isomorphism classes.

```yaml
role: proof_a
date_utc: 2026-07-29T02:53:13Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: exclusion of exact-three raw
  circuits inside a type-three 3+6 leaf relation, orbit-closed residual
  capacity, coupled type-two/type-three exact-one usage, and the coefficient
  certificate 12Q>=18C giving Q>=6237.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
  verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256: fc17484bd8c32a5886ecdcc65d153903cef5f3b60a3de1c9905ed96697c273c4
  verification/wave190-residual-stability-verifier/package-manifest.sha256: 15686d17472fd60122072b3d679980d90d3cfe12fd87e5359344e52e216f1280
method: >-
  Two-star module subtraction, center orientation of exact-three companion
  circuits, canonical-C4 Gram-kernel incompatibility, proper-star
  independence, Wave181 exact-two uniqueness, coupled raw-plus-residual
  label capacity, and an exact coefficient identity.
  No graph, cover, code, SAT, configuration, LP, isomorphism, or
  enumeration search.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave191-exact-three-residual-proof-a\exact_check.py --verify
  attempts\wave191-exact-three-residual-proof-a\exact-results.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave191-exact-three-residual-proof-a\test_exact_check.py
outputs:
  - agents/2026-07-29-wave191-exact-three-residual-proof-a.md
  - attempts/wave191-exact-three-residual-proof-a/
limitations:
  - An independent append-only verifier audit passed, but this source
    package has not yet received sealed verifier promotion.
  - The theorem is conditional on the frozen prism-free rank-11 endpoint.
  - The integer row at Q=6237 is an arithmetic null control, not an
    asserted cover, code, graph, circuit family, or endpoint.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain
    UNKNOWN.
```

## 1. Frozen notation

Retain the verified minimal-cover notation. Let `n_i` be the number of
selected circuits of label multiplicity `i`, and let `p_i` count their
private labels. Put

```text
C = 4158,
I = 2*n1+2*n2+3*n3+p2+p3 >= 2*C,
p2 >= n2,
p3 >= n3.
```

The selected cover and selected type-three companions contribute

```text
B = n1+n2+2*n3.
```

The private-label star translations supply

```text
A = n1+2*p2+p3
```

raw assignments. Close every exact-three raw circuit under the verified
companion involution. Write this pool as `r` circuits of exact
cross-multiplicity at most two and `h` complete exact-three companion pairs,
and define

```text
delta = 2*r+3*h-A >= 0.
```

If `r1` low circuits have exact multiplicity one, actual assignment
capacity gives

```text
r1 <= delta.                                     (1)
```

## 2. Local exclusion of exact-three raw circuits

Fix a selected type-three flag `(x,T)` with

```text
T={y,u,v},  e=xy.
```

Let `A_x` be the three `j=2` blocks in the `x`-star. The source
weight-four relation and the full `y`-star relation give

```text
c4(x,T)=z_T+2*sum_(S in A_x) z_S=0,
s_y=sum_(R in S_y) z_R=0,
w_e=c4(x,T)+2*s_y.
```

The `T` coefficient cancels. Thus `w_e` has coefficient two on exactly
three `x`-star blocks and the six blocks of the `y`-star other than `T`.
Its support profile is `3+6`.

Suppose the raw circuit `D` extracted inside `w_e` has exact
cross-multiplicity three. Its three labels form a star and include `xy`,
so its center is either `x` or `y`.

The center cannot be `x`. In that case the unique leaf block of `D` is one
of the six `y`-side blocks. A weight-five member would require four
`x`-star blocks, but only three are available. Hence `D` would be the
weight-four member

```text
D=z_U+2*sum_(S in A_x) z_S.
```

Then `w_e-D` is a nonzero relation supported on the six proper `y`-star
blocks. This contradicts the verified independence of every proper star
subset.

It remains to test center `y`. The six source leaf/common-neighbor
incidences have three leaf types `y,u,v`. Two incidences of the same type
cannot occupy one `x`-star block: those two common neighbors would be
adjacent, and their edge would have both `x` and that leaf as common
neighbors, contradicting `lambda=1`. Thus the three source blocks in `A_x`
pair the types

```text
yu, yv, uv.
```

The target leaf block must be anticomplete to `y`, so it is the unique
source block `S` of type `uv`. Write `S={x,a,b}`, where `a` is adjacent to
`u` and `b` to `v`. For the target flag `(y,S)`, the owner triangle
`T={y,u,v}` has exactly two cross incidences with `S`. Hence `T` is the
target `A_y` block opposite the leaf `x`.

Split the target `y`-star as

```text
A_y={three j=2 blocks},  B_y={four j=0 blocks}.
```

Because `T in A_y` and `w_e` omits `T`, the only target companion member
whose support could be contained in `w_e` is

```text
D=c5=z_S+sum_(R in B_y) z_R.
```

Subtracting twice this relation from `w_e` cancels `S` and all four `B_y`
coordinates. It leaves an all-equal coefficient word

```text
(2,2 | 2,2)
```

on `(A_x minus {S}) union (A_y minus {T})`. This is exactly the canonical
four-block support determined by the two common neighbors of `xy`.
Wave181 independently proves that its one-dimensional relation space has
checkerboard kernel

```text
(1,2 | 2,1)
```

up to scalar and reordering within the two endpoint sides. The all-equal
word is not in that kernel. This contradiction excludes center `y` as
well. Therefore

```text
Every type-three raw leaf extraction has exact multiplicity one or two.
                                                                    (2)
```

Whenever it has exact multiplicity two, Wave181 identifies it as the
canonical checkerboard conic, and the verified Wave190 subtraction forces
a residual assignment for the same private label.

## 3. Coupled raw/residual capacity

Let `t` count type-three raw assignments that land on exact-one circuits,
and put

```text
u=r1-t >= 0.
```

By (2), the other `p3-t` type-three raws are exact-two and force residual
assignments. Let `Z` count residual-assignment incidence that is not
absorbed by the old closed raw pool. Combined raw-plus-residual capacity
gives

```text
A+(p3-t) <= (2*r-r1)+3*h+Z,
p3+u <= delta+Z.                                 (3)
```

Close every genuinely new exact-three residual under the companion
involution. Let `Y` be the number of circuits in this closed new pool. A
low circuit has at most two labels per circuit; an exact-three companion
pair has three labels for two circuits. Thus

```text
Z <= 2*Y,
delta+2*Y >= p3.                                 (4)
```

The new exact-three mate cannot collide with an old pool: every old
exact-three pool is already companion-closed. Privacy excludes the
selected and selected-companion pools.

There is a coupled type-two charge. A selected type-two circuit is itself
the unique exact-two circuit through each of its private labels. Its two
raw translates are distinct from the selected owner, so neither can be
exact-two. All `2*p2` type-two raw assignments therefore land on
exact-one circuits or exact-three raw pairs.

The `t` type-three assignments already occupy `t` of the `r1` exact-one
circuits, leaving at most `u` exact-one slots for type two. Exact-three
pairs have three labels. Hence

```text
2*p2 <= u+3*h.                                   (5)
```

Eliminating `u` between (3)--(5) yields the joint row

```text
delta+3*h+2*Y >= 2*p2+p3.                        (6)
```

## 4. The coefficient certificate

The disjoint selected, companion, closed-raw, and new-residual pools give

```text
Q >= B+r+2*h+Y
  = B+A/2+delta/2+h/2+Y.
```

The penalty is an exact positive combination of (4) and (6):

```text
delta/2+h/2+Y
 = (delta+2*Y)/3+(delta+3*h+2*Y)/6
 >= p2/3+p3/2.
```

Hence

```text
Q >= B+A/2+p2/3+p3/2.                            (7)
```

Multiplying by 12 yields

```text
12*Q
 >= 18*n1+12*n2+24*n3+16*p2+12*p3

  = 9*(2*n1+2*n2+3*n3+p2+p3)
    +6*(p2-n2)+p2+3*(p3-n3)

 >= 18*C.                                        (8)
```

For `C=4158`,

```text
Q >= 3*C/2 = 6237.                               (9)
```

Adding the 693 verified edge-isolated projective circuits gives at least

```text
6237+693 = 6930
```

projective short-circuit classes, hence the circuit-only scalar consequence

```text
B4+B5+B6+B7+B8+B9 >= 13860.
```

Wave188's verified `18018` lower bound for all short dual words remains
numerically stronger because it also counts nonminimal words.

## 5. What happened to the Wave190 sharp row

The Wave190 arithmetic row

```text
n3=1386, p3=4158, h=1386,
n1=n2=p2=r=delta=Y=0
```

packs every type-three raw assignment into an exact-three pair. The local
Gram-kernel contradiction shows that no such raw assignment can exist.
Thus this former sharp row is analytically excluded; no global orbit or
brute-force search is needed.

The new scalar inequality still has an integer arithmetic null control:

```text
n3=p3=2079, n1=n2=p2=h=0,
r=1040, r1=1, delta=1, Y=1039, Q=6237.
```

It satisfies all displayed integer inequalities. It is not an asserted
cover or circuit family. Further progress must use compatibility among
these residual circuits, not only single-label capacity.

## Boundary

```text
conditional Q>=6237 theorem:      DERIVED
Wave190 sharp arithmetic row:     analytically excluded
new Q=5891 arithmetic row:        null control only
independent append-only audit:     pass
sealed verifier promotion:         pending
rank 11 / endpoint excluded:      no
strict n3 improvement:            no
Conway-99 / external novelty:     UNKNOWN
```
