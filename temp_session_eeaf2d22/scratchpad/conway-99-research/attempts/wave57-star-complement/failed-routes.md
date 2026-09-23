# Failed routes and retained boundaries

## 1. The quotient spectrum is not a contradiction

The quotient has the global nontrivial eigenvalues `3` and `-4`, as expected.
Its useful content is the two-dimensional supported sector for each eigenvalue.
It does not exclude the endpoint.

## 2. The supported sectors do not force a canonical star complement

They prove that every relevant star set must hit `U=T union X`, and the
projector ranks quantify the exact minimum hit.  They do not determine which
vertices occur.  No automorphism is available to normalize those choices.

## 3. Moment localizers stop at 18 cases

The order-three localizers force `18<=mult_Y(3)<=20` and
`8<=mult_Y(-4)<=13`.  The order-four constraints sharpen the allowed
four-cycle count, but every multiplicity pair retains at least 25 possible
integer values of `C4(X)`.

## 4. Algebraic integrality supplies controls, not graphs

Sixteen rows have all-integer residual spectral controls.  The two remaining
rows have controls using conjugate roots of monic integral quadratics.
Therefore a contradiction based only on the first four moments, interval
support, and algebraic integrality cannot work.  No control is claimed to be
the spectrum of an 8-regular graph.

## 5. The Reconstruction Theorem is not self-executing

Writing

```
mu I-A_S = B^T (mu I-C)^(-1) B
```

reduces reconstruction to exact binary compatibility, but neither the
star-complement graph `C` nor the incidence matrix `B` is known.  Matrix rank
and solver exit codes without complete candidate data would not be
certificates.

## 6. Next exact target

Work on `Y`, not on an assumed symmetric 99-vertex model:

1. enumerate or constrain 8-regular 60-vertex graphs with 32 triangles and
   `C4(Y)=171+C4(X)`;
2. impose nullities `mult_Y(3)=a` and `mult_Y(-4)=b` for one of the 18
   ledger rows;
3. choose a 40-to-42 vertex `3`-star complement or a 47-to-52 vertex
   `-4`-star complement inside `Y`;
4. solve the Reconstruction Theorem over binary neighbourhood columns;
5. emit a complete graph certificate or a complete proof-producing
   exhaustion.

Until such a certificate is independently checked, both the endpoint and
Conway-99 remain `UNKNOWN`.
