# Rank-44 scaled-dual, discriminant-form, and root-glue notes

Access date: `2026-07-24` UTC. Query IDs: `L01-L05`, `D01-D04`.

## The scaled-dual hypothesis is weaker than modularity

The Nebe-Sloane catalogue definition says that an `N`-modular integral
lattice is **similar to its dual** and describes a similarity matrix
carrying the dual to the lattice.  Therefore

```text
21 L* subset L
```

does not by itself make `L` 21-modular or strongly 21-modular.  Results
whose hypotheses require an Atkin-Lehner similarity, rational
equivalence to a specified modular genus, or exact `N`-modularity cannot
be imported into the Wave 28 package from the containment alone.

The rank-44 row in the online modular-lattice table is likewise not a
classification of positive-definite even rank-44 lattices satisfying
the weaker containment and one of

```text
9, 21, 49, 81, 189, 441, 729, 1029.
```

No exact classification covering that frozen package was located in
queries `L01-L05`.

## Standard discriminant-form ingredients located

The primary reference is V. V. Nikulin, *Integral symmetric bilinear
forms and some of their applications*, Math. USSR-Izvestiya 14(1)
(1980), 103-167, DOI
[10.1070/IM1980v014n01ABEH001060](https://doi.org/10.1070/IM1980v014n01ABEH001060).
The following attributions were checked against exact modern
restatements of the numbered results:

- Propositions 1.4.1-1.4.2 give the correspondence between even
  overlattices and isotropic subgroups of the discriminant form, and
  the residual discriminant quotient.
- Proposition 1.6.1 gives opposite discriminant forms for primitive
  orthogonal complements in an even unimodular lattice.
- Corollary 1.9.4 says that signature and discriminant form determine
  the **genus**.  It does not by itself say that a positive-definite
  genus has one isometry class.

For the imported signature-phase theorem, Laurence Taylor's
[Gauss Sums in Algebra and Topology](https://arxiv.org/abs/2208.06319)
gives a modern proof route to the Milgram Gauss-sum formula.  Xiao-Jie
Zhu's
[Finite quadratic modules and lattices](https://arxiv.org/abs/2110.06783)
is a modern source for indecomposable finite-quadratic-module
decomposition and explicit lattice realizations.  These sources support
the standard machinery, not the exact Wave 28 arithmetic census.

The ADE classification, root-string argument, and primitive
overlattice bookkeeping are standard ingredients.  No source was found
that states the exact combined Wave 28 theorem involving all of:

- positive-definite even rank 44;
- `21L* subset L` and the eight determinant rows;
- twelve Milgram-compatible formal 3/7-primary forms;
- the scaled-dual local-sign comparison;
- an index-two single-root complement;
- a primitive ADE root closure with a rootless complement; and
- the marked 231-coordinate projector restrictions.

Accordingly, literature can source the imported theorems, while the
combination and its arithmetic remain `DERIVED`/independently checked
inside the repository rather than `CITED`.

## Mandatory correction from the independent verifier

The correct group-theoretic conclusion from `21A_L=0` is:

```text
the 3-primary and 7-primary components are elementary;
no p-primary cyclic factor has order p^2 or higher;
invariant factors divide 21 and may have order 21.
```

The discovery sentence excluding cyclic order-21 invariant factors is
false because `Z/21` is isomorphic to `Z/3 direct_sum Z/7`.  This prose
correction does not alter the primary decomposition, exact-level table,
Milgram census, or downstream local calculations.

## Status boundary

```text
standard discriminant/glue ingredients: CITED
exact Wave 28 rank-44 application: repository DERIVED/VERIFIED only
realization or exclusion of any determinant row: UNKNOWN
classification under the weak scaled-dual containment: not located
novelty of the exact combination: UNKNOWN
```
