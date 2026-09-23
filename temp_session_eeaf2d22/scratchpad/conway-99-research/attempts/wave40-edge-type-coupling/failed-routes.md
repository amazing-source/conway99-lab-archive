# Retained failed routes

All statements below are conditional on the prism-free endpoint
`n3=4158`. None is evidence that the endpoint exists.

## Euler-characteristic contradiction

The Wave 39 edge cycles do glue into a closed two-dimensional incidence
complex after splitting triangle-vertices with disconnected links. If
`(a,b,c,d)` count types `(222,24,33,6)` and `H` is the total number of
triangle-link components, then

```text
chi = H-4158+(3a+2b+2c+d).
```

For all-`222`, this becomes `chi=H-2079`, in the interval
`[-1848,-693]`. Negative Euler characteristic is normal for high-genus
surfaces. Orientability was not proved and must not be assumed. Therefore
this exact topological packaging is not a contradiction.

## Edge-type totals alone

The linear face identities

```text
F4=3a+b, F6=2c, F8=b, F12=d
```

exhaust the information obtained solely from boundary lengths. Their
weighted sum is the tautological dart count `8316`. No nonnegative linear
combination of these equalities forces `a<693`.

## One-triangle exclusion of all-`222`

The exhaustive normalized quotient census does not exclude three `222`
sides. Its minimum `rank_F3(P_T-I)` is eleven, attained by eight normalized
labelled forms. An explicit 36-vertex lift is cubic, triangle-free, respects
the audited local codegree caps, and has the required `4+8` component
profile. This refutes any contradiction using only:

- the three pairwise cycle types;
- the quotient rank ceiling at `r3=12`;
- cubicity and triangle-freeness of the one-triangle neighbor core;
- the local codegree caps; or
- nonnegativity and rational rank of the required `B B^T`.

A successful continuation must couple the `2+4` selections across different
base triangles or use a full simultaneous `B/H` completion.

## Treating the quotient as the full 39-vertex block

The quotient `P_T` contracts eighteen matching edges, but it does not record
which two incident quotient edges at a contracted vertex use the same
original endpoint. There is one invariant binary choice at each of the
eighteen quotient vertices. Different choices for the same `P_T` can give
different ranks to

```text
(J-I-2A)[T union N(T)].
```

For one rank-11 all-`222` quotient, the complete `2^18` census realizes
39-block ranks 33, 34, and 35 among triangle-free lifts. Consequently the
4,050 quotient census cannot by itself support a universal 39-block rank
claim. The correct exact reduction is

```text
rank_F7(K_39)=1+rank_F7(3I-A_X).
```

The remaining task is a Laplacian-rank bound across every admissible
36-vertex core, not another quotient-only elimination.

## Sign and parity shortcuts

The parity of the number of edge-local components distinguishes
`222,6` from `24,33`, but no global cancellation identity was derived.
Promoting the surface to an orientable one would impose extra parity
conditions, but orientability is not a consequence currently in hand.

## Boundary

```text
all edges type 222:          survives
joint r3=12/all-222 boundary: survives one-triangle controls
n3=4158:                     UNKNOWN
general upper bound:         n3<=4158
Conway-99:                    UNKNOWN
```
