# Wave 28 orchestrator correction ledger

Date: 2026-07-24

Frozen public base:
`d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b`

This ledger records corrections and failed routes without rewriting the
chronology of the submitted reports. None changes the headline bound:

```text
n3 >= 708
induced_C6_count >= 209994
n3=708 / Conway-99 / novelty: UNKNOWN
```

## 1. Formal discriminant-form count

The live glue/discriminant derivation initially expected eleven formal
Milgram-compatible finite quadratic modules. The exact discovery checker
found twelve, and a hostile test rejects the stale count eleven. The
independent implementation again finds exactly twelve.

This is a corrected finite census, not a realization theorem. None of the
eight determinant rows is excluded.

## 2. Cyclic order-21 invariant factors

The frozen discovery report says:

> There can be no cyclic factor of order 9, 49, or 21: every invariant
> factor is killed by 21.

The order-21 clause is false. A cyclic group `Z/21` is killed by 21 and is
isomorphic to `Z/3 direct_sum Z/7`. The publication-safe replacement is:

> No `p`-primary cyclic factor has order `p^2` or higher. Invariant factors
> divide 21 and may have order 21.

The independent verifier assigns `PASS_WITH_CORRECTION`. The corrected
3-primary and 7-primary decomposition, exact levels, twelve-form census,
local sign comparison, root-glue theorem, and `46 -> 32` coordinate-pattern
census do not use the false wording.

## 3. Simultaneous-neighbor freeze and hostile controls

The candidate freeze changed during independent verification. The final
accepted freeze is

```text
7b8fce3763e2f6d4db2e0f7841e680d01486195d3ea4b6b04c5f59ace768d90a
```

and the superseded hashes are retained in the verifier's failed-run log.
A proposed `41 -> 42` support mutation unexpectedly remained valid and is
therefore a positive control, not a rejecting mutation. The replacement
`41 -> 2` mutation is the active negative control.

The direct unreduced 44-dimensional root enumeration exceeded its 124-second
budget. That timeout is retained as `NON_EVIDENTIARY`; the accepted result
comes from the complete exact blockwise reverse-LDL enumeration.

The verifier run report and audit initially used a placeholder instead of
the required full input commit. They were repaired to the public-base hash
above. The final publication hashes are:

```text
audit:
  79876274f467b4a13b3f95bf03961177cc56940d1ceecd206f6eff1647738aa3
run report:
  71bcb257872d6695b2dcbabd75c8ad2929ba59e7b4872175d47e14bae323067e
manifest:
  068d9270a83b0d99a39bbc8cda8a18773c62d5899fcba202c42755f79145e985
```

Both accepted two-neighbors are abstract arithmetic/lattice controls only.
They supply no `X`, projector `M`, Schur-square identity, or graph.

## 4. Theta source retention, enumeration, and strengthening

The theta verifier fetched and hash-checked the two catalogue pages while
building its independent input, then removed the raw HTML. The public package
retains URLs, access metadata, byte counts, raw-response hashes, attributed
numeric matrices, canonical matrix hashes, and an optional live
fetch-and-hash replay. It redistributes no copied HTML or paper.

Several preprocessing profiles timed out before a reusable exact result and
are preserved in the audit. The successful fraction-free closed-ellipsoid
run visits `15,053,011` recursion nodes and enumerates all `146,880`
norm-four vectors of `LAMBDA(F)`. A deterministic replay produces the same
JSON:

```text
24298ae282c7baa252a39ffe96fc37b7c696cb51f14b9ddea2318a59b4335b7f
```

The verifier strengthens the discovery statement
`min(21 S0^-1)>=14` to the exact value

```text
min(21 S0^-1)=28.
```

This is not a repair to a false discovery claim.

The first telemetry commit omitted two manifest-listed `.log` files because
of the repository-wide ignore rule. They were force-added, then normalized
to LF before publication. The mathematical result and audit hashes did not
change. The final run-report and manifest hashes are:

```text
run report:
  16af82dcc5db7d5664f0a68ba855e4e60bd79c7b401a4575568e6fd8c6fac640
manifest:
  50a5e3d4b5bb066b4b281c80d6d2caa0906afc21b9de99e12731177f661c6fed
```

## 5. Literature-service limits

The proof-separated literature audit freezes and executes 35 queries and
retains 17 metadata-only source records. One official strongly regular graph
table could not be opened through the search service, and no authenticated
zbMATH connector was available. Both are recorded as access limitations, not
zero-result evidence.

A 2025 refereed article explicitly describes Conway-99 existence as open,
and a 2026 SAT preprint reports attempts without resolution. No exact Wave 28
match was found in the bounded search, but openness after the access date,
novelty, and priority remain `UNKNOWN`.

## Publication wall

The independently accepted Wave 28 results are:

- corrected necessary discriminant/root-glue restrictions;
- a rootless bare `h=729` lattice/theta control;
- two simultaneous-neighbor abstract arithmetic/lattice controls; and
- a bounded current-source audit.

They neither construct nor exclude the full endpoint package. In particular,
the bare rootless control has no primitive `Z^231` embedding, marked
231-vector frame, `Q`, `B`, Schur-square certificate, or graph.
