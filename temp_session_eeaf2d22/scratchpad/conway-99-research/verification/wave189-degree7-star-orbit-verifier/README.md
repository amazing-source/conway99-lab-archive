# Wave 189 degree-seven and orbit verifier

Status: `VERIFIED_WITH_SCOPE`.

This clean-room package audits two logically separate conclusions under the
frozen conditional rank-11 endpoint model:

1. a 16-cell exact rational complete-enumerator control satisfies the
   one-star polygon lift, complete MacWilliams constraints through total
   degree seven with `B70=B07=99`, the star-pair rows in degrees 12--14,
   all ordinary rows, and the quadratic typed-moment census; and
2. private-label extraction closed under exact-three companion orbits gives
   the conditional circuit theorem `Q>=4852`.

The first item is relaxation feasibility only. It constructs no code, point
set, graph, or endpoint. The second is a conditional theorem inside the
endpoint model and is not a Conway-99 resolution.

The verifier does not import either discovery checker. Its arithmetic,
cyclotomic transform, local polygon lift, canonical quadratic-form counts,
singleton translation, orbit packing, Hoffman null boundary, and equality
cancellation are reconstructed independently.

Run:

```powershell
.\.venv\Scripts\python.exe -B verification\wave189-degree7-star-orbit-verifier\independent_check.py --verify verification\wave189-degree7-star-orbit-verifier\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave189-degree7-star-orbit-verifier\test_independent_check.py
```
