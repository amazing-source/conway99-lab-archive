# Exact projector and rooted three-point derivation

Claim labels: `DERIVED` for the necessary conditions,
`REFUTED_AS_A_REALIZATION` for the declared support families,
`REFUTED_AS_A_RELAXATION` for code-only three-point caps, and `UNKNOWN`
for the actual local cap.

## 1. The span-projector necessity

For a hypothetical target graph,

```text
E = (27I-9A+J)/63
```

is the orthogonal projector onto its 44-dimensional `-4` eigenspace.  Its
entries are

```text
E_uu = 4/9,
E_uv = -8/63  if u~v,
E_uv =  1/63  if u is not adjacent to v.
```

Let the full-column-rank matrix `T` have actual integer `-4` eigenvectors
as its columns.  Then

```text
W = T(T^T T)^-1T^T
```

is the orthogonal projector onto `span(T)`.  Since `span(T)` is contained
in `image(E)`, the difference `E-W` is also an orthogonal projector and in
particular

```text
E-W is positive semidefinite.                         (1)
```

The one-coordinate principal minors of (1) give the graph-independent
leverage condition

```text
W_uu <= 4/9.                                          (2)
```

For each coordinate pair, the two-by-two principal minor further requires

```text
(E_uv-W_uv)^2
  <= (4/9-W_uu)(4/9-W_vv),                            (3)
```

for at least one of the only two permitted off-diagonal values
`E_uv in {1/63,-8/63}`.  This is still only a necessary local completion
test; it does not enforce degrees, `lambda`, `mu`, or global PSD
simultaneously.

## 2. Exact leverage results

The Wave120 records embed into all 99 coordinates as follows:

- four alternating cycle anchors;
- four unused type-11 cross-edge witnesses;
- the six disjoint pools of sizes `10,10,25,10,10,26`.

Every record has norm 16.  Exact Gauss-Jordan inversion of `T^T T` gives:

| family | rank | coordinates violating (2) | maximum leverage |
|---|---:|---:|---:|
| all forty Wave120 records | 40 | 46 | `0.670912...` |
| first 26 records | 26 | 6 | `0.527998...` |
| explicit candidate 26 | 26 | 0 | `0.443656...` |

The first two coordinate realizations are therefore impossible in one
target eigenspace.  This does not alter the abstract residual Gram from
Wave120 because that Gram did not claim to preserve the displayed integer
coordinates.

The explicit candidate's maximum is exactly

```text
1217462828759965373070564
----------------------------------------------- < 4/9.
2744155911807689338327015
```

It is a valid null control for (2).  It fails (3) on exactly 352 coordinate
pairs, so it is not a common eigenspace family.

## 3. Product-Johnson three-point variables

After the four fixed anchors, each record selects two coordinates from
each of six blocks.  Thus the support code lies in

```text
J(10,2) x J(10,2) x J(25,2)
        x J(10,2) x J(10,2) x J(26,2).
```

Fix a root record `a`.  In block `b`, define

```text
i_b(a,x) = |a_b intersect x_b|,
t_b(a;x,y) = |a_b intersect x_b intersect y_b|,
u_b(a;x,y) = |(x_b intersect y_b) minus a_b|.
```

The centered endpoint-one stabilizer blocks have entries

```text
K_in(x,y)  = t_b - i_b(a,x)i_b(a,y)/2,
K_out(x,y) = u_b
             - (2-i_b(a,x))(2-i_b(a,y))/(v_b-2).      (4)
```

Each matrix in (4) is exactly a Gram matrix of centered coordinate
incidence vectors on the root-selected or root-unselected cell.  Hence it
is PSD with a displayed rational factorization, not a floating eigenvalue
test.

The checker also builds degree-two feature Grams:

- three within-block blocks according to whether a selected coordinate
  pair meets the root in 0, 1, or 2 points;
- four cross-block blocks for every pair of blocks, according to whether
  each selected coordinate lies inside or outside the root.

Across all 26 roots this gives

```text
312 centered endpoint-one blocks,
468 within-block degree-two blocks,
1,560 cross-block degree-two blocks,
2,340 exact PSD blocks total.
```

These constraints contain genuine triple information.  For example,
records `(0,3,6)` and `(0,6,39)` both have sorted pair-overlap tuple
`(1,1,4)`, but their total three-way intersections are respectively zero
and one.  Overall, 28 of the 52 pair-overlap tuples realized by the
candidate split into multiple triple-intersection values.  Ordinary
pair-distance data cannot reconstruct these rows.

Every `x+y+z` and one-minus signed triple row in the candidate has squared
norm at least 22.  Thus the verified lattice minimum and the known
classifications through norm 20 do not reject it.

## 4. What this establishes

The records are an actual product-Johnson constant-weight code, so any
valid relaxation using only that code geometry—including a full
code-only Schrijver/Terwilliger necessary condition—must admit the code.
The explicit factor census makes a nontrivial rooted third-order part of
that statement reproducible.

The graph-valued projector entries in (3) kill the displayed candidate.
This isolates the next useful space: a completion must retain the discrete
edge/nonedge values and one common outside adjacency, rather than only
support-code intersections.

No exhaustive search of 26-subsets or graph-valued completions was made.
The local caps 25 and 24 and Conway-99 remain `UNKNOWN`.
