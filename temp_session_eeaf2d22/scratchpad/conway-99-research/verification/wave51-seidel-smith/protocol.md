# Wave 51 independent verification protocol

Status: `UNKNOWN` until the checks and hostile tests below are complete.

## Frozen scope

Independently check the Wave 51 discovery claim for the Seidel matrix
\[
S=2A-J+I
\]
of a hypothetical `srg(99,14,1,2)`.

The verifier will:

1. rederive `S^2 = 49(I+J)`, the rational spectrum, and the determinant;
2. prove or refute the claimed 7-primary Smith exponents without importing
   discovery code;
3. determine whether ranks modulo 2, 5, and 7 determine the full Smith form;
4. rederive the square-zero Jordan type modulo 7;
5. rederive the symmetric-square dimension bound;
6. enumerate every abstract Smith profile for `r=1..49`, with special
   attention to the imported endpoint interval `r=28..44`;
7. attack edge cases, factor ordering, local-to-global assembly, and hidden
   existence or symmetry assumptions.

## Restrictions

- Discovery code and artifacts are evidence under test, not dependencies of
  the independent reconstruction.
- No graph, Seidel matrix, automorphism, or realizability is assumed beyond
  the frozen conditional equations.
- Abstract compatibility of invariant factors is not graph existence.
- The endpoint remains `UNKNOWN` unless an independently checked
  contradiction or construction is produced.
- Corrections to discovery claims are recorded explicitly and are not made
  silently in discovery files.

