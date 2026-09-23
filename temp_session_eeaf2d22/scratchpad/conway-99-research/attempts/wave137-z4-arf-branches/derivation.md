# Signed Krawtchouk derivation

Let `R=im_F2(A)`, with `dim R=54`, and define on the even-weight ambient
space

```text
q(x)=wt(x)/2 mod 2.
```

The restriction to `R` is nondegenerate. Its Gauss sum therefore has one of
two signs:

```text
G_R = sum_(x in R) (-1)^q(x) = epsilon*2^27.
```

For the ordinary image weight enumerator this is

```text
G_R = sum_(w even) (-1)^(w/2) A_w.
```

For a vertex subset `T` of size `t`, put `a_T=A 1_T`. Exact graph algebra
gives

```text
q(a_T)=t+e(T) mod 2,
a_T dot x = 1_T dot x.
```

Summing the quadratic character after translating by all `a_T` gives

```text
M_t = sum_(w even) (-1)^(w/2) K_t(w) A_w = S_t G_R,
```

where `K_t` is the standard length-99 binary Krawtchouk polynomial and

```text
S_t = sum_(|T|=t) (-1)^(t+e(T)).
```

The independently supplied exact constants used here are

```text
S_0 = 1
S_1 = -99
S_2 = 3465
S_3 = -56595
S_4 = 462924
S_5 = -1821204.
```

The implemented K1 equation

```text
sum_(w even) (-1)^(w/2) (99-w) A_w = 0
```

is equivalent, after using `M_0=G_R`, to `M_1=-99 G_R`.

Ordinary MacWilliams also gives the exact redundant relation

```text
G_E=-G_R/32.
```

For `t>=6`, the rational shadow layer uses only

```text
|M_t| <= 2^27 binom(99,t).
```

No modular divisibility or parity assertion is inferred from these rational
inequalities.
