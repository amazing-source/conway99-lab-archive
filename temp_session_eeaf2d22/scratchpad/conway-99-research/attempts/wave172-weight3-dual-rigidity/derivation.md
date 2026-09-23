# Derivation

## 1. Frozen endpoint data

At `P=0`, let `C` be the verified integral reflection on the 231 triangle
blocks and put `D=C+J` over `F_3`.  The required facts are

```text
C^2=441I,
C*1=-21*1,
C_ii=-13,
C_ij in {-2,0,2} for i!=j.
```

For distinct blocks, `C_ij=+2,0,-2` means respectively:

```text
disjoint with 0 cross edges,
intersecting or disjoint with 1 cross edge,
disjoint with 2 cross edges.
```

Wave 171 verifies that `W=row(D)` is the centered ternary code.

## 2. A weight-three kernel word is pairwise orthogonal

Let `y` have support `{i,j,k}`, with nonzero coefficients `a,b,c`, and assume
`D*y=0`.  Since `D` is symmetric with zero diagonal, the three support
coordinates give

```text
b*D_ij+c*D_ik=0,
a*D_ij+c*D_jk=0,
a*D_ik+b*D_jk=0.
```

Eliminating the three nonzero coefficients over `F_3` gives

```text
D_ij=D_ik=D_jk=0.                                 (1)
```

Thus each of the corresponding off-diagonal entries of `C` is congruent to
`-1=2` modulo three.  At the endpoint the only available integer value with
that residue is `+2`.  Hence all three block pairs are disjoint and have zero
cross edges.  Their nine points induce `3K3`.

Up to scaling and permuting coordinates, the coefficient vector has one of
two types:

```text
(1,1,1) or (1,1,-1).
```

## 3. The mixed type is impossible

Suppose `D_i+D_j-D_k=0` over `F_3` and put

```text
S=C_i+C_j-C_k.
```

The row relation gives `S=-1 mod 3`.  By (1), the coordinates `i,j,k` of
`S` are

```text
-13, -13, 17.
```

At any of the other 228 coordinates, `S` is an even integer between `-6`
and `6`, congruent to `-1` modulo three.  It is therefore either `-4` or
`2`.  If `m` coordinates have value `-4`, the exact row sum

```text
S*1=-21
```

gives

```text
-13-13+17-4m+2(228-m)=-21,
m=78.
```

The coordinate calculation would then give

```text
S*S
 =13^2+13^2+17^2+78*4^2+150*2^2
 =2475.
```

But distinct rows of `C` are orthogonal and have squared norm 441, so

```text
S*S=3*441=1323,
```

a contradiction.  Mixed coefficient types do not occur.

## 4. Joint composition of the surviving type

Now suppose `D_i+D_j+D_k=0` and put `S=C_i+C_j+C_k`.  The three support
coordinates of `S` are all `-9`.  Every other coordinate is an even multiple
of three between `-6` and `6`, hence lies in `{-6,0,6}`.

Let `m_-`, `m_0`, and `m_+` count these three values outside the support.
The row sum and norm give

```text
-27-6*m_-+6*m_+=-63,
3*9^2+36*(m_-+m_+)=3*441.
```

Therefore

```text
m_-=18,
m_+=12,
m_0=198.                                          (2)
```

Since `D=C+J`, the three support positions and the twelve `S=6` positions
are joint symbol `000`; the eighteen `S=-6` positions are `222`.  At an
`S=0` position the joint symbol is either `111` or a permutation of `012`.

Each row of `D` has composition

```text
(0^33,1^162,2^36).
```

Let `u` be the number of `111` positions and `v` the aggregate number of
permutations of `012`.  From (2),

```text
u+v=198.
```

The total number of symbol ones across the three rows is `3*162=486`, while
the `111` and permutation cells contribute `3u+v`.  Thus

```text
3u+v=486,
u=144,
v=54.
```

Together with the support positions this proves

```text
000: 15,
111: 144,
222: 18,
permutations of 012: 54.
```

## Boundary

The theorem is a marked complete-weight constraint.  It neither counts the
number of weight-three dual words nor shows that such a word exists.  The
ordinary Wave 54 enumerator is only one formal distribution and cannot be
contradicted merely by refining one of its possible dual coefficients.
