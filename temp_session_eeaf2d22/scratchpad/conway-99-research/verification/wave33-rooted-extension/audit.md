# Wave 33 rooted-extension precomparison clean-room audit

Verdict: **the frozen structural synopsis is independently derived in its
stated necessary-and-sufficient scope; candidate comparison remains
unreleased**

```text
norm-two endpoint root
  ==> forced 14+70+15 partition and quotient
  ==> simple 2-(15,3,2) O-Q design
  ==> exact finite binary (D,B,H) extension criterion
  ==> conditional exact spectrum of H.
```

This does not construct a binary solution, exclude every solution, extend the
rooted endpoint, exclude roots, settle `n3=708`, or resolve Conway-99.  Those
statuses remain `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-24T10:20:59Z
git_commit: b2595baa40d50e9c259051751fe27090bee6a449
claim_label: DERIVED
audit_verdict: PRECOMPARISON_RECONSTRUCTION_PASS
comparison_status: NOT_RELEASED
scope: >-
  Clean-room reconstruction of the frozen Wave 33 rooted synopsis from the
  public Wave 32 actual-incidence root theorem. Derive the 14+70+15 cells,
  quotient, Q independence, simple 2-(15,3,2) design, all six blocks of the
  necessary-and-sufficient binary (D,B,H) criterion, and the conditional
  spectrum of H. Do not inspect or execute the candidate package.
inputs:
  verification/wave33-continuation-protocol.md: b98b6bb8228b54b67cd949ee1bf6eb05ebd6ebe74f1cbc9e49b041a55e2d2fe6
  agents/2026-07-24-wave32-rooted-proof.md: 04990231e3b42cded363e39ffea771556e52ec66fe03a97164ae99f40ddbefe0
  verification/wave32-rooted-vector/audit.md: 36d83232d82e30205e0aefa30aedff0a517de1edb0adbaa54575ea68d04ce1a5
  verification/wave32-rooted-vector/independent-results.json: 4ed239e997e4485abdab4e26a2e28e2a981b6fff069c4d926ccff3d2241dbe6f
method: >-
  Independent exact Fano construction, support-completion incidence,
  lambda/mu double counts, block multiplication, fraction-free ranks,
  invariant-subspace spectral reconstruction, and hostile binary mutations.
command: |-
  cd verification/wave33-rooted-extension
  python -B -m unittest -v test_independent_check.py
  python -B independent_check.py --output independent-results.json
limitations:
  - The discovery report and discovery code remain uninspected.
  - No binary criterion solution is supplied or searched for.
  - The result is conditional on the verified Wave 32 norm-two root support.
  - Quotient and design data alone are not sufficient; every block equation
    and every binary/simple-graph gate remains essential.
  - Rooted extension/exclusion, n3=708, Conway-99, and novelty remain UNKNOWN.
```

## 1. Independence and freeze

The verifier froze the four permitted public inputs and the exact synopsis
before implementation.  It did not open, print, import, execute, hash, or
otherwise inspect:

```text
agents/2026-07-24-wave33-rooted-extension.md
attempts/wave33-rooted-extension/
```

The implementation uses only Python's standard library.  The canonical Fano
plane is regenerated from the seven nonzero vectors of `F_2^3`, not copied
from a candidate or a catalog.

## 2. Forced support and the fixed matrix `D`

Wave 32 supplies signed support classes `P,R`, each of size seven, whose
cross graph is the complement of Fano point-line incidence.  In a canonical
labeling its `7`-by-`7` cross matrix `C` satisfies

```text
C1=C^T1=4*1,
CC^T=2I+2J.
```

Let `F` be the resulting `14`-vertex bipartite adjacency matrix.  It is
simple and 4-regular, with spectrum

```text
4^1, (-4)^1, (+sqrt(2))^6, (-sqrt(2))^6.
```

The 70 outside vertices seeing the support are forced individually:

- one completion for each of the 28 support edges;
- two completions for each of the 21 cross nonedges.

Let `D` be their `14`-by-`70` support incidence matrix.  Every column has
weight two, every row has weight ten, and

```text
rank(D)=13,
ker(D^T)=span((+1)^7,(-1)^7),
F^2+DD^T=12I-F+2J.                                (1)
```

Thus `D` is fixed up to harmless relabeling of the 70 vertices.  No support
automorphism is assumed to extend to a target graph.

## 3. Equitability is a conclusion

Write:

```text
S = signed support,                         |S|=14,
O = outside vertices with two S neighbors, |O|=70,
Q = outside vertices with no S neighbor,   |Q|=15.
```

For `o in O`, sum the number of common neighbors of `o` and `s` over all
`s in S`.  Two support vertices are adjacent to `o`, and twelve are not, so
the SRG side is

```text
2*lambda+12*mu=2+24=26.                          (2)
```

Counting the same length-two paths by the middle neighbor of `o` gives:

- its two `S` neighbors contribute `2*4=8`;
- every `O` neighbor contributes its two `S` neighbors;
- every `Q` neighbor contributes zero.

Equation (2) therefore forces

