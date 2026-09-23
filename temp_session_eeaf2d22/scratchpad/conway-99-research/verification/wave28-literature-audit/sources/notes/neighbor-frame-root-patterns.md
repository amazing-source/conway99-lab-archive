# Neighbor, marked-frame, and root-image notes

Access date: `2026-07-24` UTC. Query IDs: `N01-N05`, `F01-F05`,
`R01-R04`.

## Standard one-lattice neighbor theory

The ordinary Kneser neighbor method is well represented in the
literature:

- John Voight,
  [Kneser's method of neighbors](https://jvoight.github.io/articles/kneser-033024.pdf)
  (survey dated 2024-04-30), Definition 3.10 defines a `p`-neighbor by
  equal index-`p` intersections.  Lemma 3.12, Proposition 3.13, and
  Theorem 3.18 give same-discriminant/genus, explicit-construction, and
  connectivity statements with their stated hypotheses.
- Gabriele Nebe,
  [Quadratic Forms](https://www.math.rwth-aachen.de/~Gabriele.Nebe/SummerSchool2023/QFVorl.pdf),
  Definition 14.31 and Theorem 14.32, gives the same standard
  one-lattice framework.
- Jacques Martinet,
  [On Parity Classes](https://jamartin.perso.math.cnrs.fr/Othertexts/paritylat.pdf),
  supplies index-two/parity bookkeeping and an explicit two-neighbor
  construction.

These sources justify the imported neighbor idea.  They do not state
the exact Wave 28 claim that one rational basis change acts
simultaneously on a tuple of paired forms and auxiliary matrices while
preserving a scaled-dual/endomorphism package.  Searches using
`simultaneous`, `paired quadratic forms`, `contragredient`, and
`scaled-dual endomorphism` found standard one-lattice neighbors, Hecke
neighbor operators, or unrelated uses of “neighbor,” but no direct
match to the frozen tuple.

The congruence identities for changing several matrices by the same
basis are elementary algebra.  Their exact integrality and endpoint
preservation in the frozen package remain repository arithmetic, not a
located literature theorem.

## Tight frames, projectors, and lattice shells

Nearby standard ingredients were located:

- Marcus Appleby, Ingemar Bengtsson, Steven Flammia, and Dardo
  Goyeneche,
  [Tight Frames, Hadamard Matrices and Zauner's Conjecture](https://arxiv.org/abs/1903.06721),
  relates projectors, Hadamard matrices, and equiangular tight frames
  in a SIC-specific setting.
- Claude Pache,
  [Shells of selfdual lattices viewed as spherical designs](https://arxiv.org/abs/math/0502313),
  uses theta series to study **complete** lattice shells as spherical
  designs.

Neither source treats the exact real integral package

```text
231 selected norm-4 vectors in rank 44
tight-frame/projector identity
Gram alphabet {0,+/-1,-2}
Schur-square equation
oriented cubic tensor with squared norm 60
```

The distinction between a complete antipodal shell and a selected
orientation of 231 antipodal pairs is essential.  Odd moments of a full
antipodal shell cancel automatically; that fact does not certify the
Wave 28 marked cubic tensor.

## Exact `46 -> 32` root-image pattern

The frozen searches used exact counts and structural paraphrases:

```text
"root image" "231" lattice
"squared norm 42" "231" lattice root
"46 patterns" "32 patterns" lattice
"sum" "norm 42" "cubic energy" root projection
```

No direct source was found for the reduction of 46 coordinate-count
patterns to 32 using the displayed cubic-energy bound.  This is an
exact finite arithmetic result in the repository's Wave 28 proof and
independent verifier artifacts.  It is not converted into a cited
prior result, a vector realization, or a novelty claim by this search.

## Status boundary

```text
ordinary one-lattice Kneser neighbor theory: CITED
generic tight-frame/projector and full-shell design ingredients: CITED
exact simultaneous paired-form neighbor package: no direct match found
exact 231-vector marked frame/Schur/cubic package: no direct match found
exact 46-to-32 root-image pattern result: no direct match found
novelty of any exact combination: UNKNOWN
```
