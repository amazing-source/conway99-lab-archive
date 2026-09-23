# Verification protocol

1. Hash all named discovery artifacts and current generator sources before
   inspection.
2. Never import or execute discovery Python.
3. Use only exact integer and rational arithmetic for promoted claims.
4. Reconstruct cut coefficients from graph and flag semantics, not from
   solver output.
5. Replay every retained witness equality and every stored cut value.
6. Reconstruct principal entries by unit directions and polarization.
7. Treat post-freeze files and source drift explicitly; do not silently update
   the evidence seal.
8. Treat all numerical solver statuses as diagnostics.
9. Maintain at least 15% free physical memory.
10. Limit `VERIFIED` to the finite feedback claims; endpoint and graph status
    remain unknown.
