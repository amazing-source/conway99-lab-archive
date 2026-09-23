# Wave 32 indecomposable verifier: failed objections and active premises

The verifier did not import or execute
`attempts/wave32-indecomposable/exact_check.py`. Candidate bytes and all
named public inputs were frozen before inspection. The clean-room checker
was written and passed before static comparison.

## Objections that fail

### Primitive columns really do make the rows generate

For a full-column-rank integral matrix `X`, the index of
`X^T Z^231` in `Z^44` is the gcd of the maximal minors. Primitivity makes
that gcd one. The hostile matrix

```text
X = [[2],[0]]
```

has full rational rank but row lattice `2Z`; it confirms that full rank
cannot replace primitivity.

### Connectivity is exactly the decomposition boundary under minimum four

If the row nonorthogonality graph disconnects, primitive row generation
makes the component spans an integral orthogonal direct sum. Conversely,
in an integral orthogonal split, minimum at least four forces every
norm-four row into exactly one summand, so the graph disconnects.

The minimum premise is active: in `A1 orthogonal_sum A1`, the mixed row
`(1,1)` has norm four while occupying two norm-two components.

Wave 31's `21|b` projector trace and actual-incidence `33|b` commutator
leave only coordinate-block sizes `0` and `231`. This actual-incidence
premise cannot be replaced by an abstract projector.

### The switched three-row motif is unique

An independent enumeration of all `{-2,-1,0,+1}^3` edge labels and all
row-sign choices finds exactly three ordered edge placements and one
switching class:

```text
{-2,-2,-1}.
```

Its canonical Gram has determinant `20` and all-ones norm `2`. Replacing
the `-1` by `+1` gives attainable signed norms `{6,10,22}`, so the sign is
active and no norm-two combination survives.

### The trace normalization has a factor two

For one motif, exact matrix multiplication gives

```text
tr(A_-1 A_-2^2)=2.
```

Two disjoint motifs give trace four. The two orientations of the unique
`-1` edge explain the factor:

```text
tr(A_-1 A_-2^2)
 = 2 * #{unordered {-2,-2,-1} triples}.
```

### The endpoint pair census does not force a motif

At `n3=708`, `sum q=472`. The exact unordered counts are

```text
M=+1:  2546
M= 0: 22161
M=-1:   708
M=-2:  1150.
```

The clean-room hostile labeled graph preserves all four counts, is
connected, and has zero forbidden motifs. It intentionally drops the
positive-semidefinite rank-44 projector/frame realization. Thus pair
counts and connectivity alone cannot prove the decisive trace positive.

### The corrected finite-field ranks hold, but universal self-orthogonality does not

For `m=v_p(h)`, local elementary discriminant form gives

```text
rank_Fp(S)=44-m,
rank_Fp(G)=m,
rank_Fp(M)=44-m.
```

Primitivity gives `rank_Fp(X)=44`, and the column-code hull has dimension
`44-m`. It is self-orthogonal only when `m=0`. All eight determinant rows
were hard-matched independently.

The false rank inference is actively refuted:

```text
over F3: X=(1,1,1)^T has rank 1 but X^T X=0;
over F7: X=(1,2,3)^T has rank 1 but X^T X=0.
```

A nonisotropic one-column example over each field refutes universal
self-orthogonality.

### The binary shadow is consistent even with connected support

The independent construction uses the nine nonzero singular vectors in
each of eleven four-dimensional hyperbolic spaces, ten doubled singular
bridge rows, and fifty-six doubled filler rows. It has:

```text
231 nonzero singular rows,
row sum zero,
rank(X)=44,
X^T X = 22 hyperbolic planes,
M symmetric alternating idempotent,
rank(M)=44,
M1=0,
connected nonorthogonality graph.
```

Its odd-pair count is `806`, not the endpoint count `3254`; it deliberately
drops the integral entry profile and positive-semidefinite lift. It proves
only that the named mod-two properties, even together with connectivity,
are not contradictory.

## Static candidate comparison

No blocking mathematical defect was found.

The submitted package has nonblocking verification-coverage gaps:

1. The corrected `F3/F7` ranks and hull statements occur in the prose and
   failed-route ledger, but not in the submitted result JSON, checker, or
   tests. The independent suite supplies all eight rows and hostile
   counterexamples.
2. Candidate row generation and the two directions of the
   connectivity/decomposition equivalence are returned largely as prose.
   The independent checker supplies exact index and lattice controls.
3. The submitted `-1 -> +1` test checks only the all-ones sum. The
   independent sign census verifies that the minimum over every sign choice
   is six.
4. The submitted binary construction has eleven orthogonal support blocks;
   it does not test compatibility with support connectivity. This is not a
   defect in its stated finite-field scope. The independent bridged
   construction strengthens the control to connected support.
5. The submitted tests import the discovery checker and therefore cannot
   serve as the independent verification required by `AGENTS.md`.

The candidate's seven-entry artifact manifest and five-entry input freeze
both validate byte-for-byte. The independent verifier did not replay the
candidate executable.

## Boundary

```text
rootless decomposable actual endpoint:             impossible upstream
surviving rootless actual endpoint indecomposable: verified reduction
{-2,-2,-1} motif forbidden under rootlessness:     verified reduction
actual incidence forces the motif:                 UNKNOWN
motif forcing from pair counts/connectivity:       REFUTED
rootless indecomposable endpoint:                   UNKNOWN
n3=708:                                            UNKNOWN
Conway-99 existence/nonexistence:                   UNKNOWN
novelty:                                           UNKNOWN
```
