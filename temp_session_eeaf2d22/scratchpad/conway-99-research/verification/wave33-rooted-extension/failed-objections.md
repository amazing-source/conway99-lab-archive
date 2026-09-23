# Wave 33 rooted-extension precomparison objections

## V33-R-O01: the three-cell partition may not be equitable

**Attack.**  Wave 32 supplies only the support-neighbor types of outside
vertices.  It does not state their O/Q degrees.

**Disposition.**  Objection defeated.  Summing common-neighbor counts over
the fourteen support vertices forces every O vertex to have nine O and three
Q neighbors, and every Q vertex to have fourteen O and zero Q neighbors.
Equitability and Q independence are conclusions, not hypotheses.

## V33-R-O02: `B` may be a weighted or repeated-block design

**Attack.**  The equation `B^TB=12I+2J` alone does not say that rows are
distinct triples.

**Disposition.**  Binary graph incidence and the quotient give row weight
three.  Duplicate rows would make two O vertices share at least three Q
neighbors, impossible whether that pair is adjacent (`lambda=1`) or
nonadjacent (`mu=2`).  The design is simple.

## V33-R-O03: canonical `D` may assume an extending automorphism

**Attack.**  Fixing a Fano labeling and ordering the 70 O vertices could
discard extensions whose graph automorphisms do not preserve that labeling.

**Disposition.**  Objection defeated.  Wave 32 forces the support up to
relabeling.  Each support edge has one O completion and each support cross
nonedge has two.  Labeling those vertices fixes `D` but imposes no equation
on `B,H` beyond target incidence.  No support automorphism is required to
extend.

## V33-R-O04: quotient plus design could be advertised as sufficient

**Attack.**  Equitable degrees and a `2-(15,3,2)` design do not control O-O
common neighbors or compatibility with the support.

**Disposition.**  Valid objection.  The verifier retains all SO, SQ, OO, OQ,
and QQ equations, plus the fixed SS equation.  Dropping any unverified block
invalidates sufficiency.

## V33-R-O05: necessity may omit a block of the SRG identity

**Attack.**  A compact criterion can accidentally enforce only diagonal
degrees and some cross blocks.

**Disposition.**  Objection defeated for the verifier criterion.  Direct
99-by-99 multiplication is compared against six separately constructed
residuals:

```text
SS, SO, SQ, OO, OQ, QQ.
```

They are exactly the blocks of `A^2-(12I-A+2J)`.

## V33-R-O06: sufficiency might prove only a weighted matrix identity

**Attack.**  Matrix equations do not by themselves make `A` a simple graph.

**Disposition.**  Binary `B,H`, symmetry and zero diagonal for `H`, the fixed
binary simple `F,D`, and zero S-Q/Q-Q blocks are explicit gates.  With them,
the assembled `A` is a simple adjacency matrix.  The diagonal and
off-diagonal entries of the SRG identity then give all target parameters.

## V33-R-O07: `H` spectrum could import full-graph multiplicities without proof

**Attack.**  Interlacing does not determine the spectrum of an induced
70-vertex subgraph.

**Disposition.**  Objection defeated without interlacing.  The spectrum is
derived from invariant subspaces forced by `HB=2J-B`,
`HD^T=2J-D^T-D^TF`, and the OO equation.  Exact ranks give a 43-dimensional
residual space satisfying `(H-3I)(H+4I)=0`; trace zero fixes multiplicities
27 and 16.

## V33-R-O08: the centered `D` and `B` spaces might overlap

**Attack.**  The spectral dimension count would fail if their images were not
orthogonal or intersected unexpectedly.

**Disposition.**  `DB=2J` makes

```text
<D^Tx,By>=x^TDB y=0
```

for centered `x,y`.  `rank(D)=13`, with the signed support vector as the only
kernel of `D^T`; `rank(B)=15` follows from the positive-definite
`B^TB=12I+2J`.  The centered image dimensions are exactly 12 and 14.

## V33-R-O09: a simple `2-(15,3,2)` design could solve the extension

**Attack.**  The design is a strong finite object and might be mistaken for
a graph construction.

**Disposition.**  Valid objection.  A design must also be assigned to the 70
fixed D-columns and coupled to a 9-regular binary H satisfying SO, SQ, OO,
and OQ.  No such joint object is supplied here.

## V33-R-O10: candidate agreement could contaminate clean-room status

**Attack.**  Reading candidate prose or code before freezing the independent
implementation would turn agreement into post-hoc reconstruction.

**Disposition.**  Candidate comparison remains `NOT_RELEASED`.  Candidate
paths were neither opened nor executed before this package freeze.

## Strongest remaining objection

The exact finite criterion is still unsolved:

```text
binary (B,H) satisfying every gate and block equation: UNKNOWN.
```

A necessary-and-sufficient reduction is not an extension or an exclusion.
The root branch and every global target status remain `UNKNOWN`.
