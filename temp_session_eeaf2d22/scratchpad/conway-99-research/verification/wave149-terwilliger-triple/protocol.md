# Wave 149 independent verification protocol

## Frozen discovery input

The sealed discovery manifest is

```text
attempts/wave149-terwilliger-triple/package-manifest.sha256
```

with SHA-256

```text
84bea47182b6a59b69f5df29d4f7a8cdf71bff63cfbc47947b1e65013d09d70f.
```

The verifier may read the manifest, prose, and stored JSON data.  It must not
import or execute discovery code.

## Independent tasks

1. Derive the `12+12+12+60` triangle-root partition from
   `(v,k,lambda,mu)=(99,14,1,2)`.
2. Derive the matching-composition trace for rooted triangular prisms.
3. Reconstruct the proposed fixed-point-free matching witness from its
   mathematical description.
4. Independently build the forced `36 x 36` Gram matrix.
5. Check symmetry, integer entry bounds, diagonal 10, row sum 60, and exact
   agreement with the sealed stored matrix.
6. Prove PSD and rank by exact commuting-involution characters and separately
   recompute rational rank.
7. Confirm `rank(G)=32<=60`.

## Evidence boundary

- Floating eigensolvers are not used.
- Solver timeouts or `unknown` statuses have no evidentiary force.
- Feasibility of the Gram projection is not a binary incidence factor or a
  graph realization.
- The verifier may promote only the declared local projection.

