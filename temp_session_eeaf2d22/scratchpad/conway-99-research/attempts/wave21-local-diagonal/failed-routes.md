# Wave 21 local-diagonal retained failures

## Scalar diagonal contradiction does not close

At `n3=705`, `tr(A4)=1008`, so the 231 positive diagonals divisible by four
have only 21 excess units above the all-four floor.  The local tensor bound

```text
(A4)[T,T] >= (99/43)*(q(T)-2)^2
```

is strong enough to force `q<=8`, but not to exhaust those units.  A scalar
witness is:

```text
223 q=2, 8 q=3;
210 diagonals 4, 21 diagonals 8.
```

This witness is not a matrix or graph construction.  It only refutes the
claim that the displayed scalar conditions are already inconsistent.

## Harmonic cubic is locally sharp but globally superseded

The PSD harmonic kernel

```text
H=23*(M o M o M)-24*M
```

forces `q<=10` at the endpoint.  Centering its all-ones direction shows that
two `q=10` indices are impossible.  The `A4` local tensor/trace argument
already forces `q<=8`, so this route did not improve the endpoint.

## Frobenius congruence remains feasible

Exact matrix algebra and parity give

```text
tr(A4^2)=441*t,  t=4 (mod 8),  t>=60.
```

The resulting lower bound `tr(A4^2)>=26460` does not contradict positivity,
rank 44, and trace 1008.  A scalar spectral witness has 22 copies of each of

```text
(252+21*sqrt(21))/11,
(252-21*sqrt(21))/11.
```

No integral matrix with these data is asserted.

## No universal individual mod-eight diagonal was proved

Writing `W=M+2D` gives

```text
A4=M^3+2MDM.
```

The Wave 20 alternating-form argument evaluates each diagonal modulo four.
Modulo eight, the remaining quadratic form depends on pair data within the
odd support of the anchored row.  Those pair counts are not fixed by
`q(T)`, the row profile, or `M^2=21M` alone.  The route was stopped rather
than silently assuming that `W` commutes with `M` or belongs to an
association algebra.

## Missing bridge

A stronger endpoint attack must control off-diagonal or pair-incidence data
inside `A4`, or add a genuinely new positive kernel.  The current scalar
relaxations do not enforce the full identities `A4 M=21A4`, the prescribed
parity matrix, or global matrix realizability.
