# Independent verifier protocol

Treat `endpoint_deck.py` as opaque until the following reconstruction is
frozen.

1. Independently enumerate the 62 locally admissible six-vertex and 208
   locally admissible seven-vertex isomorphism classes.
2. Build every seven-to-six vertex-deletion column and confirm that each
   column sums to seven.
3. Independently evaluate the corrected Wave 21 six-vertex formulas at
   `n3=4158`.
4. Reconstruct the 19 Hamiltonian types and their affine formulas with
   `h11=16632`.
5. Expand the stored 99-entry support to all 208 classes and check every
   deletion row, every Hamiltonian count, nonnegativity, integrality, and the
   total `binom(99,7)`.
6. Confirm that every seven-class containing the zero-count prism type has
   count zero.
7. Mutate at least one positive count and one Hamiltonian parameter and show
   that the exact checker rejects them.

Passing this protocol verifies feasibility of a necessary count relaxation
only. It cannot promote graph existence, endpoint existence, an improved
upper bound, Conway-99, novelty, or priority.
