# Imported-theorem applicability for Wave 23

The only imported lattice theorem used by the endpoint closure is the
even-unimodular signature obstruction already audited in Wave 21:

```text
the signature of an even unimodular integral symmetric form
is divisible by eight.
```

Its bibliography and stable source links are frozen in:

```text
verification/wave21-lattice-extension/theorem-sources.md
sha256 7f70a36ad124a94d983771274cb7b925a4f2560d835b0f607563045110107f8f
```

The Wave 23 application has all required hypotheses.  If `h=1`, then the
already proved inclusion `21L* subset L` is equality.  For an integral basis
matrix `X` of `L`, with `G=X^T X`, dual-lattice coordinates give

```text
21G^{-1} Z^44 = Z^44.
```

Thus `21G^{-1}` is integral and unimodular, and its inverse `G/21` is also
integral and unimodular.  It is symmetric and positive definite.  Since `G`
is even and 21 is odd, every diagonal entry of `G/21` is even.  Therefore
`G/21` defines an even positive-definite unimodular integral lattice of
rank and signature 44.  The signature theorem would require
`44=0 (mod 8)`, a contradiction.

No root-system classification, minimum-norm premise, integral embedding of
the rescaled lattice, or unproved converse is used.
