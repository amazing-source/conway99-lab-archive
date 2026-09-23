# Independent verification of Wave 142

Verdict: `PARTIAL_PASS_WITH_TOP_BAND_VETO`.

The discovery package is frozen at manifest SHA-256
`241cb75308d26942adf6dcdfc3b1c344c3c48fee35df2b9eeb1561fa2b01b443`.
All nine package entries and all five prerequisite hashes pass.  The
discovery test suite passes six tests; the clean-room hostile suite passes
ten tests.  Host memory remained above 40% free.

The four order-six interlace rows, kernel moment, local diagonal-toggle
census, IAS transversal identities, and weak nonnegativity bounds verify.
The claimed target-forced complement band from subset size 86 through 99
does not: the frozen target premise supports only sizes 92 through 99.

## Verified order-six interlace rows

The verifier independently enumerated all 62 locally admissible six-vertex
classes, replayed the frozen Wave21 source alignment, computed every
principal adjacency rank over `F_2`, and obtained

```text
I_(6,0)=  45845415 + (4/3)n3
I_(6,2)= 470213205 - 3n3
I_(6,4)= 503184528 + (4/3)n3
I_(6,6)= 101286108 + (1/3)n3.
```

The slopes sum to zero and the constants sum to `binom(99,6)`.  Fresh
vertex-deletion descent also reproduces all lower rows through size five.
Alternation of every principal adjacency matrix forces

```text
nullity(A[S]) == |S| mod 2.
```

Weighting the four rows by `2^nullity` gives exactly

```text
sum_(|S|=6) 2^nullity(A[S])
  = 16459961595 + 32 n3.
```

The sole decreasing ordinary coefficient yields only

```text
n3 <= 470213205/3 = 156737735,
```

so it does not improve `4158`.

## Verified IAS and diagonal-toggle census

For `IAS(G)=[I|A|I+A]`, taking `phi` outside `S`, `chi` on `S\T`, and
`psi` on `T` reduces by the identity columns to

```text
A[S]+diag(1_T).
```

Consequently

```text
rank(transversal)
  = 99-|S|+rank(A[S]+diag(1_T)).
```

The verifier checked all `3^3=27` `phi/chi/psi` transversals of the `K3`
control, strengthening the discovery’s eight `phi/chi` checks.

It then independently evaluated all `62*64=3968` six-class diagonal
toggles.  Every split and aggregate coefficient matches the sealed
discovery output.  The strongest decreasing cell is again

```text
(|T|,nullity)=(3,5):
5072760-(2/3)n3 >= 0,
```

which gives only `n3<=7609140`.  Every cell remains strictly positive at
`n3=4158`, and the denominators introduce no congruence beyond the already
known `3|n3`.

## Interlace moment versus the Wave141 table

For fixed `S`, vectors in `ker A[S]` are exactly full vectors `x` such that

```text
supp(x) subset S,
supp(Ax) disjoint S.
```

Double counting gives

```text
sum_(|S|=t) 2^nullity(A[S])
 = sum_(x: supp(x) disjoint supp(Ax))
     binom(99-wt(x)-wt(Ax),t-wt(x)).
```

Wave141 records only

```text
B[i,j]=#{x:wt(x)=i,wt(Ax)=j}.
```

The `K3 disjoint_union K1` control is symmetric, idempotent, and even-rowed.
Its cell `B[2,2]=6` contains three vectors with support overlap `h=0` and
three with `h=2`.  All five small kernel-moment identities replay exactly.
Thus the summand in the displayed double count is not constant on a
`B[i,j]` fiber: the identity is not a direct coefficient row in `B` alone.

An additional exact control strengthens the general warning.  The two
six-vertex graphs with masks `5782` and `5872` have identical complete
`B[i,j]` tables but different size-three interlace rows:

```text
mask 5782: nullity-1 count 18, nullity-3 count 2
mask 5872: nullity-1 count 20, nullity-3 count 0.
```

Those two graphs are symmetric and zero-diagonal but do not satisfy the
target even-row/idempotent conditions.  Therefore they prove that general
graph interlace data are not determined by `B`, but they do not prove that
every target-specific elimination is impossible.  The correct target
status is:

```text
direct B-row projection: REFUTED
some different target-specific B-only consequence: UNKNOWN
```

## Veto: unsupported minimum-distance premise

The discovery’s top-band proof is mathematically correct conditional on

```text
d(im(A)) >= 14.
```

But the package’s frozen Wave131 input states

```text
frozen_binary_facts.image.minimum_weight_lower = 8.
```

The number `14` occurs only in the audit of a formal rational witness:

```text
rational_witness_audit.image_minimum_nonzero_weight = 14
rational_witness_audit.formal_integral_enumerator = false
rational_witness_audit.realized_binary_code = false.
```

An unrealized, nonintegral rational witness cannot supply a target premise.
No frozen input proves that image weights 8, 10, or 12 are absent.

Using the actually verified `d(im(A))>=8`, the complement argument applies
only for `|C|<8`.  It verifies

```text
rank(A[S])=54,
nullity(A[S])=|S|-54
```

for

```text
92 <= |S| <= 99.
```

The six additional rows with subset sizes 86 through 91 are
`VETO_UNSUPPORTED_PREMISE`.  If a separate proof of `d(im(A))>=14` is later
supplied, the discovery’s conditional argument would immediately validate
them.

## Final boundary

No verified inequality improves `n3<=4158`.  The interlace lift may still be
useful, but its formal rational and integral feasibility are unsolved.
Graph realizability, Conway-99, and novelty remain `UNKNOWN`.

## Reproduction

```powershell
python -B attempts\wave142-interlace-isotropic\exact_check.py --verify
python -B -m unittest discover `
  -s attempts\wave142-interlace-isotropic -p "test_*.py" -v
python -B verification\wave142-interlace-isotropic\independent_verify.py
python -B -m unittest discover `
  -s verification\wave142-interlace-isotropic -p "test_*.py" -v
```
