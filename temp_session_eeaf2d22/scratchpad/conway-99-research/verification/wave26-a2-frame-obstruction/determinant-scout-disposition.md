# Disposition of the proposed determinant strengthening

The proposed continuous-relaxation bound

```text
det(B) <= 5*3^6 = 3645
```

remains **UNKNOWN**.  No exact relaxation counterexample and no global proof
was obtained before the scout was stopped.  Numerical optimizer output is
not retained as evidence and is not a claim.

One exact partial reduction was obtained for spectra whose nonzero
\(\mu\)-values are all positive.  From

```text
sum mu = 8,
product mu >= 1,
```

AM--GM gives at most eight nonzero values.  Rank eight would force every
\(\mu=1\), contradicting the strengthened premise
\(\sum\mu^2\ge10\); hence the positive-only rank is at most seven.  For ranks
at most six, concavity of \(\log(1+2\mu)\) gives

```text
det(B) <= (1+16/r)^r <= (11/3)^6 < 3645.
```

The rank-seven positive case and all mixed-sign cases were not resolved.
Accordingly, this partial observation is not a Wave 26 determinant theorem.
