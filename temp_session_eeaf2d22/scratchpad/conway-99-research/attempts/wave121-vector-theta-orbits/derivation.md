# Exact derivation

Claim label: `DERIVED`.

Everything is conditional on the frozen verified Wave 66/80/86/97/101
imports and a hypothetical `srg(99,14,1,2)`. No automorphism is assumed.

## 1. Frozen rank-30 setting

Use the Wave 101 row

```text
q=14, r=44-q=30,
det(L)=7^14,
K=sqrt(7)L*,
det(K)=7^30,
min(K)>=14.
```

Write

```text
Theta_K = sum x_n q^n,
Theta_L = sum y_n q^n,
```

where the exponent is half the squared norm. Wave 101 gives a complete
15-dimensional scalar modular parameterization, with `x14` eliminated by
`y0=1` and seven remaining variables `x7,...,x13`.

Wave 80 identifies

```text
D_L=L*/L = O^-(14,7).
```

The lattice `K` is even, elementary level seven, and has discriminant
length 30. Its signature is 44, so Milgram's normalized Gauss phase is
`-1`. In dimension 30 over `F7`, this forces determinant Legendre sign
`+1`; the split sign would be `(-1)^15=-1`. Therefore

```text
D_K=K*/K = O^-(30,7).
```

For an even-dimensional minus space of dimension `2m` over `F7`, the exact
quadratic-value orbit sizes are

```text
Q=0, including zero:       7^(2m-1) - 6*7^(m-1)
Q=a for each nonzero a:    7^(2m-1) + 7^(m-1).
```

The script checks that zero, nonzero isotropic, and all six nonzero-value
orbits sum to `7^(2m)`.

## 2. What orbit reduction is justified

It is not justified to assert that individual coset theta components are
equal merely because their discriminant classes lie in one abstract
orthogonal orbit. An isometry of a finite discriminant form need not lift
to an automorphism of the lattice, much less the graph.

What is always justified is summing components over a complete exact-value
orbit. The full orthogonal group preserves the exact quadratic value, not
only its square class. Accordingly the model retains eight aggregates:

```text
{0}, nonzero Q=0, and Q=a for each a=1,...,6.
```

Wave 97's projective reduction is not used: it would merge some square
values and erase the distinct Wave 80 coordinate compositions at norms
14, 16, and 18.

## 3. The two nonzero-isotropic coefficient families

### The `L*/L` quotient

Every `z in K` can be written `z=sqrt(7)y` with `y in L*`. Its class
`y+L` lies in `D_L`, and

```text
q_L(y) = (y,y)/2 = (z,z)/14 mod Z.
```

If `z` contributes to `x_n`, then `(z,z)=2n`, so its exact quadratic value
is `n mod 7`. The zero class is `y in L`, whose scaled theta series is

```text
Theta_(sqrt(7)L)(tau) = Theta_L(7 tau).
```

At exponent `7m`, the total isotropic coefficient is `x_(7m)` and its zero
class contributes `y_m`. Hence the nonzero-isotropic aggregate is exactly

```text
x_(7m)-y_m >= 0.                         (1)
```

Through the scalar Sturm variables this supplies `x7-y1>=0` and
`x14-y2>=0`.

### The `K*/K` quotient

Now `K*=(1/sqrt(7))L`. If `w=l/sqrt(7)`, its exponent is one seventh of
the exponent of `l in L`, and

```text
Theta_(K*)(tau) = Theta_L(tau/7).
```

At an integer exponent `n`, the total isotropic coefficient is `y_(7n)`.
The zero class `w in K` contributes `x_n`. Thus

```text
y_(7n)-x_n >= 0.                         (2)
```

The package checks (2) for `1<=n<=11`, requiring exact `Theta_L`
coefficients through `y77`.

For nonzero quadratic values, the orbit aggregate is simply the appropriate
residue dissection of `Theta_K` or `Theta_L(tau/7)`. Its nonnegativity is
ordinary scalar coefficient nonnegativity. Therefore (1) and (2) are the
only new inequalities in this full-orthogonal aggregate.

