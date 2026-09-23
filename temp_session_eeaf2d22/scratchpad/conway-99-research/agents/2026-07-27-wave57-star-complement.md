# Wave57 proof-A report: endpoint star complements

```yaml
role: proof_a
date_utc: 2026-07-27T20:50:44Z
git_commit: a4a61658356253fb95cf68252c972a4f79df38fe
claim_label: DERIVED
scope: conditional n3=4158 endpoint, arbitrary fixed triangle, no automorphism
inputs:
  - attempts/wave35-n3-4158-combinatorial/exact-results.json
    sha256 07e1469e7690bd630385e734d387fa13a1eb537f0c578bf31270c3b7b8824b67
  - attempts/wave35-n3-upper-spectral/exact-results.json
    sha256 ca1df07bede11642fb1639a2ae554c1a31ce9a58424d5b3e5031c90ad550a194
  - verification/wave35-n3-upper-spectral/independent-results.json
    sha256 c704d8fce8f1d5975204b9a06ada0098c66fbdb9e0de8016a1ff89d86e691305
  - verification/wave35-n3-upper-spectral/audit.md
    sha256 5300d965a23846e2549196e9a5c207047ee268579f60e5d3c5133c092d1a287b
method: exact projector algebra, supported sectors, moment localizers,
  algebraic-integer controls, and star-complement rank reduction
command: Set-Location attempts/wave57-star-complement; python exact_check.py;
  python -m unittest -v test_exact_check.py; python -m py_compile
  exact_check.py test_exact_check.py
outputs:
  - attempts/wave57-star-complement/exact-results.json
    sha256 2b49b0bf3d52c0101cfcd59c3324279c1f153f4d48504c7ae67658e8786e6216
  - attempts/wave57-star-complement/derivation.md
    sha256 bb0fef9897088f929b70d99f2f90df118f3093a13337f9521f44bce2b49a8aa4
  - attempts/wave57-star-complement/run-report.yaml
    sha256 2bf30c78c09dc05577440b810db48e162bceaaf98c7fd964aab6b0647f1bc622
limitations: discovery cannot certify itself; scalar controls are not certified
  graph spectra; no binary reconstruction matrix, graph, exhaustive search, or
  contradiction is supplied
```

## Result

The fixed-triangle partition has quotient

```
[2 12  0
 1  3 10
 0  6  8]
```

with eigenvalues `14,3,-4`.  For each of `3` and `-4`, the sum-zero plane
on the three 12-vertex fibres gives a two-dimensional full-graph eigenspace
supported on `U=T union X`.

The exact projectors

```
E_3  = ( A+4I-(2/11)J)/7,
E_-4 = (-A+3I+(1/9)J)/7
```

then give

```
dim E_3 supported on U  = mult_Y(-4)-6,
dim E_-4 supported on U = mult_Y(3)-16.
```

Hence `mult_Y(-4)>=8` and `mult_Y(3)>=18`.  Compact-interval localizers
using the 32 triangles in `Y` sharpen these to

```
18 <= mult_Y(3) <= 20,
 8 <= mult_Y(-4) <= 13.
```

All 18 pairs survive.  The fourth moment is controlled by `c=C4(X)`:

```
C4(Y)=171+c,
tr(A_Y^4)=8568+8c,
0<=c<=89.
```

The per-pair lower bounds range from 0 to 65 and are recorded exactly in
`exact-results.json`.

## Star-set consequence

The maximum number of independent `3`-projector columns available in `Y`
is `60-mult_Y(-4)`.  Therefore a `3`-star set hits `U` in at least
`mult_Y(-4)-6`, and this bound is attained by extending a maximum independent
subset.  Similarly, a `-4`-star set hits `U` in exactly the minimum
`mult_Y(3)-16`.  The respective ranges are 2-to-7 and 2-to-4.

This rules out a star set wholly inside `Y`; it does not provide a canonical
choice inside `U`.

## Feasibility controls

Sixteen multiplicity pairs have exact residual controls supported on the
integer roots `-3,-2,-1,0,1,2`.  The other two have conjugate algebraic-integer
controls:

- `(20,8)` uses four copies of the roots of `x^2+4x+1` and has `C4(X)=45`;
- `(20,9)` uses four copies of the roots of `x^2+5x+5` and has `C4(X)=50`.

All power sums through degree four and all Newton divisibilities check exactly.
These are scalar failure-of-obstruction witnesses, not certified graph spectra.

## Smaller exact target

The next finite target is a 60-vertex, 8-regular graph `A_Y` with 32 triangles,
a ledger-compatible four-cycle count, and

```
rank(11A_Y+44I-2J) = 60-mult_Y(-4) in [47,52],
rank(-9A_Y+27I+J)  = 60-mult_Y(3) in [39,42].
```

One can then choose a `3`-star complement of order 40-to-42 or a `-4`-star
complement of order 47-to-52 inside `Y` and impose the exact binary
Reconstruction Theorem.  This is smaller than the original 99-vertex search,
but it has not been exhausted.

## Source boundary

The star-basis definition comes from Cvetkovic, Rowlinson, and Simic,
"A study of eigenspaces of graphs," *Linear Algebra and its Applications*
182 (1993), DOI `10.1016/0024-3795(93)90491-6`.  The primary
star-complement characterization source used is their 1999 article,
DOI `10.1016/S0024-3795(99)00179-2`.  The Cambridge chapter
DOI `10.1017/CBO9780511801518.006` supplies an authoritative modern
statement.

## Status

`DERIVED_INCONCLUSIVE`.  Eight tests pass, the checker and tests compile,
and the post-QA memory measurement was 51.49 percent free physical memory.
This proof agent does not promote its own result to `VERIFIED`.  The endpoint
is not excluded, no graph is constructed, and Conway-99 remains `UNKNOWN`.
