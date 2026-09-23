# Independent audit: Wave 30 bare `h=729` lattice construction

## Verdict

**PASS, with deliberately narrow scope.** The submitted exact data independently
verify an explicit even positive-definite rank-20 lattice `T20` of determinant
`729`, minimum `4`, and exactly `5076` norm-four vectors. They also verify the
bare rank-44 direct sum

```text
S = T20 orthogonal_sum LAMBDA24
G = 21*S^(-1)
```

with `rank(S)=44`, `det(S)=729`, `min(S)=4`, `S` rootless, `G` even integral
positive definite, and `S*G=21*I44`.

This audit verifies no `Q`, `B`, `X`, `M`, `W`, tight frame, Schur-square
identity, or graph. It neither realizes nor excludes `n3=708`. Conway's
99-graph problem remains **UNKNOWN**.

## Independence and freeze

The construction report and all seven files in
`attempts/wave30-h729-construction/` were SHA-256 frozen before their contents
or checker internals were inspected. The input manifest was among those frozen
files. Its three direct dependencies were therefore precommitted; their live
bytes later reproduced the committed hashes. See `protocol-freeze.md`.

The verifier then:

- parsed only `exact-results.json`;
- wrote new rational linear algebra and enumeration code using the Python
  standard library;
- reconstructed and passed the complete arithmetic claim; and only then
- inspected the discovery prose/checker to compare serialization conventions
  and retained limitations.

The verifier does not import or execute discovery code.

## Exact matrix reconstruction

All six reconstructed rank-20 Gram matrices are symmetric, integral, even, and
positive definite. Positive definiteness passed two exact checks: rational
`LDL^T` with every pivot positive and independently recomputed positive
leading principal determinants. Fraction-free Bareiss determinants are `729`
for all six forms.

The reconstructed starting form is literally block diagonal:

| block | rank | determinant | Gram SHA-256 |
|---|---:|---:|---|
| `K12` | 12 | 729 | `b5745e7885765dfadaf9251fc742703bd1956b52415f52355a4c1ad12a41a788` |
| `E8` | 8 | 1 | `05643d8ce484a8dbf8e2f0053088da734cc78510d263fcbb8411756c84adc0c2` |

The five following reduced-form hashes are:

```text
9374ae66ba0bdede1cbd0649eb3957981784d09c60b60831733ea8e445f2045d
1433fc399784634e5e3101581182a5cbc2a9d12d811798bef8d37f4d59d7a674
1c0589783b5cf6652a902f8eb0ac706dd54d8243c72395d974f515bea1748a3f
242c3380102a5a1e69e8d51dbe3771936e4b08d4104234cd7dd5e4c58332774a
1890fe1973eed47850c307d0975ae393f2a8ab32a9d0b16b35ebcab7012445d6
```

They exactly equal the submitted hashes.

## The five 2-neighbor certificates

For each step, the verifier independently formed the binary primitive vector
`v`, the parity functional `x -> x^T A v (mod 2)`, and a full-rank basis `H`
of its kernel. It proved:

```text
[Z^20:H] = 2,
v is primitive,
v^T A v is divisible by 8,
v is in H but v/2 is not in H,
H is contained in P Z^20,
|det(P)| = 1,
[P Z^20:H] = 2.
```

Thus `P Z^20 = H + Z(v/2)` and the common sublattice has index two in both
neighbors. The submitted `P^-1` was reproduced rather than trusted. Every
alleged LLL matrix `U` was checked integral and unimodular, and each identity

```text
A_raw = P^T A P
A_next = U A_raw U^T
```

was reconstructed exactly.

| step | `v^T A v` | `det(P)` | `det(U)` | both common indices | roots after |
|---:|---:|---:|---:|---:|---:|
| 1 | 24 | 1 | -1 | 2 | 112 |
| 2 | 72 | 1 | 1 | 2 | 48 |
| 3 | 56 | 1 | -1 | 2 | 20 |
| 4 | 64 | 1 | -1 | 2 | 6 |
| 5 | 88 | 1 | 1 | 2 | 0 |

No LLL optimality, canonical-basis claim, automorphism, or isometry
classification is assumed.

## Complete short-vector enumeration

The independent enumerator uses the exact decomposition

```text
A = L D L^T.
```

After coordinates above index `i` are fixed, it converts the remaining
ellipsoid condition to an integer inequality

