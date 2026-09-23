# Wave 128: finite-primary eigenlattice split

Status: `DERIVED` discovery; independent verification required.

This package shifts the conditional Wave 109 rank-74 incidence-kernel
lattice away from characteristic seven and into its finite discriminant
group at `2,3,5`.  The outside graph is still unknown, but its linear block
equations fix its action on that discriminant group.

For

```text
U=Lambda intersect eig_Q(D,3),     rank(U)=42,
K=Lambda intersect eig_Q(D,-4),    rank(K)=32,
k=rank_F7(D+4I on Lambda)=r-12,
```

exact local Smith elimination gives

```text
A_U = Z/256 + Z/4 + (Z/9)^2 + (Z/3)^2 + (Z/5)^2
      + (Z/7)^k,

A_K = (Z/8)^4 + Z/9 + (Z/3)^2 + (Z/7)^k.
```

In particular,

```text
det(U)=2^10 3^6 5^2 7^k,
det(K)=2^12 3^4 7^k,
min(U),min(K) >= 4.
```

Exact cyclotomic Gauss sums give non-seven phases `-i` for `U` and `-1`
for `K`.  Milgram then forces both elementary seven-primary forms to have
phase `-1`, equivalently type `O^-(k,7)`.

All imported rows `k=16,18,...,30` survive.  These are exact necessary
conditions, not constructed eigenlattices and not an extension of the
motif.  The motif, Conway-99, and novelty remain `UNKNOWN`.

Reproduce with the standard Python library:

```powershell
python -B attempts\wave128-alternative-spaces\exact_check.py `
  --verify attempts\wave128-alternative-spaces\exact-results.json
python -B -m unittest discover `
  -s attempts\wave128-alternative-spaces -p "test_*.py" -v
```
