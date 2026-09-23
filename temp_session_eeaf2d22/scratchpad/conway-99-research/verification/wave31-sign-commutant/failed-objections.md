# Wave 31 sign-commutant objections and hostile controls

No blocking objection survived.  This ledger records the attempted attacks,
their disposition, and concrete countermodels when a premise is weakened.
It is not a claim that the Conway graph exists or does not exist.

## Resolved objections

### `W31-SC-001`: the incidence map could have a kernel on `im(E)`

**Disposition: resolved.**  For `u in im(E)=ker(Gamma)`,

```text
||Nu||^2=u^T(3I+Gamma)u=3||u||^2.
```

The scale is positive, so `N` is injective there.  Both `im(E)` and the
adjacency `-4` eigenspace have dimension 44, making the transport onto.

### `W31-SC-002`: a lattice basis change could destroy row integrality

**Disposition: resolved.**  An integral orthogonal decomposition is reached
by a unimodular basis change.  If the basis change is `U`, the frame
coordinates change by `U^(-T)`, which is again integral.  Each component norm
is the norm of a lattice vector.  Rootlessness, meaning minimum at least four
here, makes every nonzero component norm at least four, so a norm-four row
has exactly one nonzero component.  The endpoint form is also even, but
evenness is not needed for this implication.

### `W31-SC-003`: block support might not imply a coordinate projector block

**Disposition: resolved.**  Rows supported in distinct orthogonal lattice
blocks have zero `S`-inner product.  Hence `M=XSX^T` is coordinate-block
diagonal after a row permutation, as is `E=M/21`.  The diagonal sign matrix
that is constant on each side of one row block therefore satisfies `DE=ED`.

### `W31-SC-004`: preservation of the `-4` space might not imply commutation

**Disposition: resolved with an active hypothesis.**  The transported matrix
`K=NDN^T` is symmetric.  Once it preserves `V`, symmetry also preserves
`V^perp`, so it commutes with the orthogonal projector onto `V`.  The
independent checker retains the nonsymmetric countermodel

```text
P=diag(1,0),  K=[[1,1],[0,2]].
```

Here `K` preserves `im(P)` but does not commute with `P`.

### `W31-SC-005`: the projector or commutator coefficient could have a sign error

**Disposition: resolved.**  Solving on the three adjacency eigenspaces gives

```text
P_-4=(27I-9A+J)/63.
```

The equation `KP=PK` expands exactly to

```text
9(KA-AK)=KJ-JK.
```

Since `K1=3d` and `K` is symmetric, division by three gives

```text
3(KA-AK)=d1^T-1d^T.
```

The independent checker also verifies the sign with generic exact matrices,
not by copying a string comparison.

### `W31-SC-006`: omitted summands could invalidate the adjacent cancellation

**Disposition: resolved.**  For adjacent `x,y`, the 99 summation indices
split into `x`, `y`, the unique common neighbor `z`, twelve neighbors only
of `x`, twelve neighbors only of `y`, and 72 remaining vertices.  Every
summand vanishes except the `z` term on each side:

```text
(ZA)_xy=Z_xz=s_T,
(AZ)_xy=Z_zy=s_T.
```

The two signs are equal because both edges lie in the same unique graph
triangle `xyz`.

### `W31-SC-007`: edgewise constancy might not become global constancy

**Disposition: resolved.**  Every nonadjacent pair in the target has
`mu=2` common neighbors and therefore a path of length two.  The graph is
connected without an automorphism or construction assumption.

### `W31-SC-008`: the signed-incidence double count could have a factor error

**Disposition: resolved.**  If `b` of 231 triangle signs are positive and
the constant signed degree is `d`, counting signed vertex-triangle
incidences on the two sides gives

```text
99d=3(2b-231),
33d=2b-231.
```

As `231=7*33` and `2` is invertible modulo 33, this gives `33|b`.

### `W31-SC-009`: the block trace might not exclude all proper ranks

**Disposition: resolved, with a valid shorter strengthening.**  The
submitted tight-frame identity

```text
4b=21r
```

