# Exact derivation

## 1. Quotient from a semiregular order-11 action

Let `A` be the adjacency matrix of an `srg(99,14,1,2)`. The strongly regular
graph identity is

```text
A^2 = 12 I - A + 2 J.
```

Assume a specified automorphism generates a semiregular `C_11` action. Its
nine orbits all have size 11. For a vertex in orbit `i`, let `q_ij` be its
number of neighbors in orbit `j`. Orbit invariance makes these counts
well-defined. Because all orbit sizes are equal and the graph is undirected,
`Q=(q_ij)` is symmetric.

On vectors constant on each orbit, `J_99` acts as `11 J_9`. Restricting the
strongly regular identity to this nine-dimensional fixed subspace gives

```text
Q^2 + Q = 12 I + 22 J,       Q 1 = 14 1.
```

Inside one orbit, adjacency differences in `Z_11` occur in pairs `{a,-a}`;
zero is forbidden by simplicity. Therefore each diagonal entry `q_ii` is
even.

## 2. Why the quotient multiplicities are 1, 4, 4

On the orthogonal complement of the all-ones vector, the adjacency equation is

```text
x^2 + x - 12 = (x-3)(x+4) = 0.
```

If the multiplicities of `3` and `-4` in the full 99-vertex graph are `f` and
`g`, then

```text
f+g=98,
14+3f-4g=trace(A)=0.
```

Thus `f=54` and `g=44`.

The two eigenspaces are rational: their projectors are rational polynomials in
`A`. A nontrivial irreducible rational representation of `C_11` has dimension
`phi(11)=10`. If `r` is the fixed dimension in the 54-dimensional
3-eigenspace, then

```text
54-r is divisible by 10,   0 <= r <= 8.
```

The unique possibility is `r=4`. Since the full fixed subspace has dimension
nine and already contains the all-ones vector, the fixed dimension in the
`-4` eigenspace is also four. Consequently

```text
spec(Q) = {14, 3^4, (-4)^4},
trace(Q) = 14 + 4*3 - 4*4 = 10.
```

This representation step is essential. The quotient polynomial by itself also
allows a formal multiplicity pattern with six copies of `3`; that pattern
cannot arise from the stated semiregular action on the full graph.

## 3. Seven row shapes and three diagonal cases

Fix a row and write `d=q_ii`. The diagonal equation is

```text
sum_j q_ij^2 + d = 34,
sum_j q_ij = 14.
```

The first relation implies `d^2+d <= 34`; together with evenness, this leaves
`d in {0,2,4}`. Exhausting nonnegative integer multisets for the eight
off-diagonal entries gives exactly:

```text
d=0:
  (0,0,2,2,2,2,3,3)
  (0,1,1,1,2,3,3,3)
  (0,1,1,2,2,2,2,4)
  (1,1,1,1,1,2,3,4)

d=2:
  (0,0,1,1,2,2,3,3)
  (0,1,1,1,1,2,2,4)

d=4:
  (1,1,1,1,1,1,2,2).
```

Their labeled off-diagonal permutation counts are respectively aggregated as

```text
d=0: 2716,   d=2: 3360,   d=4: 28.
```

Since the nine diagonal entries lie in `{0,2,4}` and sum to ten, a simultaneous
orbit relabeling puts the diagonal into exactly one of:

```text
(0,0,0,0,0,0,2,4,4)
(0,0,0,0,0,2,2,2,4)
(0,0,0,0,2,2,2,2,2).
```

## 4. Exhaustive quotient search

For each sorted diagonal case, `exact_search.py` proceeds from row zero through
row eight.

At depth `i`:

1. it generates every permutation of every allowed off-diagonal shape for
   diagonal entry `q_ii`;
2. it keeps exactly the rows whose first `i` entries equal the already chosen
   symmetric entries `q_0i,...,q_(i-1)i`;
3. for every earlier row `j`, it tests the exact off-diagonal equation

   ```text
   sum_k q_ik q_kj + q_ij = 22;
   ```

4. it recurses on every surviving row.

At depth nine, all row-sum, diagonal, symmetry, and off-diagonal equations have
been tested, so each leaf is exactly a quotient candidate.

The primary `unpruned` mode performs no other pruning. Sorting the diagonal is
without loss because it is only a simultaneous permutation of the nine
orbits. The optional `canonical` mode also sorts the exposed column signatures
of still-unassigned vertices within equal-diagonal classes. Its result is a
faster cross-check, not the basis for unpruned completeness.

The sealed result records exact branch counts and a deterministic SHA-256
digest of the explored tree.

## 5. Every order-11 automorphism would be semiregular

Now drop the semiregularity assumption and let an arbitrary nonidentity
order-11 automorphism have `f` fixed vertices. All other vertex orbits have
size 11, so

```text
f = 0 mod 11.
```

For a fixed vertex `i`, its 14 neighbors split into fixed points and 11-cycles.
Its degree `d_i` in the fixed induced graph `F` therefore satisfies

