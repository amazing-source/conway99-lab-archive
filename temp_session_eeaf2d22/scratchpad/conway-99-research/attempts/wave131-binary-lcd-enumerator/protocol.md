# Wave 131 protocol

Date frozen: 2026-07-28.

Role: proof A / alternative-space discovery.

## Frozen inputs

Assume a hypothetical `srg(99,14,1,2)` with adjacency matrix `A`.  Import
the independently verified Wave2 facts:

```text
over F2, A^2=A;
im(A) is an even LCD [99,54] code;
ker(A) is the dual LCD [99,45] code;
both codes have minimum weight at least 8;
1 lies in ker(A).
```

No automorphism or vertex-transitivity is assumed.

## Questions

1. What exact image/kernel codewords are forced by subsets of at most three
   vertices?
2. Are the two subset maps injective on that domain?
3. Do ordinary binary MacWilliams identities contradict the forced
   coefficients if the dual minimum is sharpened to 15?
4. Does a bounded integral formal-enumerator search terminate?
5. Which data are lost by an ordinary enumerator?

## Gates

- Graph-derived counts are recomputed, not copied from the task.
- A rational formal enumerator is not called integral.
- An integral formal enumerator would not be called a code.
- A code with matching parameters would not be called the target graph.
- Timeout and solver `UNKNOWN` prove no infeasibility.
- LCD and distinguished-row Gram data are not inferred from ordinary
  coefficients.
- Discovery cannot verify itself.
