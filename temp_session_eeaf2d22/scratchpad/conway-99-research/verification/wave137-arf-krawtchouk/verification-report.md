# Wave 137 clean-room verification

Claim label: `VERIFIED_SCOPED_RATIONAL`

## Verdict

No verifier veto is issued. The sealed discovery manifest has SHA-256
`2175aad6a21216db67b668a3450855592405f584f2490c58b1d21ce6983da02c`;
all 33 listed entries replay byte-for-byte. All fourteen staged exact
rational witnesses, seven for each Arf sign, pass the independently rebuilt
ordinary MacWilliams and distinguished-row systems.

The terminal witnesses are:

- `binary-shadow1-plus.json`,
  SHA-256
  `c3dbc0cee57a5505455202af51cbb5a31ff4c7cf075ddc8f3f8351efe7833092`;
- `binary-shadow1-minus.json`,
  SHA-256
  `9919a367ea393085d310199a4ac3ac23c68fd1bde511c4cf4e01f2d5e81a10bd`.

Both terminal witnesses pass every signed Krawtchouk identity through
degree five, the explicit degree-6 and degree-93 lower cuts, and an
independent sweep of all 94 absolute shadow bounds from degree 6 through
99.

## Clean-room reconstruction

Before opening the frozen Wave 137 package, the verifier rebuilt the
length-99 binary Krawtchouk transform from its defining binomial sum and
the four Wave 132 split systems from row sums, first moments, parities,
set-theoretic ranges, and forced distinguished-pair counts.

With the dual enumerator eliminated, the Wave 132 ordinary equality system
has 41 image variables

```text
A_0,A_14,A_16,...,A_92
```

and rank 16. Appending the signed rows

```text
sum_w (-1)^(w/2) A_w K_t(w) = G_R S_t
```

for

```text
(S_0,S_1,S_2,S_3,S_4,S_5)
 = (1,-99,3465,-56595,462924,-1821204)
```

raises the cumulative ranks to

```text
17,18,19,20,21,22.
```

Each row contributes exactly one new equality. For both signs, every
augmented rank equals the corresponding coefficient rank. Discovery did
not publish a rank table; this is an independent verifier result, not an
attributed discovery claim.

The values through `S_4` were also reconstructed combinatorially. In
particular, extending the exact six three-vertex types gives numerator
`1,851,696`, hence `S_4=1,851,696/4=462,924`. The supplied exact
`S_5=-1,821,204` target was independently encoded with the direct
Krawtchouk formula and replayed against both terminal witnesses.

## Exact replay totals

- 14 exact rational branch witnesses passed.
- 2,800 ordinary forward/inverse MacWilliams rows passed.
- 56 distinguished split systems passed, including every shell row,
  first moment, parity count, range, and forced pair lower bound.
- 14 exact distinguished pair tables passed.
- Both Arf signs satisfy `G_R=epsilon*2^27` and
  `G_E=-G_R/32=-epsilon*2^22`.
- Every signed row claimed at each cumulative stage passed.
- Both terminal witnesses pass all degree-6-through-99 absolute shadow
  bounds.
- 11 hostile verifier tests passed, including mutations of an ordinary
  coefficient, a signed branch coefficient, a split entry, and a pair
  table.

## Z4 audit

The four Z4 floating-scout JSON artifacts were hash-inventoried. They
contain numerical failure or unknown outcomes, not exact witnesses or
Farkas certificates. No mathematical inference is accepted from those
statuses. No exact Z4 Arf branch certificate exists in the sealed package,
so the Z4 branch remains `UNKNOWN_NUMERICAL`.

## Status wall

These are formal rational points in a projected enumerator system. They do
not prove integral feasibility, full genus-two compatibility, a binary or
quaternary code, an adjacency matrix, or a strongly regular graph.
Conway-99 remains `UNKNOWN`, and novelty remains `UNKNOWN`.

