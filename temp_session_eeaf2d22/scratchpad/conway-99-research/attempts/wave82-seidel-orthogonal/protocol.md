# Wave 82 protocol

## Frozen scope

Assume a finite simple undirected graph with adjacency matrix `A` satisfies

```text
A^2 = 12I - A + 2J
```

at order 99.  No automorphism, transitivity, Cayley, circulant, endpoint
`n3=4158`, or chosen-root assumption is allowed.

## Imported verified facts

1. For `S=2A-J+I`,
   `S^2=49(I+J)` and
   `spec(S)={-70^1,+7^54,-7^44}`.
2. If `r=rank_F7(S)`, then the 7-primary Smith exponents of `S` are
   `0^r,1^(99-2r),2^r`.
3. Universally,
   `r in {28,30,32,34,36,38,40,42}`.

The exact imported bytes and hashes are in `input-freeze.sha256`.

## Discovery question

Can the Seidel identity be converted into an equivalent integral orthogonal
matrix with a complete Smith form, giving a new certificate-friendly search
space?

## Evidence rules

- All claims in this package are discovery-side `DERIVED`.
- A symbolic identity is not a graph or matrix construction.
- A surviving invariant-factor profile is not realizability evidence.
- A null rank exclusion is retained as a null result.
- Independent reconstruction is required before promotion.