```text
d_i = 14 mod 11,   0 <= d_i <= 14,
```

so `d_i` is either 3 or 14.

For a pair of fixed vertices, their common-neighbor set is invariant and has
size one or two. Since an order-11 orbit cannot fit inside a set of size at
most two, every common neighbor is fixed. Thus adjacent fixed pairs have one
common neighbor in `F`, while nonadjacent fixed pairs have two.

Fix `i` and double-count length-two walks from `i` to a different fixed
vertex. Summing first by the endpoint gives

```text
d_i + 2(f-1-d_i) = 2f-2-d_i.
```

Summing first by the middle neighbor gives

```text
sum_(j adjacent_F i) (d_j-1)
  = sum_(j adjacent_F i) d_j - d_i.
```

Equating them yields the key identity

```text
sum_(j adjacent_F i) d_j = 2f-2.             (*)
```

The positive multiples of 11 are now eliminated exactly:

- If `f=11`, degree 14 is impossible, so every `d_i=3`. The left side of
  `(*)` is `3*3=9`, but the right side is 20.
- If `f=22`, a degree-3 vertex must have all three neighbors of degree 14,
  because `3(3-x)+14x=42` gives `x=3`. A degree-14 vertex has no degree-14
  neighbors, because `3(14-y)+14y=42` gives `y=0`. Hence `F` is bipartite.
  But every fixed edge has its unique common neighbor fixed, producing a
  triangle through that edge, a contradiction.
- If `f>=33`, a degree-3 vertex would make the left side of `(*)` at most
  `3*14=42`, while the right side is at least 64. Hence every degree is 14.
  Then `(*)` becomes `14*14=2f-2`, forcing `f=99`. An automorphism fixing all
  99 vertices is the identity, contrary to the nonidentity hypothesis.

Therefore `f=0`: every nonidentity automorphism of order 11 is semiregular.
The exhaustive quotient obstruction consequently excludes **all** order-11
automorphisms, not just a pre-assumed fixed-point-free action.

If a target were vertex-transitive, orbit-stabilizer would imply that its
automorphism-group order is divisible by 99. Cauchy's theorem would give an
element of order 11, which has just been excluded. Thus a target, if it
exists, cannot be vertex-transitive.

## 6. Why no `Z_11` voltage search remains

Had a quotient survived, a block-circulant lift would choose subsets
`D_ij subset Z_11` satisfying

```text
|D_ij| = q_ij,
D_ji = -D_ij,
0 notin D_ii,
D_ii = -D_ii.
```

For `zeta` an 11th root of unity, define the Hermitian character matrix

```text
(M_t)_ij = sum_(d in D_ij) zeta^(t d).
```

The zero frequency is `M_0=Q`. At every nonzero frequency the all-ones term
vanishes, so the lift equation becomes

```text
M_t^2 + M_t = 12 I.
```

An empty exhaustive quotient set therefore makes the exact lift set empty
before voltage variables are introduced.

## 7. Independent Cayley obstruction

First audit the group-theoretic premise. Sylow's theorem gives

```text
n_11 divides 9,   n_11 = 1 mod 11,
```

so the Sylow-11 subgroup `N` is unique and normal. Let `P` be a Sylow-3
subgroup of order nine. Conjugation by `P` on `N=C_11` has image whose order
divides both `9` and `|Aut(C_11)|=10`; hence the action is trivial. Also every
group of order `3^2` is abelian. Since `G=NP` and the two factors commute,
every group of order 99 is abelian, with type

```text
C_99  or  C_3 x C_3 x C_11.
```

Now suppose a Cayley graph on such a group has an inverse-closed connection
set `D` of size 14. Abelian characters diagonalize its adjacency matrix. The
principal character has value 14; among the 98 nonprincipal characters,
exactly 54 have connection-set sum `3` and 44 have sum `-4`.

Let `X` be the 54 characters of value `3`, and for nonidentity `g` set

```text
S_X(g) = sum_(chi in X) conjugate(chi(g)).
```

The sum of all nonprincipal character values at nonidentity `g` is `-1`.
Fourier inversion therefore gives

```text
99 * 1_D(g)
  = 14 + 3 S_X(g) - 4(-1-S_X(g))
  = 18 + 7 S_X(g).
```

Thus

```text
S_X(g) = -18/7   if g is not in D,
S_X(g) =  81/7   if g is in D.
```

But `S_X(g)` is a sum of roots of unity, hence an algebraic integer. Both
displayed values are rational nonintegers, while every rational algebraic
integer is an integer. This contradiction excludes the Cayley scope.

## Scope boundary

The fixed-point lemma and quotient obstruction together exclude all order-11
symmetry and hence all vertex-transitive realizations. The Fourier obstruction
independently excludes Cayley realizations. None of these arguments excludes
an asymmetric target or one whose automorphism group has order prime to 11.
The unrestricted Conway-99 problem remains `UNKNOWN`.
