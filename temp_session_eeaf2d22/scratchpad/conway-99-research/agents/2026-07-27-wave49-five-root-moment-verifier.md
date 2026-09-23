# Wave 49 five-root moment verifier

Role: verifier
Verdict: `VERIFIED_SCOPED`
Git baseline: `e4394aa9172fa97a6dafa9158148c2183603a01b`

I froze and completed an independent implementation before opening the
Wave49 discovery code, coefficients, or result. The precomparison result is
SHA-bound at
`77fc1e5d6b7d5ca417cdfd61cfef14cdb6d777d85b43cc17f2bad10af2a45930`.

The verifier independently enumerated all admissible labelled graphs through
order seven, removed complete permutation orbits, reconstructed all 21
canonical five-root attachment families and all 683 labelled-root tensors,
and checked raw per-class injection totals without any automorphism divisor.
It checked all 2,520 canonical-root/S5 mappings and 680,400 order-six/seven
class-tensor congruences.

The independently reconstructed discovery-schema coefficient document equals
the sealed `coefficients.json` exactly. Its canonical payload hash is
`940ed2820a3501e1b5017a5a3dafce55789ce189a754ef94af01954f28a79511`.
The labelled sparse tensor hash
`c239f2b4f31a26dc331f5ad28d664cd48e69417384279f78119978469ec30f80`
also matches.

All 42 Petersen/Clebsch direct integer outer-product controls equal their
coefficient expansions and satisfy their all-ones identities. All 17 support
hashes and exact lower decks were reconstructed. Every one of the 357 witness
matrices matches; the independent lane found a strict exact integer negative
direction for each before comparison. All 357 discovery-supplied directions
then replayed to the claimed strictly negative integer quadratic values.

The numerical combined-SDP artifact was not opened for mathematical evidence.
Its solver status, floating duals, residuals, and eigenvalue margins are not
part of the verdict.

Eight mutation tests pass. Physical memory remained above the 20% floor and
no Wave49 verifier process remains.

Packaging caveat: the discovery directory had no package manifest at
comparison time. Exact discovery artifact hashes are recorded in
`verification/wave49-five-root-moment/comparison.json`; the verifier package
has its own manifest.

This finite result rejects the 17 supplied aggregate witnesses only. Endpoint
`n3=4158`, branch closure, a strict upper bound, graph construction, novelty,
and Conway-99 remain `UNKNOWN` or `NOT_PROVED`.
