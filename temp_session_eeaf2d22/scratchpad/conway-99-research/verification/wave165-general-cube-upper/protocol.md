# Wave 165 verifier protocol

## Frozen target

Audit the unrestricted implication

```text
srg(99,14,1,2) => 12*C8 <= 37422+3*P = 41580-n3.
```

The identity `n3+3P=4158` is a separately verified input. All motif counts
are unlabelled induced-copy counts.

## Clean-room checks

1. Reconstruct the 2,079 induced-four-cycle count.
2. Reconstruct the fixed-cycle outside partition and ten singleton
   neighbors per anchor.
3. Exhaust all possible second common neighbors to prove that consecutive
   singleton classes form matchings of exact size nine or ten.
4. Identify the size-ten condition with adjacency of opposite edge apexes.
5. Check inducedness and both directions of the marked-square/prism
   bijection, including its factor three.
6. Check the local cube-extension injection, six faces per cube, and all
   unlabelled multiplicities.
7. Audit the endpoint floor and odd-`P` parity refinement.

## Fail-closed boundary

Reject any claim that assumes an automorphism, treats a candidate tuple as
an induced cube without checking chords, promotes literature novelty, or
infers endpoint exclusion from the motif inequality alone.
