# Wave 19 residual-B outside-Gram proof-theory audit

Verdict: **PASS / DERIVED for the fixed-case Gram-obstruction logic, with
strict scope limits.**  For any *exactly reconstructed* residual-B induced
graph `D=L(F) union R union Z`, the identity

```text
G := 12I-D-D^2+2J = C C^T
```

is necessary, where `C` is the binary incidence matrix from the thirty
vertices of `X` to the sixty-nine outside vertices.  Every nonzero column of
an actual `C` belongs to the finite necessary-support set defined by
column-space membership, exclusion of pairs with `G_ij=0`, and
`D c <= 2*1-c`.  Therefore an exact proof that `G` is not a nonnegative
integer sum of the corresponding outer products `c c^T` excludes that fixed
`(F,R,Z)` case.  An exact Farkas separator with negative value on `G` and
nonnegative value on every candidate outer product excludes even
nonnegative-real multiplicities.

These statements do **not** establish that all `(F,R,Z)` cases have been
covered, do not inspect or validate any prospective closure certificate, and
do not resolve residual B.  Residual B, conditional `n3=60`, Conway-99, and
novelty remain `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T14:57:13Z
git_commit: d4e8b9df7800ec1aeda599f2bd90f49cf75d8d81
claim_label: DERIVED
audit_verdict: PASS_FOR_FIXED_CASE_LOGICAL_SCHEME_ONLY
scope: >-
  Independent proof-theory audit of the outside-Gram obstruction for a fixed
  residual-B r=20,m=30 point-model case; no candidate package inspected and
  no residual or target exclusion claimed.
inputs:
  verification/2026-07-23-wave19-n3-60-structural-audit.md: f6f318aa187fe5790a14dcbf7eeded7c296b1d6734c710b4569ede690e0c762a
  verification/n3-60-closure/2026-07-23T140227Z-preinspection-freeze.md: 05111263664277f446217fd43aa1b4b494be611285ea44cf2e643845dc43b34b
  verification/n3-60-closure/2026-07-23T143251Z-independent-baseline.md: 237ec151c461ff6258d3c359e7cecf21d3c9655ba1ee98b54f75e890babaf2c2
method: >-
  Direct block expansion of the SRG matrix equation, exact common-neighbor
  counting, real column-space linear algebra, and conic duality.  The
  alternate-frontier directory and all prospective candidate outputs were
  excluded from inspection.
command: >-
  PowerShell Get-FileHash -Algorithm SHA256 on the three listed input files;
  no discovery program, solver, candidate checker, or Git command was run.
outputs:
  report: hash recorded in the sibling .sha256 file after this write
limitations: >-
  Conditional on the already-audited r=20,m=30 indexed-point model and on D
  being the complete induced graph for a fixed case.  This audit proves the
  obstruction scheme, not the completeness or correctness of any catalog,
  support enumeration, multiplicity result, or Farkas certificate.
```

The `git_commit` value was read directly from `.git/HEAD` and its referenced
file; no Git command or Git write was used.

## 1. Exact identity and notation

Let `A` be the adjacency matrix of an `srg(99,14,1,2)`.  The standard
common-neighbor count gives

```text
A^2 = (14-2)I + (1-2)A + 2J
    = 12I-A+2J.                                          (1)
```

Let `X` be the thirty indexed vertices in the residual-B point model and let
`Y` be its sixty-nine-vertex complement.  Write

```text
    A = [ D   C ]
        [ C^T E ],
```

where `D=A[X]`, `C=A[X,Y]`, and `E=A[Y]`.  Taking the `X`-by-`X` block of
(1) gives

```text
D^2 + C C^T = 12I-D+2J,
G := 12I-D-D^2+2J = C C^T.                              (2)
```

Thus item (i) is **PASS / DERIVED**.  The letter `G` is used here for the
Gram matrix to avoid the baseline's different use of `B` for the incidence
matrix.  In the notation of the question, `G` is its `B`.

For residual B, `D` must be the *complete induced graph*

```text
D = L(F) union R union Z
```

