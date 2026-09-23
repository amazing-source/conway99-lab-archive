# Wave 51 protocol freeze: Seidel Smith form

Status: `CANDIDATE` discovery work. This package is not a verifier report.

## Frozen target

Assume that a strongly regular graph with parameters
\[
(v,k,\lambda,\mu)=(99,14,1,2)
\]
exists. Its adjacency matrix \(A\) would satisfy
\[
A^2=12I-A+2J.
\]
Define the integral Seidel matrix
\[
S=2A-J+I.
\]

This lane asks:

1. What exact modular representation and Smith normal form must \(S\) have?
2. Does that classification contradict the independently established endpoint
   interval
   \[
   28\le r_7:=\operatorname{rank}_{\mathbf F_7}(S)\le44?
   \]
3. Does the induced symmetric-square representation give a stronger lower
   bound on \(r_7\)?

## Allowed inputs

- `verification/2026-07-22-wave2-audit.md`
  for the exact Seidel identity and spectrum.
- `verification/wave43-rank28/independent-results.json`
  for the independently checked lower bound \(r_7\ge28\).
- `verification/wave23-index-pranks/2026-07-23T192952Z-audit.md`
  for the independently checked equality between Seidel rank and the
  triangle-projector rank, hence \(r_7\le44\).

Their byte hashes are frozen in `input-freeze.sha256`.

## Restrictions

- No graph, Seidel matrix, or triangle geometry is assumed beyond the frozen
  equations and imported verified rank interval.
- No automorphism or orbit restriction is imposed.
- The argument is conditional on existence; compatible invariant factors do
  not construct a graph.
- Discovery code may check arithmetic consequences but may not promote this
  package beyond `CANDIDATE`.
- A separate verifier must reproduce the derivation and artifact bytes before
  any stronger status is considered.

