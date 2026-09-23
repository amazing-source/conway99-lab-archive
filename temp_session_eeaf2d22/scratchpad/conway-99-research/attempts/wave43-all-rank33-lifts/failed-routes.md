# Wave 43 boundary and failed route

## Component parity and forced-Gram exclusion

The all-264 census was designed to detect any rank-33 lift with a negative
entry in the forced `BB^T` matrix, a nonuniform component fibre balance, an
odd balance, or failure of the component Cauchy equality. None occurs.

This is a complete null result for those exact necessary tests, not evidence
that any lift extends to a full graph.

## Forced-Gram kernel cuts

Every forced Gram matrix has rational rank exactly 33. Its kernel is exactly
the span of the two fibre-indicator differences and the component contrast.
Those three column laws are already enforced by selecting one pair per fibre
and requiring small-component intersection two. Consequently a new linear
kernel cut cannot strengthen the three-way matching.

## Candidate-count classes

Every lift retains between 45,032 and 49,520 candidates after support,
component equality, and mixed-equation nonnegativity. Positive candidate
counts do not imply that sixty mutually compatible columns can be selected.
Conversely, a bounded solver failing to select them would not prove
nonexistence.

The remaining finite task is an exact three-way matching with all concurrence
equations, followed by the compatible outside-graph equations.
