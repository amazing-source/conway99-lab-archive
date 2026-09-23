# Retained verifier failures and non-evidentiary experiments

## Reverse-order/permuted-coordinate enumeration

The first independent CVP implementation combined the affine substitution
`x=residue+modulus*y` with both a reversed symmetric-triple order and
nontrivially permuted Cartan coordinates. The complete `build_results` run
timed out after 64 seconds before producing a result. A second timed run of
the two searches in that ordering was terminated after roughly 34 seconds.

This was a performance failure, not a solver negative and not evidence about
either tensor ball. The final checker retains the materially different affine
CVP substitution and unrestricted-`y` recursion but uses canonical Cartan and
lexicographic triple order. It completes and reproduces the independently
constructed Gram hashes and exact empty-ball counts.

## Dropped-`aaa` parity mutation

An exploratory hostile mutation removed only the six `P_aaa` congruences and
searched the original caps. The combined mutated search timed out after 64
seconds without returning a witness or a complete exhaustion. It is retained
as non-evidentiary and is not cited by the verdict.

The operative parity attack instead checks every repeated-index case,
including all six `aaa` coordinates, and uses two terminating controls:
even replacement scales admit the zero tensor at cap zero, while a separate
rank-one affine-CVP instance has an exact first witness on its cap-eight
boundary.
