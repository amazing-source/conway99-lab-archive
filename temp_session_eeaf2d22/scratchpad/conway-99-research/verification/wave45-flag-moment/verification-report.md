# Exact verification report

## Separation chronology

1. `protocol-freeze.md` was written before any Wave 45 discovery file was
   opened.
2. `independent_verify.py`, `independent-results.json`, and their tests were
   completed and committed in `independent-freeze.sha256`.
3. The independent full reconstruction replay and eight tests passed.
4. A comparison attempt against a mutable live checkpoint was discarded when
   the file changed concurrently.
5. Comparison resumed only after the orchestrator supplied the immutable v1
   filenames and SHA-256 values.

## Coefficient verification

The clean implementation enumerates every labelled simple graph through
order seven, filters the local `(lambda,mu)=(1,2)` common-neighbor caps, and
removes full permutation orbits. A rooted flag is canonicalized only under
permutations fixing every label pointwise.

For an unrooted class `H`, each coefficient counts ordered tuples
`(rho,A,B)` whose roots and two free selections have union exactly `V(H)`.
This proves that overlap orders are neither omitted nor multiply assigned.

The independently frozen stream sizes and hashes are:

| Family | Flags | Class records | Nonzero ordered entries | SHA-256 |
|---|---:|---:|---:|---|
| Vertex | 17 | 300 | 12,566 | `020ffe9943ded4adb77c308734fb05031723038d81fb7081cf9efed4352d0d27` |
| Ordered edge | 16 | 92 | 1,636 | `c4219e7f375f8f5b21e98f66d797d80dfd8183b73e3e7867d1a41ba8f72b69e0` |
| Ordered nonedge | 19 | 92 | 2,458 | `c7ea939d530d1713605f816a06a4acd77db1a77841e76fad89562b5d056d6564` |

Discovery stores only nonzero upper-triangle entries. The verifier expanded
them symmetrically, restored the clean naming convention, and obtained exact
equality of the complete serialized streams and the combined hash.

## Witness and quadratic verification

For each seven-class witness, lower-order counts were independently recovered
by

```text
sum_J x_J d_m(H,J) = binom(99-m,7-m) N_H.
```

Every division was exact and every result nonnegative. The reconstructed
matrices have the same canonical hashes as the sealed discovery result.
Standard-library rational LDL replay classified both pair-root matrices PSD
of rank one and both vertex-root matrices indefinite.

All 12 supplied integer directions were evaluated directly against the
independent vertex matrices. Every exact numerator matched and was strictly
negative.

## Cut verification

For each sealed direction `c`, the verifier independently formed

```text
c^T M_vertex c
  = constant_from_orders_4_to_6
    + sum_J coefficient_J x_J
  >= 0,
```

divided all coefficients by their exact greatest common divisor, reconstructed
the sparse record, and checked its canonical hash. All 17 cuts matched.

For each of 15 checkpoint witnesses, the verifier then checked:

- support uniqueness, positivity, total, and SHA-256;
- all 170 frozen Wave 44 equations using exact integers;
- every previously retained cut and its cut-value SHA-256;
- the independently reconstructed vertex-matrix SHA-256;
- the supplied next direction and its exact negative numerator;
- strict rejection by the newly appended cut.

The checkpoint's sixteenth solver call ended `unknown` because of timeout.
No UNSAT proof, PSD survivor, graph, or exhaustive certificate is present.

## Verdict

`VERIFIED`: coefficient streams, exact controls, the two stored-witness
refutations, and the internal consistency of immutable checkpoint v1.

`UNKNOWN`: feasibility of the entire PSD-constrained aggregate region,
existence or exclusion of the `n3=4158` endpoint, any stricter global upper
bound, Conway-99, novelty, and priority.

