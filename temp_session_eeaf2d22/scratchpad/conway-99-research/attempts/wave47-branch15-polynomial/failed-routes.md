# Wave 47 bounded and failed routes

## Unrestricted degree-two matrix not launched

After the Wave 42 closure, the branch still has 3,312 free primary variables.
An unrestricted degree-two linearization exposes roughly 5.5 million
quadratic columns and about 3.3 million products of the 987 independent linear
coordinate equations alone. Sparse elimination could fill far beyond its
input size. It was not launched because the user's 15% host-memory reserve is
more important than an uncontrolled global matrix.

The exact 276-variable mate-coordinate windows preserve complete local
constraint blocks and keep free physical memory above the stricter 20% guard.

## Unassumed degree three cannot use the new cuts

All 34,340 active Wave 43 rows are all-negative width-four clauses after the
frozen closure. Their polynomial axioms have degree four, so merely increasing
the standard Macaulay cap from two to three would still omit every new row.
No degree-three global job was launched under the false premise that it tested
those cuts.

## F7 deferred

The F2 calculation already exposed 13 exact XOR candidates and a clean
degree-four barrier. An F7 rerun was deferred until the F2 relations receive
independent replay; changing the field before that checkpoint would multiply
the verification surface without addressing the width-four obstruction.

## No status inflation

Zero derived contradictions and zero new assignments do not establish local
or global satisfiability. The 13 candidate relations do not close branch 15
and are not labelled `VERIFIED`.
