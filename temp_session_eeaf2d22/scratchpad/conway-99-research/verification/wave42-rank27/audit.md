# Wave 42 rank-27 verifier audit

Date: 2026-07-27 UTC

Verdict:

```text
all eleven local types exclude rank 26: VERIFIED
universal rank_F7(M)>=27:             VERIFIED
discovery comparison discrepancies:  0
endpoint n3=4158 excluded:            NO
```

The verifier froze only independently verified Wave 39--41 inputs and its
own clean-room protocol before opening Wave 42 discovery artifacts.  It
independently derived the singular symmetric block formula and the exact
rank-26 equality condition.

The seven even-part lanes regenerated every minimum-`F` labelled
permutation and every labelled `R`, covering 1,714,426,560 pairs with exact
finite-field rank-at-most-one rejection.  The four all-odd lanes used an
independent pivot/mate reconstruction CSP whose completeness proof covers
19,916,886,528,000 labelled pairs.  No survivor exists.

The first byte replay exposed nondeterministic elapsed-time fields in the
precomparison JSON.  That failed freeze is retained.  The only repair
removed timing metadata; the repaired result preserved every mathematical
field and subsequently replayed byte-for-byte.

Final gates:

- independent full replay: PASS;
- independent hostile tests: 19 passed, 0 failed;
- discovery tests: 10 passed, 0 failed;
- discovery manifest: 21 entries, PASS;
- discovery composition hash: expected SHA-256, PASS;
- exact comparison: zero discrepancies, PASS.

This verifies a characteristic-seven rank theorem.  It does not solve
Conway-99, construct the graph, exclude the prism-free endpoint, improve the
general `n3` upper bound, or establish novelty.
