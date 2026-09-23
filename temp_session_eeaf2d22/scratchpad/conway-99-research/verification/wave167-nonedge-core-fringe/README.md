# Wave 167 independent verification

Verdict: `VERIFIED_WITH_SCOPE`.

The verifier independently confirms:

- the 22-edge nonedge-rooted cross graph at `P=0`;
- its exact 18-core/four-fringe decomposition;
- failure of all four fringe marks;
- uniqueness, but not existence, of a valid completion;
- `F=166320-8*W8`;
- `E=8*(18711-W8)`;
- the endpoint implication `E>=16`; and
- the sufficiency of the strictly weaker global target `E<=8`.

The verifier also checks an abstract shell satisfying all currently used
one-root equations while producing extra core failures. Therefore those
local equations do not prove the old pointwise four-failure lemma.

The shell is not a full strongly regular graph. No endpoint exclusion,
strict `n3` bound, graph, novelty, or Conway-99 resolution is verified.
