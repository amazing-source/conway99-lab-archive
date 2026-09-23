# Wave 51 verifier audit

## Disposition

```text
exact tensor arithmetic:                         VERIFIED
interpretation as aggregate positive control:    VERIFIED
displayed averages as an association scheme:      REFUTED
prism-free endpoint:                              UNKNOWN
Conway-99:                                        UNKNOWN
novelty:                                          UNKNOWN
```

The `VERIFIED` label is scoped to the exact aggregate relaxation. It is not
a promotion of the endpoint or conjecture.

## Separation and provenance

Before inspecting discovery contents, the verifier hashed all nine files in
`attempts/wave51-global-triple-tensor/` and the discovery agent report. Those
hashes are preserved in `preinspection-freeze.sha256`. The discovery
manifest and its four-file input freeze both replayed without discrepancy.

The independent implementation has no import or subprocess dependency on
`attempts/wave51-global-triple-tensor/exact_tensor.py`. It parses the frozen
JSON certificate and rebuilds the claimed arithmetic from definitions.

## Findings

The SRG incidence derivation, triangle-intersection local graph and spectrum,
cross-edge matching argument, prism equivalence, and the two q-moment double
counts all check. Under the explicitly conditional assumption of zero
triangular prisms, they force `(x_0,x_1,x_2)=(32,144,36)`.

The signed relation identity

```text
S=K^2-17I-4K-J=B-D
```

has valency 4, spectrum `4^187,(-17)^44`, satisfies
`S^2+13S-68I=0`, and obeys `KS=SK=4K`. Spectral evaluation also confirms
`4I-S=21E_0`.

The frozen tensor has 21 positive canonical entries. Independent
normalization produces five nonnegative integral tables with the required
margin vectors. All 25 identity equations, 125 global balance equations,
five entries each for `K^2`, `KS`, `SK`, and `S^2`, and the local `3K6` row
pass. The family point `(288,0,288)` reproduces every parameterized entry.

Independent evaluation of

```text
sum_h p^h_ij p^k_hm = sum_h p^h_jm p^k_ih
```

over all 625 ordered quadruples finds exactly 100 failures. The first is
`81 != 153` at `(1,1,2,2)`. A digest and the complete ordered failure list
are recorded in `independent-result.json`.

## Hostile checks

Ten adversarial mutations are rejected:

1. a negative tensor entry;
2. a duplicated canonical entry;
3. a noncanonical relation ordering;
4. a one-unit tensor arithmetic change;
5. a one-unit supplied-table change;
6. a falsified associativity failure count;
7. a falsified spectral multiplicity;
8. endpoint status inflation;
9. Conway-99 status inflation;
10. novelty status inflation.

The baseline plus these mutations give 11 passing unit tests.

## Boundary

The positive tensor is only an aggregate control. It supplies neither an
association scheme nor a graph, and it does not prove that the endpoint is
realizable. Conversely, its association-scheme failure does not refute a
graph whose pair-local tables vary around the same averages. Quadruple
consistency and graph realizability remain absent. The endpoint and
Conway-99 therefore remain `UNKNOWN`.
