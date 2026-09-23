# Alternative-space strategy assessment

The scalar Fricke LP is productive but not yet positioned to close a row.
Its positive mass first appears at norms 20 through 28, while the verified
graph-to-lattice dictionary identifies signed-unit `-4` eigenvectors only
through norm 18. The following translations look more promising.

## 1. Vector-valued theta series and the discriminant code

Replace the single scalar theta series by one component for each orbit of
the discriminant group `K*/K`. The Weil representation couples these
components under `S` and `T`, retaining information erased by the scalar
sum. Wave 80's verified `F_7` code gives a natural orbit partition and
MacWilliams-type constraints.

Why it may help: the large Wave 101 mass cannot move freely among shells and
cosets. A vector-valued positivity certificate could force mass into a
specific code-weight class that the graph geometry forbids.

Roadblock: the discriminant group has size `7^(44-q)`. The calculation needs
orbit reduction from the graph/code action, not literal enumeration.

## 2. Exact integer and congruence programming

Strengthen the seven-variable rational cone with:

- even integrality of all theta coefficients;
- the full level-one mod-7 affine coefficient relations, not only an
  objective residue;
- higher coefficients generated from the same 15 modular coordinates;
- rigorous shell upper bounds.

Why it may help: several LP optima are highly fractional, especially for
`q=12,14`, so an exact branch-and-cut or congruence-lattice formulation may
raise them materially.

Roadblock: Wave 101's zero-prefix controls are already integral and even
through degree 14, and the Wave 71 congruence alone permits very long gaps.
Integrality without additional structure is therefore unlikely to force the
norm-18 shell.

## 3. Harmonic theta or Jacobi forms for the marked 99-vector frame

Insert harmonic polynomials, or introduce elliptic variables paired with the
99 marked norm-28 vectors in `L`. This turns frame moment identities into
modular/Jacobi coefficient constraints.

Why it may help: the scalar theta series forgets which vectors meet which
marked frame vectors. Harmonic moments retain exactly the angular data
needed to connect a large shell count to the graph.

Roadblock: one must derive a small, proof-producing basis and exact
positivity/Gram constraints. Raw Jacobi dimensions can become large.

## 4. Shell interaction SDP or association-scheme LP

Treat norm shells as spherical codes in dimension 44 and constrain their
pairwise inner-product distributions. Couple the Wave 101 lower bounds to
positive-semidefinite Gegenbauer moment matrices and to the known marked
frame.

Why it may help: the elementary mod-2 upper bound is orders of magnitude too
large, but semidefinite shell bounds can exploit the allowed integral inner
products and cross-shell compatibility.

Roadblock: ordinary one-shell kissing bounds are unlikely to suffice.
The computation must include cross-shell and marked-frame blocks and emit an
exact rational PSD certificate.

## 5. Code weight enumerators and invariant theory

Translate shell vectors to residue classes in the verified `F_7`
overlattice code, then use complete/symmetrized weight enumerators and
invariant-theory restrictions.

Why it may help: code enumerators give exact arithmetic constraints and
scale better than enumerating lattice vectors. They are also compatible with
the vector-valued theta route.

Roadblock: the precise norm-to-composition map is proved only in the shortest
range. Beyond norm 18, multiple coordinate profiles and lifts must be
retained rather than silently identified with signed-unit vectors.

## Recommended next experiment

Build a small orbit-reduced vector-valued model through degree 14 for the
`q=14` row first. It has the strongest scalar lower bounds and the earliest
positive prefix (norm 20). Couple discriminant-code orbit variables to an
exact two-shell (`20` and `22`) Gegenbauer/Gram relaxation. Keep the combined
integer-congruence formulation as a hostile control.

The success criterion should be either:

1. a checked exact certificate forcing positive mass at norm at most 18;
2. a checked upper bound below one of the Wave 101 prefix lower bounds; or
3. a rigorous null certificate showing this orbit reduction still admits a
   formal feasible point.
