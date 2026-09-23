# Compact two-center derivation

For a nonedge `xy`, the two common neighbors occupy two distinct
`x`-star blocks and two distinct `y`-star blocks. The remaining five
blocks on each side are anticomplete to the opposite center.

An `x->y` flag with leaf block `T` has

```text
A_x(T)={X_a,X_b,S}.
```

Fixed-center flag injectivity makes `T->S` an injective partial map into
the five opposite slots. Reverse flags use their leaf block in that same
five-slot set. The leaf-type 6-cycle gives `j(S,T)=2`.

If a reverse `y->x` flag used leaf block `S`, then

```text
A_y(S)={Y_a,Y_b,T}.
```

The four common-neighbor triangle columns are pairwise distinct. Both
canonical relations use the same globally frozen columns and are
normalized with leaf coefficient one. Adding them would force

```text
z_Xa+z_Xb+z_Ya+z_Yb=0.
```

The verified canonical quadrilateral Gram has nonzero image on the
all-equal word, so this is impossible. Hence the forward images and
reverse domains are disjoint subsets of five slots:

```text
m_(x->y)+m_(y->x)<=5.
```

Thus `3n3+4p3<=5|U|`. If both selected orientations of one nonprivate
label are occupied, their Wave198 deficit is

```text
(5-m_x)+(5-m_y)=10-(m_x+m_y)>=5.
```

No extra circuit, private label, or local fiber repetition follows from
this slot argument alone.
