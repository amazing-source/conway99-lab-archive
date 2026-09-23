# Wave 29 S0 frame exclusion: failed routes and correction chronology

## Scope

This file retains proof routes that were rejected or that become
non-conclusive after an active premise is removed. None is nonexistence
evidence outside the single frozen lattice

```text
S0 = K12 orthogonal_sum LAMBDA(F).
```

## Correction: `C_K` is not asserted positive semidefinite

An early shorthand in the task said "`C_K` integral/self-adjoint/positive."
That phrasing is too strong and was rejected before publication. The exact
statement used by the proof is:

```text
C_K=(B_K-I)/2 is integral and G_K-self-adjoint;
C_K is real-diagonalizable;
B_K=I+2C_K is G_K-positive;
therefore every eigenvalue mu of C_K satisfies mu>-1/2.
```

Negative eigenvalues in `(-1/2,0)` are allowed. The logarithmic inequality
has a separate strict proof on exactly that interval. No step assumes
`C_K` is positive semidefinite.

## Route 1: shell size alone

The frozen Wave 28 result gives

```text
r_S0(4)=147636.
```

This is far above the frame-visible floor `462`, so shell size cannot exclude
the endpoint. The successful route uses the orthogonal support of each
norm-four row, the tight-frame trace, and the Schur-square cubic trace.

## Route 2: determinant data without the rank-12 signature veto

From `det(Q)=5`, block integrality permits two formal allocations:

```text
(det(Q_K),det(Q_L))=(1,5) or (5,1).
```

If the first allocation were retained, then `det(B_K)=729`, exactly equal to
the eventual logarithmic cap `3^6`. There would be no contradiction. The
classical even-unimodular signature theorem is active: an even positive
definite unimodular rank-12 form cannot exist, so the first allocation is
removed and `det(B_K)=3645`.

## Route 3: block AM-GM without the cubic residue

Positivity and determinant one only give

```text
tr(B_L)>=32,
tr(B_K)<=28.
```

Without the row-alphabet conclusion that both traces are multiples of six,
the arithmetic pair `(tr(B_K),tr(B_L))=(28,32)` is not excluded. It would
give `tr(C_K)=8` and only the generic cap `det(B_K)<=3^8=6561`, which does
not contradict `3645`. The exact row equations and the identity
`tr(B_J)=sum_(i,j in J) M_ij^3` are therefore active.

## Route 4: logarithmic bound without integrality of `C_K`

The real diagonal control

```text
C_K=(1/2)I_12,
B_K=2I_12
```

is self-adjoint, has positive `B_K`, and has `tr(C_K)=6`, but
`det(B_K)=4096>729`. It violates integrality of `C_K`. Thus the nonzero
characteristic pseudodeterminant being a nonzero integer is essential, not
cosmetic.

## Route 5: calling a block matrix "split" before splitting the rows

The orthogonal decomposition of `S0` does not by itself make an arbitrary
`X`, `M`, `W`, `Q`, or `B` block diagonal. The missing bridge is the
norm-four observation: because both summands have minimum four, every
norm-four row has support in exactly one summand. Only after permuting those
rows do the five matrices acquire the displayed block form.

## Search and symmetry wall

No automorphism of `K12`, `LAMBDA(F)`, the row set, or a putative graph is
assumed. No finite subset search is used. In particular, failure to find a
marked 231-vector subset is not part of the proof.