```text
deg_O(o)=9,
deg_Q(o)=3.                                      (3)
```

For `q in Q`, all fourteen support vertices are nonneighbors.  Summing their
two common neighbors gives 28.  Each `O` neighbor contributes two and each
`Q` neighbor zero, so

```text
deg_O(q)=14,
deg_Q(q)=0.                                      (4)
```

In particular, `Q` is independent.  Equations (3)--(4) prove, rather than
assume, the equitable quotient

```text
       S  O  Q
S      4 10  0
O      2  9  3
Q      0 14  0.                                  (5)
```

Its spectrum is `14,3,-4`, as required.

## 4. The simple `2-(15,3,2)` design

Let `B` be the `70`-by-`15` O-Q incidence matrix.  Equation (5) gives row
weight three and column weight fourteen.  Since `Q` is independent, two
distinct Q vertices have exactly `mu=2` common neighbors, all in `O`.
Therefore

```text
B^T B=12I_15+2J_15.                              (6)
```

So the rows of `B` are the blocks of a `2-(15,3,2)` design.  It is simple:
duplicate rows would give two distinct O vertices at least three common Q
neighbors, exceeding both possible target pair counts, one and two.

## 5. Exact finite binary criterion

Let `H` be the induced adjacency matrix on `O`.  In cell order `S,O,Q`, any
extension must be

```text
A = [ F   D   0 ]
    [ D^T H   B ]
    [ 0   B^T 0 ].                               (7)
```

The target identity is

```text
A^2=12I-A+2J.                                    (8)
```

Block multiplication gives exactly:

```text
SS: F^2+DD^T                 =12I_14-F+2J_14,
SO: FD+DH                    =2J_(14x70)-D,
SQ: DB                       =2J_(14x15),
OO: D^TD+H^2+BB^T            =12I_70-H+2J_70,
OQ: HB                       =2J_(70x15)-B,
QQ: B^TB                     =12I_15+2J_15.       (9)
```

Necessity is immediate from (7)--(8).  Sufficiency needs every gate:

```text
B binary 70x15, row sums 3, column sums 14, distinct rows;
H binary 70x70, symmetric, zero diagonal, row sums 9;
all six equations in (9).
```

Under those conditions, (7) is a simple symmetric zero-diagonal binary
matrix and (9) reassembles every block of (8).  The diagonal of (8) gives
degree 14; its off-diagonal entries give `lambda=1` on edges and `mu=2` on
nonedges.  Thus (7) is an `srg(99,14,1,2)`.

The verifier compares the six residuals against the corresponding blocks of
the direct 99-by-99 residual for deterministic hostile `B,H`; every block
agrees, while the hostile input fails the criterion.

This criterion uses no orbit, transitivity, Cayley, circulant, or other
automorphism restriction.  Choosing canonical `F,D` merely labels an already
forced configuration.

## 6. Conditional spectrum of `H`

Equation (6) gives `rank(B)=15`; equation (1) gives `rank(D)=13`.  The
relations in (9) yield orthogonal H-invariant spaces:

```text
span(1_O):                           eigenvalue 9, dimension 1;
B(1_Q^perp):                         eigenvalue -1, dimension 14;
D^T(F-eigenspace +sqrt(2)):          eigenvalue -1-sqrt(2), dimension 6;
D^T(F-eigenspace -sqrt(2)):          eigenvalue -1+sqrt(2), dimension 6.
```

The centered `D` and `B` images are orthogonal because `DB=2J`.  Their
orthogonal complement

```text
W=ker(D) intersect ker(B^T) intersect 1_O^perp
```

has dimension

```text
70-1-12-14=43.
```

The OO equation restricts on `W` to

```text
H^2+H-12I=0,
```

so only eigenvalues `3,-4` remain.  Since `H` has zero diagonal, its trace is
zero; the remaining multiplicities are 27 and 16.  Hence every criterion
solution has

```text
spec(H)=
  9^1,
  (-1)^14,
  (-1+sqrt(2))^6,
  (-1-sqrt(2))^6,
  3^27,
  (-4)^16.                                       (10)
```

Checks from (10) give

```text
tr(H^2)=630,  |E(H)|=315,
tr(H^3)=336,  triangles(H)=56.
```

These are necessary consequences, not an existence certificate.

## 7. Objections and status wall

The full adversarial ledger is `failed-objections.md`.  The strongest
remaining objection is not an arithmetic defect:

> No binary `B,H` satisfying (9) has been supplied or excluded.  The finite
> criterion is an exact reformulation of the rooted continuation, not its
> solution.

Current status:

```text
14+70+15 quotient and Q independence: DERIVED
simple 2-(15,3,2) design:             DERIVED
criterion necessity and sufficiency:  DERIVED
conditional H spectrum:               DERIVED
binary criterion solution:            UNKNOWN
rooted endpoint extension/exclusion:  UNKNOWN
n3=708, Conway-99, novelty:            UNKNOWN
candidate comparison:                 NOT RELEASED
```

The standard-library suite passes eighteen tests and emits deterministic
LF-only JSON.
