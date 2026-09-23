# Source-blind Wave203 two-center incidence protocol

## Frozen target

Work conditionally inside the independently verified prism-free rank-11
endpoint framework.  For a selected exact-three label `e={x,y}`, let
`m_(x->y)` and `m_(y->x)` count selected exact-three flags in its two
orientations.  Independently verify or refute

```text
m_(x->y)+m_(y->x)<=5.                            (T)
```

The proof may use exact local incidence geometry and already verified
relation/Gram theorems.  It must not enumerate graphs, flag families,
configurations, covers, or isomorphism classes.

## Premises to re-audit

1. `G` has parameters `srg(99,14,1,2)` and is prism-free.
2. The seven triangle blocks through a vertex form its local star.
3. A canonical exact-three flag `(x,T)` has `x` anticomplete to the
   triangle `T` and the globally normalized relation

   ```text
   z_T+2*sum_(R in A_x(T)) z_R=0, |A_x(T)|=3.
   ```

4. For fixed `x`, distinct flags have distinct `A_x` sets.
5. For a nonedge `xy`, its two common neighbors determine two fixed
   blocks in each endpoint star and five remaining blocks.
6. On the four canonical quadrilateral blocks, the centered Gram has
   projective kernel `(1,2,2,1)`, not the all-equal word.

## Required independent checks

1. **Five-slot injection.**  Map an `x->y` flag to the unique member of
   `A_x(T)` outside the two fixed `xy`-type blocks.  Prove that it is one
   of the five remaining `x`-star blocks and that this map is injective.
2. **Shared slot convention.**  Map a `y->x` flag to its leaf triangle,
   which is also one of the same five remaining `x`-star blocks.
3. **Reverse matching.**  If an `x->y` flag and a `y->x` flag use the
   same slot `S`, prove that the former leaf block `T` is the reverse
   flag's third `A_y(S)` block.
4. **Sign audit.**  Use the globally fixed column representatives and
   the exact coefficient `2` in both flag relations.  Do not infer the
   cancellation from projective supports alone.
5. **Distinctness and Gram audit.**  Show that the four surviving
   endpoint-star columns are distinct canonical-C4 columns; compute the
   Gram images of the checkerboard and all-equal words over `F_3`.
6. **Counting consequences.**  Derive only what follows:

   ```text
   3n3+4p3<=5|U|,
   epsilon>=5b,
   ```

   where `U` is the selected exact-three label union and `b` counts its
   bidirectionally occupied labels.
7. **Promotion guard.**  Do not claim `Q>=7060` or any stronger endpoint
   bound unless an independent positive lower bound on `b` is proved.

## Separation

The Wave203 source directories
`attempts/wave203-two-center-incidence-proof-b/` and
`attempts/wave203-two-center-incidence-proof-a-audit/`, together with
their agent reports, remain unopened until the independent mathematical
result, checker, tests, and their hash freeze are written.  The expected
sealed source manifest hashes supplied by the orchestrator are

```text
primary: b412cce1a737b3b50718aabb399978ca2956cea0edbbe1c1f955f8083447d5b8
hostile: 62019dec2c954b2354279afd4dc114daffafbef0bff3678ddca2fcb61cb1edb8
```

## Status boundary

Even if (T) is verified, rank 11, endpoint existence, strict improvement
of the current `Q>=7059` bound, Conway-99, and external novelty remain
`UNKNOWN` unless separately established.
