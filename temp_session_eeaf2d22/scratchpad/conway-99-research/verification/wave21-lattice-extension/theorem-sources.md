# Theorem-source note for the Wave 21 lattice audit

Accessed in UTC on 2026-07-23.

## Even-unimodular signature obstruction

The imported theorem needed by the submission is:

> The signature of an even unimodular integral symmetric form is divisible
> by eight.

Primary bibliographic attribution:

- F. van der Blij, *An invariant of quadratic forms mod 8*, Proceedings of
  the Koninklijke Nederlandse Akademie van Wetenschappen, Series A 62
  (also *Indagationes Mathematicae* 21), 291--293 (1959).

Stable expositions checked:

- Jean-Pierre Serre, *Formes bilinéaires symétriques entières à
  discriminant ± 1*, Séminaire Henri Cartan 14 (1961--1962), exposés 14--15,
  pp. 1--16:
  <https://www.numdam.org/item/SHC_1961-1962__14__A9_0/>.
- Stanislav Jabuka, *The signature of an even symmetric form with vanishing
  associated linking form*, Theorem 1.1:
  <https://arxiv.org/abs/1204.4965>.

The application here is exact.  If `det(Q)=1`, the free group `Z^44` with
Gram matrix `Q` is an integral unimodular lattice.  Its quadratic norms are
even, and positive definiteness gives signature `44`.  Van der Blij's lemma
may be applied with characteristic vector zero: evenness makes zero
characteristic, so the lemma would give `44 = 0 (mod 8)`, which is false.
Thus `det(Q)` cannot equal one.

No classification of even unimodular lattices, root-system assumption, or
minimum-norm hypothesis is needed.

## Additional elementary determinant congruence

The verifier also used the following elementary consequence, for which no
external theorem is needed:

> If an even integral symmetric matrix has rank `2m` and odd determinant,
> then its determinant is `(-1)^m (mod 4)`.

Indeed, its reduction modulo two is a nonsingular alternating form.  Lift a
symplectic change of basis to an integral unimodular matrix.  Modulo four the
Gram matrix then has the form `J+2R`, where `J` is a direct sum of `m`
hyperbolic two-by-two blocks and `R` is symmetric.  Hence

```text
det(J+2R)
  = det(J) det(I+2JR)
  = (-1)^m (1+2 tr(JR))  (mod 4).
```

Because `J` has paired off-diagonal ones and `R` is symmetric, `tr(JR)` is
even.  The claimed residue follows.  At rank 44 this residue is one.
