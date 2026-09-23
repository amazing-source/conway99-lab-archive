# Independent verifier request for Wave 97

Do not rely on the discovery implementation beyond the frozen input hashes.
Reconstruct the mathematics independently.

## Required checks

1. Starting from symmetric \(S\), zero diagonal, off-diagonal
   \(\{\pm1\}\), and \(S^2=0\pmod7\), prove or refute
   \[
   R*R=\mathbf1^\perp,\qquad R*R*R=\mathbf F_7^{99}.
   \]
2. Verify that the degree-\(0,1,2,3\) evaluation dimensions at \(r=28\)
   are \((1,28,98,99)\), and that the quadratic Veronese images have one
   all-nonzero relation.
3. Independently derive
   \[
   \operatorname{rank}_{\mathbf F_7}C_2(S)=\binom r2
   \]
   and the complete Smith form for all
   \(r\in\{28,30,\ldots,42\}\).
4. Check the rank-28 Smith multiplicities
   \[
   1^{378},7^{1204},49^{1687},343^{1204},
   2401^{280},24010^{98}.
   \]
5. Recompute the compound row weight 1,947 directly from the
   \((99,14,1,2)\) intersection numbers.
6. Verify the rational spectrum, trace, and
   \(C_2(S)^2=2401C_2(I+J)\).
7. Verify projectivity of the 4,851 compound columns from
   \(d(R^\perp)\ge6\).
8. Independently compute the \(O^-(16,7)\) projective orbit sizes and the
   embedding-orbit ratio in \(O^-(42,7)\).
9. Attack the assertions with hostile changes of field, order, rank, Smith
   alignment, and orthogonal sign.
10. Preserve
   `rank 28 = UNKNOWN`, `Conway-99 = UNKNOWN`, and `novelty = UNKNOWN`
   unless a separate certificate changes them.

The verifier may veto promotion but must record corrections rather than
silently modifying the discovery package.
