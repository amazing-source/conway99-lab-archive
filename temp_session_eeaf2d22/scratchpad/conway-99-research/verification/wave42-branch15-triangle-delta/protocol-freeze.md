# Wave 42 branch-15 triangle-delta verification protocol

This clean-room verifier was written from the frozen Wave 37 OPB, the public
rooted labelling convention, and the candidate statement delivered to the
orchestrator. The discovery implementation and clause catalogue were not
opened before this implementation was completed.

The verifier must independently:

1. hash and parse the 574,615-row compressed OPB;
2. replay generalized-unit propagation to a fixed point;
3. confirm that `x2=1` is a direct one-term consequence;
4. reconstruct the rooted full vertices `[1,15,17]` as a graph triangle;
5. enumerate every disjoint second triangle and all six cross matchings;
6. simplify the resulting clauses with the independently replayed closure;
7. bind both canonical clause streams by SHA-256; and
8. reject any claim that the reduction is SAT, UNSAT, an endpoint exclusion,
   a new general upper bound, or a Conway-99 solution.
