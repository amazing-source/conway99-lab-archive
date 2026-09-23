# Wave 47 proof-agent report: polynomial-calculus alternative

Role: proof B
Status: `CANDIDATE`; independent verifier required

I shifted the refined branch-15 endpoint formula into a squarefree
polynomial-calculus problem over `F2`. A global degree-two matrix was rejected
on resource grounds: 3,312 free primary variables imply roughly 5.5 million
quadratic columns before elimination fill.

The exact safe replacement was seven mate-coordinate windows. Each is a
self-contained 276-variable system combining two perfect matchings and a
degree-two bipartite cross graph. Complete degree-two closure found no
contradiction and no assignment, but found 13 independent linear XOR
relations beyond the imported parity rows. Exact-block-only controls reproduce
the same final linear spaces, so these relations come from matching
integrality, not the imported prism clauses.

The same census proves a concrete obstruction to the proposed low-degree
route: all 34,340 active Wave 43 cuts are all-negative degree-four monomials.
Unassumed degree three cannot see them. A useful continuation is therefore
one of:

1. independently verify and add the 13 XORs to a solver with native Gaussian
   reasoning;
2. run degree three under selected true triangle-controller assumptions,
   which lowers incident Wave 43 cuts from degree four to degree three; or
3. design a different extension-variable encoding in which the four-way prism
   monomial has lower algebraic degree, with equivalence checked separately.

Complete candidate relations, decoded edge supports, matrix hashes, replay
commands, restrictions, and the verifier protocol are under
`attempts/wave47-branch15-polynomial/`.

Nothing here closes branch 15 or any endpoint case. Conway-99 remains
`UNKNOWN`.
