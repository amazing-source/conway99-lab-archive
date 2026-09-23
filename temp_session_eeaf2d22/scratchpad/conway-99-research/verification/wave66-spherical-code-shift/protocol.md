# Wave 66 independent verification protocol

Role: `verifier`.

Frozen target: audit the sealed discovery package
`attempts/wave66-spherical-code-shift/` conditional on a hypothetical
`srg(99,14,1,2)`, with

```text
S = 2A-J+I
```

and no automorphism assumption.

The complete discovery directory, including hidden bytecode files, was
inventoried by path, byte size, and SHA-256 before any discovery file was
read.  That freeze is
`discovery-inventory-preinspection.tsv`.

Imported `VERIFIED` prerequisites are kept separate:

- the SRG parameter identities and restricted eigenspace multiplicities;
- `rank_F2(A)=54` and `rank_F3(A)=45`;
- `ker_F2(A)` has minimum weight at least eight;
- every weight-eight word in that kernel has independent support, and every
  graph vertex meets that support in zero or two points;
- universally `rank_F7(S)>=27`;
- conditionally on `n3=4158`, `rank_F7(S)>=28`.

The verifier reconstructs all Wave 66 claims without importing or executing
the discovery checker.  Discovery artifacts are read only after the
independent result exists, for a mechanical comparison.

Promotion rules:

- a conditional necessary consequence may be `VERIFIED_SCOPED`;
- a scope error is recorded, not silently repaired;
- neither a discriminant group nor a surviving genus row constructs a
  lattice, frame, or graph;
- the endpoint, Conway-99, and novelty remain `UNKNOWN` absent a proof.

The verifier refuses computation below 15% free physical memory.
