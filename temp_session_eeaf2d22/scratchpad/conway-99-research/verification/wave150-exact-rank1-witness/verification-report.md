# Wave150 independent exact-witness verification

Verdict: `PASS_WITH_SCOPE`.

The sealed Wave150 discovery manifest has SHA-256

```text
ae831ec52fbaf65b9ddc66dee77c4c076621d65a059ec3205e02a3b76bfafb1d
```

and all 30 entries pass their recorded hashes. The exact witness has SHA-256

```text
e63afbe9ca36b4b1571b3dde75309d0cce45f3bc862d6e8c08bfe62f78dc130d.
```

The verifier imports or executes no Wave150 or Wave147 discovery code.
Wave44 is rebuilt through its clean-room verifier. Wave148 is rebuilt through
the precommitted clean-room implementation that the preceding audit verified.
All Wave147 rooted coefficient matrices are regenerated directly from graph
masks and pointwise ordered-root flag counts.

## Exact witness

The witness is a nonnegative rational count vector at
`srg(99,14,1,2)` and `n3=4158`:

```text
order-seven support:                 204 / 208
order-seven total:                C(99,7) = 14,887,031,544
order-eight support:                 874 / 916
order-eight total:                C(99,8) = 171,200,862,756
integer positive x8 coordinates:     865
denominator-two coordinates:           5
denominator-four coordinates:          4
```

All records have unique known class masks, canonical rational syntax,
positive stored values, and denominator at most four. Zeros outside the
listed supports are restored explicitly before checking.

Independent downward deletion from `x7` gives nonnegative integral counts:

```text
order five: support 21 / 21, total C(99,5) = 71,523,144
order six: support 61 / 62, total C(99,6) = 1,120,529,256
```

## Independent equation reconstruction

The verifier reconstructs and replays:

- all 170 Wave44 rows, including their independently rebuilt coefficients
  and right sides, with `y=h11/4=2079`;
- all 208 ordinary order-seven-to-eight deletion rows;
- all 944 marked-vertex rows and 4,440 pointwise ordered-pair rows;
- the total order-eight count; and
- every upper-triangular entry in both centered covariance blocks.

For Wave147 it independently enumerates the 66 ordered-edge and 87
ordered-nonedge flag bases. It rebuilds all 2,414 class matrices over orders
five through eight and exactly matches all 272,054 stored nonzero
upper-triangular coefficients.

The raw combined system has 11,632 equations. Removing 893 identically zero
marked rows and 429 identically zero moment entries leaves exactly 10,310
nontrivial equations. Every one evaluates to the rational number zero. After
restricting to the 874 positive order-eight coordinates, 10,259 nontrivial
rows remain and all still pass.

## Centered covariance identity

For a fixed ordered-root family, let `c(theta)` be the vector counting
order-five rooted flags around the ordered root `theta`. Define

```text
s = sum_theta c(theta)
M = sum_theta c(theta)c(theta)^T.
```

The verifier reconstructs `s` from the order-five diagonal flag coefficients
and reconstructs `M` from all overlap orders five, six, seven, and eight. It
then checks every exact integer identity

```text
R*M[i,j] - s[i]*s[j] = 0.
```

The results are:

```text
ordered edges:     R=1,386, size 66, upper entries 2,211
ordered nonedges:  R=8,316, size 87, upper entries 3,828
maximum absolute centered residual: 0
```

The independent total controls also give

```text
sum(s) = R*C(97,3)
sum(M) = R*C(97,3)^2
```

in both families. Thus both covariance matrices are exactly zero, not merely
numerically close to zero.

## Modular support selection

Over the independently rebuilt 10,259 restricted rows, streaming elimination
over `F_1000003` reaches full column rank:

```text
variables:                  874
rank:                       874
rows scanned:             1,931
selected independent rows: 874
```

The independently selected row indices and semantic labels exactly match the
stored selection. Rechecking the stored 874-by-874 subsystem alone gives rank
874. Full rank modulo a prime also proves full column rank over the rationals.
The witness's embedded and standalone selection records agree in all
mathematical fields; only their recorded wall-clock durations differ.

## False-infeasibility chronology

The initial bound-encoded HiGHS record is retained with status `infeasible`.
The explicit-inequality run is retained with status `optimal`. The exact
nonnegative rational witness satisfies the stated exact system, so the first
status is conclusively false for that system. Neither floating solver status
is used as a certificate.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave150-exact-rank1-witness\independent_verify.py

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave150-exact-rank1-witness -p "test_*.py" -v
```

The full independent rebuild took about 79 seconds on this host. Ten focused
and hostile tests pass. Free physical memory was 33.2% after the full run,
above the verifier's 20% floor.

## Meaning and scope wall

The candidate is promoted to `VERIFIED` as an exact feasible point of the
specified finite relaxation. Consequently, this Wave44+Wave147+Wave148
order-eight, two-root centered model cannot exclude `n3=4158`.

The vector is not a graph. It does not enforce arbitrary higher-order overlap
compatibility among the counted subsets. It therefore neither constructs an
`srg(99,14,1,2)` nor proves that one exists. The global interval remains
`708 <= n3 <= 4158`; a strict upper bound, Conway-99, endpoint existence, and
external novelty remain `UNKNOWN`.
