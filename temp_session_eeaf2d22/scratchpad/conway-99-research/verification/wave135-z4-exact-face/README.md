# Wave135 clean-room exact-face verification

Status: `VERIFIED` for the sealed exact linear-algebra checkpoint; rational
feasibility is `UNKNOWN_WALL` and integral feasibility remains `UNKNOWN`.

Using only the frozen Wave134 statements, the standard-library verifier
reconstructs the 161 forbidden dual transform rows on the 1,119 admissible
primal coefficient orbits.

The exact zero-row rank is 143, so its linear nullity is 976. The proof has
two independent halves:

- target odd-symbol shells give the exact upper bound
  `7+44+44+44+1+1+1+1=143`; and
- a displayed 143-by-143 integer minor is nonzero modulo `1,000,000,007`,
  proving rank at least 143 over the rationals.

Adding `A_(99,0,0)=1` and the total-size equation gives rank 145 and affine
dimension 974. The frozen torsion size supplies a further independent
equality,

```text
sum_(source nodd=0) A_source = 2^54,
```

giving rank 146 and affine dimension 973.

The dual torsion-shell equation is then redundant. Exactly,

```text
dual_allowed_b0_numerator + sum_(7 forbidden b0 rows)
  = 2^98 * primal_b0_indicator.
```

Thus the primal equality and the zero rows imply
`sum_(dual nodd=0) B=2^44`.

For nonzero residue weights, constant fibres give integer divisibility, not
additional fixed rational equalities: primal orbit-shell sums are multiples
of `2^54`, and dual orbit-shell sums are multiples of `2^44`.

The verifier also defines fail-closed exact schemas for dense rational primal
witnesses and sparse Farkas certificates. It rejects floats, missing primal
coordinates, unknown constraints, negative Farkas inequality multipliers,
nonzero stationarity, nonpositive contradiction margins, and status
promotion beyond the declared relaxation.

The sealed discovery package's 16 files all match their manifest. Its 18
primitive dependency vectors vanish exactly on the clean-room matrix and are
independent; its selected 143-row basis has exact rank 143. The two bounded
row-generation artifacts end with violated inequalities and are verified
only as `UNKNOWN_WALL` null traces. No rational primal or Farkas certificate
exists in the package.

Reproduce:

```powershell
python -B verification\wave135-z4-exact-face\independent_face.py `
  --verify verification\wave135-z4-exact-face\independent-results.json

python -B -m unittest discover `
  -s verification\wave135-z4-exact-face `
  -p "test_*.py" -v
```
