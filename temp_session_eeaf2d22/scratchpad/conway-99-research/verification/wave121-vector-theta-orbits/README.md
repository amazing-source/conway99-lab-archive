# Wave 121 independent verification

Verdict: `VERIFIED_SCOPED`, conditional on the frozen verified lattice,
code, scalar modular, and C4-incidence inputs.

The verifier froze all 15 discovery files before source inspection and
then independently rebuilt:

- the `O^-(14,7)` and `O^-(30,7)` exact-value orbit counts;
- the two nonzero-isotropic theta dictionaries;
- the q=14 scalar modular expansion through `y77`;
- both old Wave 101 optimizers in the enlarged cone;
- both conditional identities and their exact controls;
- the short-range code injection and anisotropic upper bound;
- the primitive C4 index-70/index-10 marking;
- the 140-to-20-to-11 theta-component reduction and finite Fourier phase;
- and the finite truncated coefficient null.

No mathematical correction was required.  The full orthogonal calculation
uses aggregate sums only and assumes no lifted lattice or graph
automorphism.  The formal theta controls are not lattices, and the
truncated Jacobi table is not a Jacobi form.

Rank 28, rank 30, Conway-99, and literature novelty remain `UNKNOWN`.

Reproduce with:

```text
python -B verification/wave121-vector-theta-orbits/independent_verify.py --verify verification/wave121-vector-theta-orbits/independent-results.json
python -B verification/wave121-vector-theta-orbits/compare.py
python -B -m unittest discover -s verification/wave121-vector-theta-orbits -p "test_*.py" -v
python -B verification/wave121-vector-theta-orbits/seal_checkpoint.py --verify
```