on the thirty indexed point vertices.  The identity is invalid if this is
only a known subgraph of `G[X]`, if a permitted `Z` edge was omitted, or if
an edge was inserted that the point model forbids.

## 2. Why the factor is binary, and the exact completeness scope

The entries of `C` are adjacency indicators between two disjoint vertex
sets:

```text
C_xz = 1  iff  x in X is adjacent to z in Y.
```

Consequently `C` is a `30`-by-`69` zero-one matrix.  An arbitrary real
Cholesky factor of `G` is not a substitute.

For each inside vertex `i`, and each pair `i != j`, (2) says exactly

```text
number of outside neighbors of i       = G_ii
number of common outside neighbors i,j = G_ij.
```

Equivalently,

```text
G_ii = 14-d_D(i),
G_ij = 1-(D^2)_ij   if D_ij=1,
G_ij = 2-(D^2)_ij   if D_ij=0.                          (3)
```

Hence every entry of `G` must be a nonnegative integer and `G` must be
positive semidefinite.  These tests are necessary but are not sufficient
for a binary factor.

Equation (2), with `C in {0,1}^{30 x 69}`, is a **complete characterization
of the top-left SRG block**.  It includes all row weights and all pairwise
row intersections.  If `c_z` is column `z` and `a_z=1^T c_z`, it also gives
the exact moment identities

```text
sum_z a_z   = trace(G),
sum_z a_z^2 = 1^T G 1.                                  (4)
```

Those moments alone are not complete.  Nor is (2) a characterization of a
full SRG lift: the same `C` must also admit a binary symmetric zero-diagonal
outside graph `E` satisfying the other two blocks of (1),

```text
D C + C E       = 2J-C,                                 (5)
C^T C + E^2     = 12I-E+2J.                             (6)
```

Item (ii) is therefore **PASS / DERIVED for the binary and top-left-block
claims**, and **UNKNOWN for full-lift existence**.

## 3. Necessary individual-column support filters

Fix `D` and its recomputed `G`.  Define the nonzero candidate set

```text
S(D,G) = { c in {0,1}^30 \ {0} :
           c in col_R(G),
           c_i c_j=0 whenever G_ij=0,
           D c <= 2*1-c coordinatewise }.
```

Every nonzero column of an actual outside-incidence matrix belongs to this
set:

1. **Column space.**  From `G=C C^T`,
   `im(G)=im(C)`.  Indeed, `im(G)` is contained in `im(C)`, while
   `ker(C C^T)=ker(C^T)` over the reals, so the two images have the same
   rank.  Each column of `C` is therefore in `col_R(G)`.

2. **Zero-pair exclusion.**  For `i != j`,
   `G_ij=sum_z C_iz C_jz`.  Every summand is nonnegative.  If `G_ij=0`, no
   column can contain both `i` and `j`.

3. **One-column common-neighbor bound.**  Column `z` of (5) is

   ```text
   D c_z + C E[:,z] = 2*1-c_z.
   ```

   The second term is entrywise nonnegative, so
   `D c_z <= 2*1-c_z`.  Coordinate `i` says that the common neighbors of
   `i` and `z` already lying in `X` cannot exceed `lambda=1` when
   `c_z(i)=1`, or `mu=2` when `c_z(i)=0`.

The zero column may be omitted from `S`: it contributes the zero outer
product, passes every displayed inequality, and can be used only to pad the
outside-vertex count.  It must be restored explicitly if a proof uses an
exact `69`-column count.

These three filters **characterize the declared candidate set**, provided
the enumeration really examines all `2^30` binary vectors or has a separately
checked complete equivalent.  They do **not** characterize actual outside
vertices.  In particular, the nonnegative remainder

```text
2*1-c-Dc
```

must eventually equal a sum of columns selected by an adjacency column of
`E`, with all zero-diagonal, symmetry, degree, and bottom-block constraints
coherent across the sixty-nine vertices.  Dropping those stronger
constraints enlarges the search and is safe for a nonexistence proof.