```text
(b*x_i-a)^2 <= floor(b^2 * remaining / d_i)
```

and computes both endpoints with an integer square root. There are no
floating-point bounds, acceptance tests, heuristic boxes, or omitted residue
classes.

The six complete norm-two searches give:

```text
240 -> 112 -> 48 -> 20 -> 6 -> 0.
```

Their accepted partial-node counts are:

```text
4054, 2664, 3658, 1812, 3214, 3094.
```

For every nonempty submitted root shell, the independently enumerated sorted
coordinate set reproduces the submitted canonical SHA-256 digest.

The final complete search through norm four visits `128154` accepted partial
nodes and gives:

```text
norm 0: 1
norm 2: 0
norm 4: 5076
```

The full sorted norm-four shell reproduces:

```text
7b83bccafcd31ee04e0c028f10f51363d3c3b0a22f5f87dc9bbbd14875ca6010.
```

Since the form is positive definite and even, no norm-two vector exists, and
norm-four vectors do exist, `min(T20)=4`.

Enumeration coverage was attacked in three independent ways:

1. the algorithm was compared with an exhaustive Cartesian search for a
   coupled three-dimensional form;
2. exact cutoff-boundary cases were checked; and
3. shell counts were reproduced after nontrivial unimodular shears and sign
   changes of both `T20` and the Leech block.

## Scaled duals and rank-44 assembly

Fresh Gauss-Jordan inversion over `Fraction` gives:

| matrix | property | SHA-256 |
|---|---|---|
| `3*T20^-1` | even integral | `ae64112b005b9515b1a0d677d252fbc32e8624791670b937c1579aeb3a4b8e8f` |
| `21*T20^-1` | even integral | `006011e5ea2fa29cc942bcaa3e72e6d300a549fbad6b6991f3edffb20371a024` |

The submitted 24-dimensional lower block is independently symmetric, even,
integral, positive definite, unimodular, and has an even integral inverse. A
complete norm-two search visits `40672` accepted partial nodes and returns only
zero. A diagonal entry `4` supplies an explicit norm-four vector, so its
minimum is exactly four. The checked hashes are:

```text
Leech Gram:     28b55230a24b4cc0e544b083181c05c79d599eb845fc503cfb6c9e4221ad64fb
Leech inverse:  616ce72c39079ccc3a9d531fcb82fc89f601ddbb57e9c02d38c13af837f7299c
```

The submitted `S` is literally the block diagonal sum, not merely claimed
isometric to it. Exact checks give:

```text
rank(S)=44
det(S)=729
min(S)=4
roots(S)=0
S SHA-256=3fbeb977e268913f8eb2f2b9b27897eb954ad73ccd66cdb8e124b13b6527303b
```

An additional direct 44-dimensional norm-two enumeration visits `43766`
accepted partial nodes and returns only zero.

Finally, the verifier computes `21*S^-1` itself and obtains the submitted
matrix:

```text
G SHA-256=c3402926e02395a3e932e0ca2d7f2f0aa3550e7cbd856c0ac76441b4921e211e.
```

`G` is symmetric, even integral, and positive definite, and exact matrix
multiplication gives `S*G=21*I44`.

## Hostile tests and retained failures

`test_independent_check.py` contains 24 hostile tests. All pass. Mutations of
symmetry, parity, definiteness, neighbor support, parity pivot, rational
neighbor basis, supplied inverse, unimodularity, following Gram, direct-sum
coupling, scaled dual, and status disclaimers are rejected.

Two initial verifier-only scope-gate failures and one digest-serialization
difference are preserved in `failure-ledger.md`. None was a mathematical
discrepancy. The discovery lane's frame-solver and Leech norm-four timeouts are
also retained as nonresults.

## Status wall

The strongest justified promotion is:

```text
exact bare T20 construction:       VERIFIED
exact bare rank-44 S/G package:    VERIFIED
five-neighbor route classification: NOT CLAIMED
determinant-five Q and B:           NOT CONSTRUCTED
105/126 tight frames:               NOT CONSTRUCTED
X, M, W, Schur package:             NOT CONSTRUCTED
graph certificate:                 NOT CONSTRUCTED
n3=708:                             UNKNOWN
Conway-99:                          UNKNOWN
novelty:                            UNKNOWN
```
