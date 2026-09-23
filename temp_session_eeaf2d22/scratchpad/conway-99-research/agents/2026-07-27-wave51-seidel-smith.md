# Wave 51 proof-B report: Seidel Smith form

Role: proof B  
Claim label: `CANDIDATE`  
Date UTC: 2026-07-27T19:02:48Z

## Assignment

Seek a structurally different exact reformulation of the Conway-99 endpoint,
preferably through modular representation theory, integer lattices, or the
association scheme, rather than another rooted moment matrix.

## Candidate result

For the Seidel matrix
\[
S=2A-J+I
\]
of a hypothetical `srg(99,14,1,2)`, put
\[
r=\operatorname{rank}_{\mathbf F_7}(S).
\]
The identity \(S^2=49(I+J)\), its rational spectrum, and its ranks modulo 2
and 5 imply the conditional Smith normal form
\[
\operatorname{SNF}(S)=
\operatorname{diag}(1^r,7^{99-2r},49^{r-1},490).
\]
Equivalently,
\[
\operatorname{coker}(S)\cong
(\mathbf Z/7)^{99-2r}\oplus
(\mathbf Z/49)^{r-1}\oplus
\mathbf Z/490.
\]

Modulo 7, the complete Jordan type is
\[
J_2(0)^r\oplus J_1(0)^{99-2r}.
\]
The pure-square representation has Gram matrix \(J-I\) of rank 98 and gives
\[
\frac{r(r+1)}2\ge98,\qquad r\ge14.
\]

## Outcome

This is an exact lattice classification conditional on the imported
identities, but it does not contradict the current verified interval
\(28\le r\le44\). All 17 integer ranks survive the exact profile checks. The
association-scheme symmetric-square route therefore collapses to a weaker
bound than the existing \(r\ge28\).

The package is in `attempts/wave51-seidel-smith/`. It includes a frozen
protocol, full derivation, deterministic result artifact, exact checker, eight
unit tests, input hashes, and explicit failed-route analysis. It must remain
`CANDIDATE` until a separate verifier reproduces it.