## 4. Exact seven-variable feasibility model

The Wave 86 product basis is regenerated exactly through degree 77. The
Wave 101 Fricke relation

```text
Theta_L = -7^4 (Theta_K | W_7)
```

then expresses every tested coefficient as an affine rational form in

```text
z=(x7,x8,x9,x10,x11,x12,x13).
```

The finite cone uses:

```text
x7,...,x14 >= 0
y1,...,y77 >= 0
x7-y1 >= 0
x14-y2 >= 0
y_(7n)-x_n >= 0, 1<=n<=11.
```

For an actual lattice all displayed nonconstant coefficients and orbit
differences are nonnegative even integers. Rational feasibility is kept
separate from that integral refinement.

## 5. The norm-20 and norm-22 optima do not move

Adding inequalities can only raise a Wave 101 minimum. Conversely, the
package substitutes the independently verified Wave 101 exact minimizers
and checks every new inequality through `y77`.

Both remain feasible. Therefore the strengthened cone has the same exact
optima:

```text
x7+...+x10 >= 389888/57
x7+...+x11 >= 4675706896/9307.
```

Parity of actual theta coefficients gives the same lattice bounds as Wave
101:

```text
x7+...+x10 >= 6842
x7+...+x11 >= 502388.
```

This is a rigorous null result for the abstract orbit refinement: it adds
valid information but does not strengthen these two objectives.

## 6. Conditional forcing beyond norm 18

Impose the formally feasible case

```text
x7=x8=x9=0.
```

Direct exact elimination in the four remaining free coordinates gives

```text
x10 - 2729216
 = 440363*y1 + 32536*y2 + 1715*y3 + 49*y4.       (3)
```

All multipliers and theta coefficients on the right are nonnegative, so

```text
x10 >= 2729216.
```

The bound is attained by the exact even-integral prefix

```text
(x7,...,x14)
=(0,0,0,2729216,9904496,64688008,374547488,1753425792).
```

Every `x`, `y1,...,y77`, and orbit-difference coefficient checked for this
control is a nonnegative even integer. This is still only a formal prefix,
not a lattice.

A second exact identity is

```text
x10+x11 - 4144144
 = (6/7)*x11 + 280574*y1 + 13377*y2 + 343*y3.    (4)
```

Thus

```text
x10+x11 >= 4144144.
```

The rational cone attains equality, but its `y` coefficients include
denominators 7 and 49. Equation (4) is therefore not rounded or presented
as the exact integer optimum.

## 7. Abstract code upper boundary

Wave 80 gives a `[99,44]_7` evaluation code `C` with radical

```text
R=row_F7(S), dim R=30,
```

and nondegenerate quotient `C/R=O^-(14,7)`. Every exact nonzero quadratic
value in the quotient has

```text
7^13+7^6
```

classes, each with `7^30` codeword lifts through the radical. Consequently
the total number of codewords of either fixed anisotropic value is

```text
7^30 (7^13+7^6).                          (5)
```

For two distinct `K` vectors of norm at most 22 to have the same evaluation
word, their difference would lie in `7K`. A nonzero such difference has
norm at least `49*14=686`, while the triangle inequality bounds the
difference norm by at most `88`. Thus evaluation is injective on this
short range, and (5) is a rigorous shell upper bound after selecting the
appropriate exact self-dot value.

Norm 20 has code self-dot `2*20=5 mod 7`; norm 22 has self-dot
`2*22=2 mod 7`. The same numerical upper applies to both and is vastly
above the lower bounds.

The quotient does not determine the Hamming or signed-coordinate
composition at either norm. Those compositions remain explicitly
`UNKNOWN_UNDER_FROZEN_INPUTS`.

## 8. Exact boundary

The alternative space yields an exact, compact orbit dictionary and two
conditional forcing identities, but also a complete finite null control:

```text
rank-30 row excluded:                 no
upper/lower contradiction:           no
formal even-integral prefix feasible: yes
graph or lattice constructed:         no
Conway-99:                             UNKNOWN
literature novelty:                   UNKNOWN
```
