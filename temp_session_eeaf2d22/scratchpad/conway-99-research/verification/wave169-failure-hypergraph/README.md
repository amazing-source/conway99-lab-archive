# Wave 169 independent verification

Verdict: `VERIFIED_WITH_SCOPE`.

Two independent hostile audits confirm:

- one-mark Wagner completion is a zero-or-one order-eight event;
- `W8>=18710`, `F<=16640`, `F<16648`, and `E<=8` are equivalent;
- the 40 marks split into 36 core and four mandatory fringe failures;
- integral one-hot mismatch energy is exact bookkeeping but not a PSD proof;
- the current pairwise/root-local relaxation admits five simultaneous
  optional failures; and
- it therefore cannot prove a pointwise four-failure upper bound.

The five-failure gadget is not a full SRG and is not asserted globally
extendable. The verified result is only a failure of the current relaxation.
A higher-order failure hypergraph, overlapping-root closure, or full exact
conic certificate remains `UNPROVED`.
