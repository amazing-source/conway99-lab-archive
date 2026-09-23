# Retained limitations

1. **Wave150 witness as endpoint feasibility.** Refuted. It violates two
   exact four-root covariance blocks.
2. **One separated witness as endpoint infeasibility.** Invalid inference.
   Other endpoint count vectors are not covered by these certificates.
3. **No negative vector as PSD evidence.** Invalid inference. Root masks
   0, 1, 7, 11, and 13 remain exact-sign `UNKNOWN`.
4. **Numerical eigenvalues as certificates.** Rejected. Only exact integer
   quadratic values are used.
5. **Zero blocks.** Root masks 15 and 30 are exactly zero and therefore PSD,
   but this does not offset the non-PSD masks 3 and 12.

The next useful step is a universal endpoint-level separation, or a search
over the endpoint face with these four-root constraints imposed from the
start.
