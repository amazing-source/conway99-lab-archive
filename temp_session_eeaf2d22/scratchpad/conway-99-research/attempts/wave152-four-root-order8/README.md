# Wave 152: four-root order-eight covariance

Status: **verified finite separations and nine-cut survivor; endpoint unknown**.

This lane strengthens the order-eight flag relaxation without introducing
order-nine graph classes. Fix four pointwise-labeled root vertices and add an
unordered pair of free vertices to form an order-six flag. The product of two
such flags has union order 6, 7, or 8. Therefore every resulting covariance
matrix is determined by the endpoint counts already used in Waves 147--150.

## Verified result

The exact Wave150 count vector is feasible for all frozen Wave44 aggregate
rows, Wave148 marked rows, ordinary order-7-to-8 deletion, and both centered
pair-root covariance blocks. It is nevertheless impossible in the stronger
four-root relaxation.

Two of the nine locally admissible four-root types have independently
verified negative integer directions in

```text
B_tau = 4 * (R_tau M_tau - s_tau s_tau^T).
```

Here `R_tau` is the number of ordered embeddings of the labeled root type,
`s_tau` is its flag first-moment vector, and `M_tau` is its raw flag Gram
matrix.

```text
root mask 3   (two incident edges plus an isolated root):
  flag dimension: 155
  direction support: 24
  exact quadratic value: -2293145527521819747490560

root mask 12  (two disjoint root edges):
  flag dimension: 178
  direction support: 88
  exact quadratic value: -8605517548253993047296
```

The clean-room verifier independently rebuilt the nine flag universes and all
order-6/7/8 products without importing or executing the discovery code. Its
scoped verdict is that both blocks are `VERIFIED_NOT_PSD`; hence the Wave150
pseudowitness is refuted.

This is not an endpoint contradiction. A pseudodistribution can move after a
separating inequality is added.

## First feedback step

`build_exact_cuts.py` converts the two negative directions into primitive
exact linear inequalities in the order-seven and order-eight induced counts.
The stored Wave150 vector violates both.

A numerical HiGHS feedback solve on the old pair-root zero-covariance face and
the `h11=16632` endpoint slice found another point satisfying both cuts. The
point was then reconstructed exactly:

```text
order-7 support:                   204 / 208
order-8 support:                   885 / 916
exact rows passed:                 10311
active root-mask-12 cut value:     0
root-mask-3 cut value:             positive
maximum order-8 denominator:       139384324586894
```

This second object is an exact rational pseudowitness, not a graph. Its large
denominators are permitted by the relaxation but impossible for actual
induced-subgraph counts. The next cutting-plane step evaluates all nine
four-root blocks on this replacement vector and adds newly violated
directions.

The second evaluation again separated masks 3 and 12. After those directions
were added, a third exact pseudowitness survived four cuts:

```text
order-8 support:                   886 / 916
exact rows passed:                 10312
two active cut values:             0, 0
maximum order-8 denominator:       170404771984456964442574301594
```

Evaluating that vector exposed a new non-PSD root type, mask 13 (an induced
four-vertex path). Its violation already appears in a two-by-two principal
submatrix, producing a sparse primitive cut with only four order-seven and
28 order-eight coefficients. After adding that fifth cut, another exact
rational vector survives with the same `204/886` supports and 10,312 exact
rows. Thus five directions still do not close the face, but the separation
has spread from masks 3 and 12 to a third root geometry.

Bundling the next three negative directions gives an eight-cut exact
pseudowitness with support `204/886`, 10,312 exact rows, and two new active
equalities. A ninth, manually simplified mask-12 direction is also satisfied
strictly by that same exact vector. Wave156 independently rebuilt these late
directions and replayed the five- and eight-cut witnesses. It therefore
verifies exact feasibility of this retained nine-cut finite relaxation.

The simplified direction is especially transparent. The relevant mask-12
principal submatrix has equal diagonal entries and a larger off-diagonal
entry, so the integer direction is simply `(1,-1)` on flag masks 5428 and
6324. After primitive normalization its exact endpoint inequality is

```text
320166
+ x7[7864]
+ 6*x8[2022000]
- x8[5691760]
- x8[14332512]
+ x8[15434592]
- 2*x8[23804464]
+ 2*x8[51173472]
- x8[51205216]
- x8[127242964]
- x8[144594160] >= 0.
```

The bracketed integers are canonical graph-mask identifiers, not numerical
weights. Wave156 independently reconstructed this inequality and its positive
value on the eight-cut witness; it does not by itself exclude the endpoint.

A later equal-diagonal mask-12 minor simplifies much further:

```text
18711 + 6*x8[2022000] - 2*x8[5683824] >= 0.
```

Exact canonical-isomorphism checks identify mask `2022000` as the 3-cube
`Q3` and mask `5683824` as the 8-vertex Wagner graph (the Möbius ladder).
Wave156 independently reconstructs the sparse endpoint cut and verifies that
it exactly separates the eight-cut witness. Since induced counts are
integers, the endpoint inequality is equivalently

```text
number of induced Wagner graphs
    <= 3 * number of induced 3-cubes + 9355.
```

The order-six term behind the constant is class mask `1884`, whose general
strongly-regular count is `41580-n3`. The same covariance calculation
therefore suggests the all-`n3` inequality

```text
4 * number of induced Wagner graphs
    <= 41580 - n3 + 12 * number of induced 3-cubes.       (candidate)
```

This symbolic lift is a Wave157 discovery claim until a separate verifier
checks it. It is the cleanest human-readable output of the current loop, but
it still does not give a strict bound without an independent lower bound on
Wagner graphs relative to cubes. External novelty is also `UNKNOWN`.

Adding this sparse cut and the three next covariance directions still leaves
a numerical point. Exact reconstruction produces a thirteen-cut rational
pseudowitness with order-7/8 supports `204/887`, 10,313 exact retained rows,
modular rank `887/887`, and three active scalar cuts. It satisfies all
thirteen inequalities exactly. This newest survivor is a discovery result
outside the Wave156 freeze, not yet an independently verified claim. Evaluating
all nine covariance blocks again gives fresh exact negative directions for
root masks 3 and 12, so this survivor is not a graph-compatible moment
sequence either; those directions seed the next iteration.

## Why this space is useful

The pair-root matrices remember how triples overlap around an ordered pair.
The new matrices instead remember how vertex pairs overlap around four fixed
vertices. This retains simultaneous information about six root-to-free
incidences and the edge between the two free vertices. It is therefore able
to detect compatibility failures invisible to every pair-root block, while
still closing at order eight.

## Boundary

The verified claim is exactly:

> The stored Wave150 exact rational count vector cannot be the induced-count
> vector of a graph because it violates two valid four-root covariance
> inequalities.

It does **not** prove:

- that every endpoint count vector violates a four-root block;
- that the full four-root SDP is infeasible;
- that `n3<4158`;
- that `srg(99,14,1,2)` exists or does not exist.

Conway-99 and every strict general upper bound below 4158 remain `UNKNOWN`.

## Reproduce

Use the repository virtual environment:

```powershell
.\.venv\Scripts\python.exe `
  attempts\wave152-four-root-order8\four_root_scout.py

.\.venv\Scripts\python.exe `
  attempts\wave152-four-root-order8\build_exact_cuts.py

.\.venv\Scripts\python.exe `
  attempts\wave152-four-root-order8\cut_feasibility_scout.py `
  --mode zero --solver HIGHS --time-limit 120 `
  --output attempts\wave152-four-root-order8\zero-face-two-cuts-highs.json

.\.venv\Scripts\python.exe `
  attempts\wave152-four-root-order8\reconstruct_cut_witness.py
```
