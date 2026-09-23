# Wave 195: Hilton--Milner flag diversity

This package proves, conditionally on the prism-free rank-11 endpoint,

```text
Q>=6980.
```

The analytic chain is:

1. selected and raw exact-three companion pairs define canonical flags;
2. at a fixed center, each flag gives a three-subset `A_x(T)` of the seven
   triangle blocks through that center;
3. ternary cancellation and dual distance at least four make the local
   three-subset family simple and intersecting;
4. Hilton--Milner and the common-star `lambda=1` analysis give the uniform
   local bound `j_x<=39`;
5. the resulting oriented-label slack combines exactly with the
   independently verified Wave194 inequalities; and
6. `Q0>=13959/2`, so integrality gives `Q>=6980`.

The old `Q=6930` equality face is excluded directly as a corollary.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave195-leaf-packet-intersection-proof-a\exact_check.py --verify attempts\wave195-leaf-packet-intersection-proof-a\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave195-leaf-packet-intersection-proof-a\test_exact_check.py
```

The checker performs fixed `F_3` cancellations, binomial arithmetic, and
exact rational coefficient algebra only. It performs no graph, code,
cover, SAT, LP, configuration, enumeration, or isomorphism search.

Status: `DERIVED_PENDING_INDEPENDENT_VERIFICATION`.
