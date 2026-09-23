# Wave 41 failed and bounded routes

## 1. Full-rank border projection

An attempted continuation began with the symmetric-border lemma

```text
rank [P U; U^T W] >= rank(P)+2 rank(H^T U),
```

where `H` spans `ker(P)`. It is false that the outside incidence constraints
make `H^T U` full row rank. Every triangle block contains the three
independent vectors

```text
h_v=(A+4I)e_v,  v in T,
```

and all three lie in `ker(U^T)`. This is an exact universal obstruction, not
a failed heuristic. See the polynomial and column checks in `README.md`.

## 2. Adding nominal ranks of overlapping blocks

Two principal blocks of rank 25 do not supply 50 independent global
directions. Principal rank is not additive under overlap, and the compact
kernel vectors are globally repeated vertex-star columns. No valid
submodular or inclusion-exclusion inequality for these symmetric principal
ranks was found. Any future packing argument must identify actual independent
row or column minors after quotienting the common structural space.

## 3. One-triangle floor 31 or 33

Random Wave 40 scouts often had ranks 34--36, but those minima were not
exhaustive. Exact controls in this package have ranks 28 and 29; the latter
has a triangle-free core. Hence sample minima cannot justify a 31 or 33
local theorem. The controls do not show that a full 99-vertex completion has
such low rank.

## 4. Even-part equality search

For an all-odd type, `P+Q` is invertible and rank-25 equality reduces to the
single Schur equation recorded in the package. When an even part occurs,
`P+Q` has a radical of dimension twice the number of even parts. Equality
first requires the projected permutation columns to span the minimum
dimension and then requires the induced bilinear form on the remaining
right kernel to agree with `P+R`.

A discovery-side frontier enumeration found the following numbers of
minimum-projection permutations:

```text
1+1+1+1+2 : 80,640
1+1+2+2   :    192
1+1+4     :    768
1+2+3     : 80,640
2+2+2     :     32
2+4       :     64
6         :  2,592
```

These counts are diagnostic only in this package: the subsequent exhaustive
perfect-matching compatibility test for `R` was not completed or
certificate-packaged. They must not be read as a rank-25 existence or
nonexistence result. A continuation should canonicalize the induced
right-kernel bilinear constraints and solve the 66-edge perfect-matching
system once per canonical constraint, with a checkable orbit or UNSAT
certificate.

## 5. Seven independent vertex-stars

Seven independent vertices expose a 49-triangle principal block, but the 21
nonadjacent-pair cross blocks are not independent variables. Repeating the
Wave 35 one-pair control would silently discard shared common neighbours,
shared graph edges, and the global identity `M^2=21M`. No gluing enumeration
was performed, so this route remains an exact target rather than evidence
for or against the endpoint.
