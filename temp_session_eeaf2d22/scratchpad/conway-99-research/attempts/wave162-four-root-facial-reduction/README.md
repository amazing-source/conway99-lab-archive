# Wave162: exact four-root facial-reduction audit

Status: `DERIVED` negative/null result from a discovery lane. It is not
independently `VERIFIED`.

## Result

No unconditional forced face of the root-3 or root-12 covariance cone is
supported by the accessible exact data.

Wave162 replayed all fifteen stored scalar covariance cuts on all six stored
exact fixed-slice pseudowitnesses. The three cuts that are zero at the
Wave159 fifteen-cut witness are:

| root | cut hash prefix | exact comparison witness | comparison value |
|---:|---|---|---:|
| 12 | `68a099dd` | eight-cut | `387341807777838263670298632558020140512814872 / 42943811696010075252336217` |
| 12 | `8fc95276` | two-cut | `-236563073663757900784408124760 / 1142494463827` |
| 3 | `93c3dceb` | two-cut | `-376016787882791250547671775500 / 1142494463827` |

All six witnesses have the same exact order-seven vector and freeze the same
three core affine inputs. Their stored exact-solve records say the relevant
base rows replay. Therefore each displayed nonzero difference is a direct
primal certificate that the corresponding scalar functional is **not**
identically zero on the common stored affine slice. In linear-algebra terms,
the cut row is not a consequence of the common affine equality rows.

The older root-12 direction `68a099dd` looks persistent: its quadratic value
is zero at five of the six witnesses. The eight-cut witness's exact positive
value above disproves universal activeness. No retained direction is zero at
all six witnesses.

## Conditional face, not a discovered face

For a positive-semidefinite matrix `B`,

```text
v^T B v = 0  implies  B v = 0.
```

Consequently, **if** a genuine PSD-feasible solution were separately proved
to make all three Wave159 cuts active, their exact independent directions
would give:

```text
root 3:   S_+^155  ->  S_+^154
root 12:  S_+^178  ->  S_+^176
```

The exact determinant minors proving the direction ranks are:

```text
root 3 active rank 1:  determinant -48251 at flag index [0]
root 12 active rank 2: determinant 2575230448 at flag indices [0,1]
```

This reduction is both conditional and shallow: only one of 155 root-3
directions and two of 178 root-12 directions are removed.

The stored objects do not meet the PSD premise. Every evaluated
pseudowitness has an exact negative four-root direction. In particular, at
the fifteen-cut witness the newest negative direction is outside the span of
the active directions:

```text
root 3:  combined rank 2, determinant -54011205 at indices [0,3]
root 12: combined rank 3, determinant 3152254737888 at indices [0,1,2]
```

Thus the newest violations are not repetitions within the proposed
conditional face.

## Why zero is not yet a kernel

Each cut has the form

```text
L_v(x) = v^T B_tau(x) v >= 0,
```

where `B_tau(x)` is affine in the induced-count vector `x`. The implication
from `L_v(x)=0` to `B_tau(x)v=0` uses `B_tau(x) >= 0`. The exact
pseudowitness matrices are indefinite, so a zero scalar quadratic value at
one of them cannot be promoted to a null vector. Moreover, Wave159 explicitly
added its selected active cuts as equality rows during rational
reconstruction. Their exact zero values are therefore by construction, not
an independently recovered dual certificate.

## What a real facial reduction now requires

The next useful object is an exact conic-dual exposing certificate. In
schematic form, seek positive-semidefinite multiplier matrices `Z_tau` and
affine-row multipliers `lambda` such that

```text
sum_tau <Z_tau, B_tau(x)> + lambda^T(Ax-b) = 0
```

identically in `x`, with every surviving term nonnegative on the feasible
set. Then every feasible solution must have

```text
<Z_tau, B_tau(x)> = 0,
```

which forces the range of `Z_tau` into the kernel of `B_tau(x)` and exposes
a genuine face. A strict negative constant in the corresponding dual
identity would instead be an infeasibility certificate.

More sampled eigenvector cuts do not produce this identity. The next search
should optimize directly for a low-rank rational `Z_tau`, coupled across the
root-3 and root-12 blocks and the full deletion/marked affine system, then
recover and replay the dual identity exactly.

## Reproduction

The audit is lightweight and runs no optimizer:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B `
  attempts\wave162-four-root-facial-reduction\analyze_facial_reduction.py
.\.venv\Scripts\python.exe -B -m unittest `
  attempts\wave162-four-root-facial-reduction\test_wave162.py -v
```

The final run sampled at least `17.48%` free physical memory and never used a
heavy solve.

## Evidence boundary

- Wave162 is a same-project discovery audit, not an independent verifier.
- It independently replays the cut values but relies on the exact base-row
  replay counts frozen in the witness files instead of rebuilding all base
  rows.
- Count pseudowitnesses are not graphs.
- The conditional cone reductions are implications, not demonstrated faces
  of the unrestricted feasible set.
- Endpoint feasibility at `n3=4158`, a strict bound below `4158`, and
  Conway-99 remain `UNKNOWN`.
