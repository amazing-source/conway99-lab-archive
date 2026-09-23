# Exact derivation of the `b=0` local-incidence skeleton

## 1. Frozen lemma under attack

Wave203 proves for every selected nonprivate unordered label `e={x,y}`

```text
m_(x->y)+m_(y->x)<=5
```

and consequently

```text
3n3+4p3<=5|U|,
epsilon>=5b.
```

The new hostile lemma is deliberately restricted to the information
actually present in this local interface:

> Ninety-nine centers, degree 14 and complement degree 84, a local
> intersecting family of triples on seven blocks at each center, four
> leaf values per block-pair fiber, the Wave201 equality row, and the
> Wave203 five-slot injections force `b>0`.

The certificate refutes that statement. It does not address a theorem
that additionally uses actual SRG common-neighbor equations, globally
identified triangle columns, canonical ternary relations, or rank 11.

## 2. A 99-center degree skeleton

Use `Z/99Z`. Join `x` to `x+-d` for `1<=d<=7`. This is a simple
14-regular circulant, hence its complement is 84-regular.

Orient every complement edge by

```text
x -> x+d,  8<=d<=49 mod 99.
```

Exactly one orientation is chosen for each complement edge, and each
vertex has 42 outgoing complement neighbors. The construction will use
at most 36, so no reverse label is ever needed.

The graph is only a degree skeleton. For example, from vertex zero its
adjacent vertices have 6,7,...,12 common neighbors, two at each value.
It is therefore not `srg(99,14,1,2)`.

## 3. The local family

At every center use the Hilton--Milner family

```text
H = {{1,2,3}}
    union {{0,a,b}: {a,b} subset {1,...,6},
                       {a,b} intersects {1,2,3}}.
```

It has 13 distinct triples, is pairwise intersecting, and has empty total
intersection. Its 39 pair incidences have exactly three degree-five
pairs:

```text
{0,1}, {0,2}, {0,3}.
```

Every other pair has degree at most four. A degree-five fiber is
partitioned into four labels by repeating one label. In three specified
fibers the repeated label has multiplicity three, so that fiber has
three distinct labels. This is the only extra full-pool loss.

The 21 pair fibers are then completed, exactly and disjointly, to four
of the 84 complement neighbors apiece. This declared partition is part
of the relaxation and is not asserted to be induced by the circulant's
common-neighbor geometry.

## 4. Selected flags and repeated labels

Centers `0,...,78` select all 13 flags. The remaining centers select

```text
13 centers * 9 flags + 7 centers * 8 flags = 173 flags,
```

so the total is

```text
79*13+173=1200.
```

At each of the first 79 centers, one selected repeated label is placed
in each degree-five fiber. At centers 0,1,2 the `{0,1}` label has
multiplicity three; the other 234 repeated labels have multiplicity
two. Thus:

```text
q=79*3=237,
profile(nonprivate)=2^234 3^3.
```

At the other 20 centers the selected subfamily has degree at most four
on every degree-five pair. Its full-family repeat uses at most one
selected occurrence, so every selected label at those centers is
private.

There are `3*1200=3600` selected incidences. Repetition saves

```text
234*(2-1)+3*(3-1)=240
```

labels, giving

```text
|U|=3600-240=3360,
p3=3360-237=3123.
```

The orientation deficit is

```text
epsilon=234*(5-2)+3*(5-3)=708.
```

## 5. Full-pool equality and slots

The ordinary degree-five repeat saves one full leaf value in each of
the `99*3=297` baseline fibers. The three multiplicity-three groups save
one additional value apiece. Therefore

```text
J=99*39-297-3=3561,
delta=3564-J=3.
```

The Wave201 equality slack is exactly

```text
L=delta-3q+epsilon
 =3-3*237+708
 =0.
```

For one leaf label of pair type `P` in a flag with triple `A`, its
Wave203 slot is the unique block in `A-P`. Repeated occurrences use
distinct triples and hence distinct slots among the five blocks outside
`P`. The largest full multiplicity is three. Since the global complement
orientation forbids every reverse occupancy,

```text
m_full(x->y)+m_full(y->x)<=3<=5.
```

The selected capacity row has exact slack

```text
5|U|-(3n3+4p3)
 =5*3360-(3*1200+4*3123)
 =708
 =epsilon.
```

Thus every stated local/fiber/slot equation holds while `b=0`.

## 6. Cohomology boundary

The certificate supplies a global orientation section: every used label
follows the fixed circulant complement orientation. Wave203 supplies only
partial slot maps for flags that exist. With `b=0`, it supplies no matched
reverse transition from which a nontrivial group-valued gain or monodromy
could be derived.

Consequently:

- `b=0` is not itself a failure of global orientation;
- partial injections are not transition isomorphisms;
- a gain, signed-matroid, or sheaf obstruction needs an additional
  transition rule derived from the ternary columns;
- assigning gains merely to fit a desired contradiction would add an
  unproved hypothesis.

This underdetermination is the boundary exposed by the countermodel.