is valid and enumerates exactly `r=4,8,...,40`, with row counts
`21,42,...,210`; none is divisible by 33.

There is also a shorter consequence that adds no premise.  Once `E` is
coordinate-block diagonal, its selected principal block `E_I` is itself an
orthogonal projector.  Since every diagonal entry of `E` is `4/21`,

```text
rank(E_I)=tr(E_I)=4b/21.
```

The left side is integral, so `21|b`.  Together with `33|b`, this gives
`231|b`, impossible for a nonempty proper coordinate block.  This
strengthens the presentation; it does not repair a defective submitted step.

### `W31-SC-010`: the conclusion might escape its hypotheses

**Disposition: resolved by a strict scope wall.**  The verified conclusion
excludes only rootless, integrally orthogonally decomposable endpoint
`S`-forms carrying the actual target graph incidence/projector semantics.
It does not exclude rooted forms, rootless indecomposable forms, rational
splits, bare lattices, or abstract `X/M/S/Q/B` packages without `N,A,Gamma`.

## Active hostile mutations

| Removed or mutated premise | Exact control | What fails |
|---|---|---|
| Rootlessness | component norms `2+2=4` | A frame row can meet two blocks, so `E` need not split. |
| Nonzero-component norm floor | component values `1+3=4` | If block components are not protected as lattice vectors by the minimum-four floor, the support argument fails. This also controls dropping integrality/evenness together, but not evenness alone. |
| Evenness alone | no countermodel | No failure: minimum at least four still forces one-block support. |
| `DE=ED` | `E=(1/2)[[1,1],[1,1]]`, `D=diag(1,-1)` | `D` does not preserve `im(E)`. |
| Symmetry of `K` | `P=diag(1,0)`, `K=[[1,1],[0,2]]` | Preservation of `V` does not imply projector commutation. |
| One shared triangle sign | set `Z_xz=1`, `Z_zy=-1` | `(ZA-AZ)_xy=2`, and the equation permits `d_x-d_y=-3`. |
| Connectedness | use more than one connected component | Edgewise constancy need not use one global value. |
| Actual incidence transport | retain only abstract endpoint matrices | There is no justified map from `im(E)` to the graph `-4` space. |
| Proper-block condition | take `b=0` or `b=231` | Both trivial coordinate signs satisfy the divisibility arithmetic. |

## Non-objections retained as limitations

- The argument constructs no graph, projector, frame, lattice, or endpoint.
- A multiple of 33 is a necessary count, not a construction certificate.
- The superseded rank-24 tensor profile is not used in this verdict.
- `n3=708`, Conway-99, and novelty remain `UNKNOWN`.

## Verifier QA wording correction

Before the verifier package was frozen, QA found that the original hostile
label attached `[1,3]` to deleting "even integral component norms."  That
label did not isolate evenness: retaining minimum at least four already
forbids both components, regardless of parity.

The checker, tests, audit, and run report now use `[1,3]` only as a control
for dropping the nonzero-component norm floor (which may happen when the
integral lattice-component interpretation and evenness are dropped
together).  Evenness is recorded as an inherited endpoint hypothesis that
is logically unnecessary for this support step.  This is verifier QA wording
correction only; no candidate artifact, theorem, verdict, or status changed.

## Verifier harness failures

One replay invocation from the verifier directory used

```text
python -B -m unittest -v ../../attempts/wave31-survivor-proof/test_exact_check.py
```

`unittest` treated the filesystem path as an invalid dotted module name,
raised `ValueError: Empty module name`, and ran zero tests.  During QA, a
second invocation from that same wrong directory used the bare module name,
raised `ModuleNotFoundError`, and also ran zero substantive tests.  Both
were harness-only failures.  Running the frozen command from
`attempts/wave31-survivor-proof` corrected the invocation and passed all 15
tests.

A proposed single-command clean-archive wrapper was rejected by the host
execution policy before it ran.  It created no archive or filesystem
change.  Frozen-commit identity was instead established by exact SHA-256
freezes plus `git diff --quiet` on every candidate path.
