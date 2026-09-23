# Wave 51 verifier report: Seidel Smith form

Role: verifier  
Claim label: `VERIFIED` for the corrected scoped theorem  
Date UTC: 2026-07-27T19:09:30Z

## Verdict

I independently verified that the frozen identities force
\[
\operatorname{SNF}(S)=
\operatorname{diag}(1^r,7^{99-2r},49^{r-1},490)
\]
for \(r=\operatorname{rank}_{\mathbf F_7}(S)\), together with the mod-7
Jordan type
\[
J_2(0)^r\oplus J_1(0)^{99-2r}
\]
and the symmetric-square bound \(r\ge14\).

One discovery assertion is `REFUTED`: the signs' multiplicities in the
rational spectrum were reversed. The correct spectrum is
\[
-70^1,+7^{54},-7^{44},
\]
not \(-70^1,+7^{44},-7^{54}\). The incorrect list has trace \(-140\), while
\(\operatorname{tr}S=0\). This correction does not alter the absolute
determinant or the verified Smith, Jordan, and rank conclusions.

## Key hostile check

Ranks modulo 2, 5, and 7 do not by themselves determine the Smith form. The
determinant determines the unique 2- and 5-primary exponents, while the
identity
\[
49S^{-1}=(I+J)^{-1}S
\]
over \(\mathbf Z_7\) forces the reciprocal pairing of 7-adic exponents. At
\(r=28\), a second exponent list with the same rank and determinant is
\[
0^{28},1^{44},2^{26},3^1;
\]
the reciprocal pairing, not rank data, excludes it.

The complete audit, canonical independent artifact, frozen comparison, and
13 hostile tests are in `verification/wave51-seidel-smith/`.

## Boundary

The endpoint remains `UNKNOWN`. Every imported rank \(28,\ldots,44\)
survives. This work provides an exact necessary lattice classification, not a
construction or a nonexistence proof.

