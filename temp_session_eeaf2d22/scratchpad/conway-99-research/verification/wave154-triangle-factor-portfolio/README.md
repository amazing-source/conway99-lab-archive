# Wave154 clean-room verification

Verdict: **PASS_WITH_SCOPE**.

The verifier froze the discovery package before inspection and did not import
or execute discovery code.  From declarative Q1 certificates and independently
derived formulas it reproduced:

- both exact 24-by-60 binary partial factors and their claimed hashes;
- all diagonal and `G01` Gram blocks;
- the complete 384-element centralizer of the matching `M` and shift `P`;
- two size-384 Q1 orbits with empty intersection;
- 69,270 allowed triples, 292 triple orbits, 612 constraint rows, and
  1,039,050 integer-matrix nonzeros.

Seven hostile tests reject malformed or Gram-breaking Q1 data, exclude a
noncentralizing permutation, distinguish a true orbit member from the new
representative, and reject a zero-capacity triple.

The discovery label `VERIFIED_PORTFOLIO_NULL` is not accepted on the
discovery agent's authority.  This verifier promotes only the deterministic
finite claims above to `VERIFIED`.  Every solver-negative status remains
diagnostic because no checkable unsatisfiability proof was exported.

The complete 36-by-60 factor `C` remains **UNKNOWN**.  The residual matrix `D`
remains **NOT_REACHED**.  No graph, forced prism, Conway-99 resolution, or
improved `n3` bound follows.

## Reproduce

```powershell
python verification/wave154-triangle-factor-portfolio/exact_check.py `
  --verify verification/wave154-triangle-factor-portfolio/exact-results.json

python -m unittest discover `
  -s verification/wave154-triangle-factor-portfolio -p "test_*.py" -v
```
