# Independent verification of Wave143

Verdict: `PASS_WITH_SCOPE_CORRECTION`.

The final discovery manifest was frozen before inspection at SHA-256
`91e1053b886f05d8457bb14a5acaf87c02afe73ad087e98203cc779012571a61`.
All 20 entries and all six frozen prerequisite files reproduce their stated
hashes.

The exact computations in the sealed package pass.  The correction is about
premises and scope: the target arguments currently establish only

```text
d(im A) >= 8,  d(ker A) >= 8.
```

The rational Wave143 witnesses instead live in the stronger formal slice

```text
d(image) >= 14,  d(dual) >= 15,
```

including `D_1=...=D_14=0`.  Those stronger null rows are not presently
target-forced.  Therefore any graph-nonexistence or Conway-99 implication
that relies on `d(ker A)>=15` is vetoed.  Wave143 itself supplies feasible
formal points rather than such a nonexistence claim, so the exact replay
receives no veto.

## Independent S6 reconstruction

Without importing or executing Wave143 code, the verifier rebuilt all 62
locally admissible six-vertex classes, checked the frozen source alignment,
and signed the Wave21 affine class counts by `(-1)^(6+e(T))`.  This gives

```text
S6 = 2024484 + (512/3)n3
M6 = epsilon*2^27*S6.
```

The reconstruction uses the target identity

```text
q(A 1_T) = |T| + e(T) (mod 2)
```

and the already frozen six-vertex census.  It does not infer individual
output weights from six-vertex isomorphism classes.

## Eight exact rational points

All eight submitted points pass:

- both Arf signs at `n3=708`;
- both Arf signs at `n3=4158`;
- both Arf signs at the formal minimum `n3=0`; and
- both Arf signs at the formal maximum `n3=838878579/128`.

Across the eight points the verifier independently replayed:

```text
1,600 ordinary forward/inverse MacWilliams rows
   32 distinguished split-enumerator systems
   56 signed identities M0 through M6
  752 shadow inequalities for t=6,...,99
```

Every submitted dual enumerator equals the independently computed forward
transform.  Every nonnegativity, support, normalization, forced lower bound,
dual-complement, distinguished-pair, split row-sum, split first-moment,
split parity, and split-range check passes.  The points are genuinely
rational: depending on the point, 31--33 image coefficients and 48--52 dual
coefficients are nonintegral.

The weak rational optimum is exact but unhelpful:

```text
0 <= n3 <= 838878579/128 = 6,553,738.8984375.
```

The lower endpoint is the explicit model condition `n3>=0`.  At the upper
endpoint the degree-six shadow inequality is active:

```text
2024484 + (512/3)n3 <= C(99,6).
```

The stored optimum witnesses attain both endpoints, so this inequality is
an exact proof of optimality for the encoded rational projection.  It is far
weaker than the independent graph-count bound `n3<=4158`.

## Critical HNF reconstruction

The verifier did not accept the hashes in `lattice-certificate.json` on
trust.  It independently rebuilt the full equality matrix with

```text
41 image variables A_w
100 dual variables D_t
  1 variable k, where n3=3k
109 equality rows
142 variables total.
```

For each sign, exact FLINT HNF arithmetic gives rank `109` and nullity `33`.
The verifier reconstructed the integral particular solution at `k=0` and
the homogeneous step with `delta k=1`, replayed both against the matrix, and
then independently recomputed their comma-encoded SHA-256 digests.  Both
matrix digests and all four enormous-vector digests, coordinate counts,
maximum decimal-digit counts, and `k` values match the sealed certificate.

Necessity is elementary.  Before introducing `k`, the cleared target row is

```text
3 M6 = epsilon*2^27*(3*2024484 + 512*n3).
```

Modulo three, the coefficient of `n3` is nonzero, so `3|n3`.  The
reconstructed `delta k=1` step proves sufficiency at the equality layer.
Thus the exact equality-lattice projection is

```text
n3 in 3 Z.
```

This HNF layer is weaker than the rational Wave143 slice: it omits
`D_1=...=D_14=0`, lower bounds, nonnegativity, complement symmetry, split
systems, and shadow inequalities.  Its huge particular and homogeneous
vectors may contain negative coordinates.  It proves no nonnegative
integral enumerator.

## Status wall

The four integer-solver runs ended `UNKNOWN_HARD_TIMEOUT` and are accepted
only as telemetry.  They are not infeasibility evidence.

The verified result is exact rational feasibility in a strengthened formal
projection plus the equality-only congruence `3|n3`.  Integral nonnegative
feasibility, a binary code, an adjacency matrix, a strongly regular graph,
external novelty, and Conway-99 all remain `UNKNOWN`.

## Reproduction

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave143-binary-s6-projection\independent_verify.py

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave143-binary-s6-projection -p "test_*.py" -v

python -B -m unittest discover `
  -s attempts\wave143-binary-s6-projection -p "test_*.py" -v
```
