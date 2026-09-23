# Wave 62 rooted Terwilliger/SDP protocol

## Frozen scope

Assume a hypothetical `srg(99,14,1,2)` at the endpoint `n3=4158`, hence
with no induced triangular prism. Fix one graph vertex only to obtain the
standard rooted scaffold. Its 84 residual labels are the signed edges

```text
(ij, si, sj),  0 <= i < j < 7,  si,sj in {-1,+1}.
```

The scaffold group `C2 wreath S7` may relabel these objects. It is used only
to average matrices that are positive semidefinite for every hypothetical
completion. No element of this group is required to be an automorphism of
the completed graph.

## Orbital algebra

The unordered residual-label pairs have five off-diagonal scaffold orbits:

1. same support and Hamming distance one;
2. same support and Hamming distance two;
3. one support index, with the same sign there;
4. one support index, with the opposite sign there;
5. disjoint supports.

Together with the diagonal, their valencies are

```text
1, 2, 1, 20, 20, 40.
```

The checker reconstructs all 84 labels, proves that the six orbital matrices
form a commutative association scheme, reconstructs its intersection tensor,
and checks the six exact character rows and primitive idempotents.

## Endpoint edge counts

Let `y` count selected residual edges in orbit 2. The endpoint prohibition
sets all 84 orbit-1 candidate edges to zero. The exact Wave 3 relation
algebra gives

```text
orbit 1: 0
orbit 2: y
orbit 3: 84
orbit 4: 84-2y
orbit 5: 336+y
0 <= y <= 42.
```

This package rederives `2y+e4=84` spectrally but does not claim that identity
as new.

## Linear invariant SDP

Let `B` be the residual adjacency matrix. Its fixed spectrum is

```text
12^1, 3^40, 0^7, (-2)^6, (-4)^30.
```

The scaffold incidence subspaces of dimensions 6 and 7 are forced
`B`-eigenspaces for `-2` and `0`. If `E_1,E_6,E_7` are the first three
scheme idempotents, the rank-40 eigenvalue-three projector is exactly

```text
P3 = (B + 4I - 16E_1 - 2E_6 - 4E_7)/7.
```

Both `P3` and its rank-30 complement in the 70-dimensional residual kernel
are PSD. Their group averages lie in the six-dimensional orbital algebra,
so PSD reduces to six rational scalar blocks. The checker evaluates every
integer `y=0,...,42` and also proves feasibility for the full real interval
by affine endpoint checking.

## Bounded Schur/Terwilliger family

For each scaffold primitive idempotent `E_s` and all `a,b>=0` with
`a+b<=24`, the checker forms the exact group average of

```text
E_s o P3^(o a) o Pminus4^(o b),
```

where `o` denotes entrywise product. The Schur product theorem makes each
matrix PSD in every hypothetical graph. Binary adjacency makes every
averaged orbital coefficient affine in `h=y/42`; therefore evaluating
`h=0,1` proves or refutes the whole interval for this declared family.

Negative floating eigenvalues, numerical SDP statuses, or a nonhit in this
bounded family are never promoted. All arithmetic is `fractions.Fraction`.

## Status rule

This is discovery work. A strict upper bound or endpoint exclusion requires
an independently checked negative exact block, a rational dual certificate,
or a separate proof. Feasibility of the averaged relaxation is not a graph.
The verifier must inspect the package without relying on discovery internals.

Abort computational work if free physical memory approaches 15 percent.
