# Wave 53 multi-root WL clean-room verification protocol

Frozen: 2026-07-27T20:02:54Z

Repository baseline: `a4a61658356253fb95cf68252c972a4f79df38fe`

Role: independent verifier under `AGENTS.md`. This protocol was written before
reading the discovery implementation, exact result, derivation, tests, run
report, or agent report. Filenames and the externally assigned claim surface
were known.

## Frozen claim surface

For each ordered two-root relation `K`, `B`, `C`, and `D`, independently
reconstruct the finite rooted CSP induced by the `srg(99,14,1,2)` equations.
Check:

- the common-`K` class sizes `5`, `2`, `1`, and `0`, respectively;
- all exact-two common-neighbor constraints and caps;
- candidate-node construction, identity, and merge rules;
- the claim that a specified shared variable in the `B` case is forced true;
- exact stable 2-WL orders/color counts
  `K 319/285`, `B 323/584`, `C 325/321`, `D 326/63`;
- tractable triangle-core 3-WL color counts
  `K 107`, `B 321`, `C 240`, `D 61`;
- positive local cap controls, only for the local scopes actually claimed.

No result may be promoted beyond the finite rooted model that is exactly
reconstructed and checked.

## Clean-room construction

1. Derive the vertex types and Boolean edge variables directly from the four
   root relations and the strongly regular parameters, not by importing or
   calling discovery code.
2. Represent each unordered edge variable by a canonical ordered endpoint pair.
   Candidate nodes use structural provenance; merge only when the mathematical
   construction proves identity, never because labels or neighborhoods happen
   to coincide.
3. Generate exact constraints as equations over distinct variables. Check for
   accidental duplicate literals, omitted fixed contributions, and candidate
   aliasing before solving.
4. For every cap, enumerate all satisfying assignments independently. A
   forced-literal claim requires both satisfiability with the claimed value and
   unsatisfiability with its negation, by complete finite enumeration or an
   independently checked exact solver transcript.
5. Positive controls must perturb only the scoped cap and exhibit a concrete
   satisfying witness. They do not establish global extendability.

## WL reconstruction

1. Build the claimed finite relational structures from clean-room CSP data.
2. Use exact integer tuples throughout. Initial colors encode the full stated
   vertex/tuple relations and equality pattern.
3. Refine synchronously to a fixed point. Canonicalize every round by sorting
   complete signatures, so color IDs do not depend on hash order, insertion
   order, or prior numeric IDs.
4. Re-run under multiple vertex permutations and require invariant partition
   cell-size multisets, color counts, and intersection parameters after mapping
   vertices back.
5. Compute 2-WL over all ordered pairs. Compute only the explicitly claimed
   triangle-core 3-WL domain, after independently checking its closure/domain
   definition. Report tuple-domain order separately from color count.
6. Check intersection parameters directly from final stable colors and fail if
   a purported color class has nonconstant transition counts.

## Adversarial audit

Attack hidden automorphism assumptions, arbitrary completion choices,
candidate identity errors, missing caps, endpoint orientation mistakes,
stable-color nondeterminism, discovery/result circularity, incomplete record
envelopes, stale or self-referential manifests, and status inflation. Solver
exit codes and self-authored discovery tests are not certificates.

## Resource and status policy

Before high-memory runs, measure available physical memory and keep at least
15 percent free. Abort or partition the computation if the threshold would be
crossed. Labels:

- `VERIFIED`: independently reproduced exact finite claim;
- `REFUTED`: explicit counterexample or corrected exact value;
- `UNKNOWN`: incomplete, ambiguous, or not independently reproducible;
- `CANDIDATE`: discovery artifact not yet independently certified.

The endpoint remains `UNKNOWN` unless these finite rooted computations by
themselves prove the unrestricted Conway-99 statement, which is not expected.
