# Wave 20 retained failed runs

These failures occurred during the independent `n3=63` discovery lane.  They
are retained because neither a timeout nor a partial program output is
mathematical evidence.

## 1. REJECTED two-profile census

After the naive product timed out, an exploratory recursive generator printed
only

```text
r=14, q=3^14
r=21, q=2^21.
```

That census was **wrong**.  Its recursion replaced the global maximum part by
`min(maximum,total//remaining_parts)` and then passed that temporary average
bound into every deeper call.  This silently forced later parts to remain
below an early average and discarded valid nonconstant partitions.

The discovery lane initially announced the two-profile result to the
orchestrator.  The first deterministic checker rejected it immediately by
finding the complete 18-profile census.  The announcement was withdrawn
before it was used as a published premise.

Status: **REJECTED / FALSE INTERMEDIATE CLAIM / NO EVIDENCE**.

Repair: the final fixed-length generator keeps the true global
`d_K>=4` maximum unchanged and uses `total//remaining_parts` only as the
current loop bound.  The exact expected 18 rows and counts

```text
r=14,15,16,17,18,19,20,21: 1,1,1,5,4,3,2,1
```

are hard-coded in the checker and tests.  Every newly restored `r=18,19,20`
case receives its own contradiction; none is inferred from the rejected
census.

## 2. Naive `q`-profile product

The first exploratory command iterated
`combinations_with_replacement(range(2,43),r)` separately for every
`1<=r<=21`.  It timed out after about 14 seconds before returning a complete
profile list.

Status: **FAILED / NO EVIDENCE**.

Repair: replace the product by a nondecreasing fixed-length partition
generator with the a priori bound

```text
q <= floor((r-5)/3)
```

coming directly from `d_K>=4`.  The final checker uses that bounded
enumeration and tests that weakening the bound changes the census.

## 3. Vertex-by-vertex outside-degree dynamic program

An exploratory program attempted to decide every outside first/second moment
pair by carrying all `(sum, square_sum)` states through `99-m` vertices.
It timed out after about 124 seconds without completing the five values of
`m`.

Status: **FAILED / NO EVIDENCE**.

Repair: use the exact convex integer bound.  If `N` nonnegative integers have
sum `S`, write `S=aN+r`; their square sum is at least

```text
(N-r)a^2+r(a+1)^2.
```

The bounded maximum is obtained by packing entries of 14.  These are
mathematical necessary conditions, require no search over outside vertices,
and are independently unit-tested at the equality values used in the proof.

## 4. Unbounded grouped degree-distribution recursion

A second exploratory script generated all count distributions over degrees
`6,...,14` before applying the small spectral slack.  It timed out after
about 34 seconds and emitted no complete census.

Status: **FAILED / NO EVIDENCE**.

Repair: first compute the local minimum degree sum and the exact spectral
slack, which is at most 12 in the relevant cases.  The final checker
enumerates only integer partitions of that slack and then reconstructs the
degree histograms.

## Boundary

No solver status, timeout, incomplete enumeration, floating-point
eigenvalue, or Wave 19 artifact is used in the final conditional exclusion.