Item (iii) is **PASS / DERIVED as an exhaustive necessary-support
relaxation**, not as a sufficient lift criterion.

## 4. Multiplicity and exact Farkas contradictions

Because columns may repeat, associate a multiplicity `m_c` to every
`c in S(D,G)`.  Any actual lift necessarily yields

```text
m_c in Z_{\ge 0},
G = sum_{c in S(D,G)} m_c c c^T.                        (7)
```

Zero columns make no contribution.  If the exact number of columns is being
used, one must additionally require

```text
sum_{c != 0} m_c <= 69
```

and pad with `69-sum m_c` zero columns.  Omitting this bound relaxes (7);
infeasibility of the relaxed system is still decisive.

There are three sound exact exclusion routes:

1. exact row reduction shows that the linear equations in (7) are
   inconsistent even over the rationals;
2. a checkable integer argument shows that no nonnegative integral
   multiplicities solve (7); or
3. an exact conic/Farkas separator rules out even nonnegative real
   multiplicities.

For route 3, fix one coordinate convention, for example the upper-triangular
entries `i<=j` counted once.  Let `y_ij` be exact rational weights.  If

```text
sum_{i<=j} y_ij G_ij < 0,                               (8)
sum_{i<=j} y_ij c_i c_j >= 0  for every c in S(D,G),    (9)
```

then (7) would imply

```text
sum y_ij G_ij
  = sum_c m_c (sum y_ij c_i c_j) >= 0,
```

contradicting (8).  Integer weights are especially easy to replay.  The
checker must use the same convention on off-diagonal entries on both sides;
silently doubling them in only one place invalidates the certificate.

A floating optimizer's status, a rounded dual vector, or a separator tested
on only a restricted sample is not evidence.  A valid certificate requires
exact weights, an exactly recomputed target value, and an exhaustive exact
check of (9) for every candidate support.  Subject to those requirements,
item (iv) is **PASS / DERIVED for a fixed `(F,R,Z)` case**.

## 5. Safe omissions versus invalidating omissions

The following omissions weaken the obstruction but do not invalidate an
infeasibility result, because they admit more possibilities:

- not imposing the at-most-69 nonzero-column bound;
- not imposing individual outside degrees beyond what follows from the
  displayed inequalities;
- not requiring the remainder `2*1-c-Dc` to be assembled from other
  columns;
- not constructing a common symmetric outside adjacency matrix `E`;
- not checking the bottom block (6); and
- retaining candidate supports that later local rules could delete.

By contrast, any of the following is fatal to the claimed scope:

- `D` is not the exact induced graph for the fixed labeled `(F,R,Z)` case;
- the upstream enumeration omits an allowed `F`, `R`, or labeled `Z`
  placement, or uses an orbit quotient not proved valid for the already
  fixed structure;
- a candidate-column generator omits even one binary vector satisfying the
  stated filters, uses an unproved additional restriction, or computes
  column-space membership with floating tolerances;
- repeated column supports are forbidden, multiplicities are assumed
  zero-one, or zero columns are omitted while an exact column count is used;
- only row/column moments, entrywise nonnegativity, rank, or PSD are treated
  as a binary-factor certificate;
- the multiplicity contradiction is only a solver exit code without an
  independently checkable exact proof;
- a Farkas sign, coordinate, or off-diagonal normalization is inconsistent;
  or
- a contradiction established for one case is promoted to residual-B
  closure without a complete per-case coverage ledger.

## 6. Status boundary

```text
SRG block identity G=C C^T:                  PASS / DERIVED
C binary and top-left-block completeness:   PASS / DERIVED
three candidate-column filters necessary:   PASS / DERIVED
multiplicity/Farkas exclusion implication:  PASS / DERIVED per fixed case
any prospective certificate or case count:  NOT INSPECTED
coverage of every F/R/Z case:                UNKNOWN
residual B:                                  UNKNOWN
conditional n3=60:                           UNKNOWN
Conway-99 target:                            UNKNOWN
novelty:                                     UNKNOWN
```

This report validates a proof rule, not an application of that rule.
