# Wave162 facial-reduction protocol

## Frozen scope

Analyze the exact Wave152 and Wave159 witnesses, cuts, and four-root
evaluations without modifying them. Seek a rigorously forced face of the
root-3 and root-12 PSD covariance cones. If none is certified, preserve an
exact negative/null result.

## Separation and evidence

- Wave162 writes only under `attempts/wave162-four-root-facial-reduction`.
- It is a discovery/derivation lane and cannot promote itself to `VERIFIED`.
- Exact scalar cut replay uses independent `Fraction` arithmetic.
- Frozen witness row-pass records may be used as inputs but are explicitly
  distinguished from independently rebuilt base equations.
- Sampled zero quadratic values are not called null vectors without a PSD
  premise.
- Conditional faces must state every assumed active equality.
- A count pseudowitness is not a graph.

## Resource boundary

Sample physical memory before and after analysis, fail below 15% free, and do
not start a large solve.

## Promotion boundary

An unconditional forced face requires an exact conic-dual exposing identity
checked independently against the full affine and PSD system. This package
does not contain such an identity.
