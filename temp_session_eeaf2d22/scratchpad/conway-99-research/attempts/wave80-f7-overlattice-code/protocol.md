# Wave 80 protocol: characteristic-seven overlattice code

Date frozen: 2026-07-27

Role: discovery

Claim label: `DERIVED`

## Conditional imports

Assume the conditional Wave 66 and Wave 71 lattice conclusions attached to
a hypothetical \(\operatorname{srg}(99,14,1,2)\).  In particular:

- \(L\) is an even positive-definite lattice of rank \(44\);
- \(L^*/L\cong(\mathbf Z/7)^q\), where
  \(q\in\{2,4,\ldots,16\}\);
- \(7L^*\subseteq L\);
- \(r=\operatorname{rank}_{\mathbf F_7}S=44-q\), for
  \(S=2A-J+I\);
- \(v_i=3u_i\in L\), for \(0\le i<99\), satisfy
  \[
  \langle v_i,v_i\rangle=28,\quad
  \langle v_i,v_j\rangle=-8\ (i\sim j),\quad
  \langle v_i,v_j\rangle=1\ (i\not\sim j),
  \]
  \[
  \sum_i v_i=0,\qquad
  \sum_i v_iv_i^{\mathsf T}=63I.
  \]

Wave 71 additionally forces, when \(q=16\), short-vector counts
\[
N_{14}+N_{16}+N_{18}\equiv2\pmod{14}
\]
with the exact signed-support dictionary recorded in that package.

This package does not independently verify either imported wave.

## Frozen code

Define
\[
C=\left\{
  \big(\langle y,v_i\rangle\bmod7\big)_{i=0}^{98}:
  y\in L^*/7L^*
\right\}\subseteq\mathbf F_7^{99}.
\]

The quotient in the domain, the evaluation scale, and the Seidel sign are
fixed.  They may not be replaced by \(L^*/L\), by an unscaled real dot
product, or by the opposite Seidel convention.

## Questions

1. Is evaluation injective, and what are the dimension and hull of \(C\)?
2. How is the hull related to \(\operatorname{row}_{\mathbf F_7}S\)?
3. Which finite orthogonal-space type is forced at \(r=28,q=16\)?
4. Do the Wave 71 norm-\(14,16,18\) vectors give forbidden code classes?
5. Can small-support dual words or MacWilliams identities exclude rank 28?

## Separation rules

- Discovery cannot promote itself to `VERIFIED`.
- No automorphism, transitivity, or restricted graph search is assumed.
- Exhaustion is used only for the complete set of \(2^{10}\) labelled
  five-vertex graphs and is accompanied by exact local and outside-pattern
  checks.
- Positive moment slack is not a complete weight enumerator.
- A surviving code profile is not a graph or lattice construction.
- Conway-99 and novelty remain `UNKNOWN`.
