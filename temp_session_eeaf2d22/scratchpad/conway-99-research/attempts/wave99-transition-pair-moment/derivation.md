# Transition-pair moment bound

Claim label: `DERIVED`; independent verification required.

## 1. First moment

Fix a root `o` at the prism-free endpoint. The 14 base points are partitioned
into seven mate pairs. A four-point seed chooses one endpoint from four mate
pairs, so there are

```text
C(7,4)*2^4 = 560
```

seeds.

The 84 selected transitions each use three distinct mate groups and extend
to exactly eight seeds. If `j_Q` is the number of selected transitions
contained in seed `Q`, then

```text
sum_Q j_Q = 84*8 = 672.                                (1)
```

Every seed has `0<=j_Q<=4`, because at each of its four base points a local
perfect matching selects at most one pair among the other three points.

Wave 90 used only (1), giving at least `672/4=168` bad seeds.

## 2. Co-incidences around one transition

Fix a selected transition centered at `s` on the base triple `{s,a,b}`.
Its eight seed extensions add a point `d` from one of the four unused mate
groups.

At center `s`, no second transition can occur because the local relation is
a matching.

At center `a`, consider the matching on the three relevant points
`{s,b,d}` as `d` ranges over the eight extensions.

- If `s` is paired with `b`, the same centered transition occurs in all
  eight extensions.
- Otherwise, `s` and `b` have fixed distinct matching partners, so an
  internal transition occurs for at most two extension points.

The same dichotomy holds at center `b`.

The two eight-extension cases cannot occur simultaneously. Together with
the original transition at `s`, they would make the three residual labels

```text
{s,a}, {s,b}, {a,b}
```

pairwise adjacent. The edge `{s,a}--{s,b}` already has common neighbor `s`;
the third residual label would be a second common neighbor, contradicting
`lambda=1`.

Therefore centers `a,b` contribute at most `8+2=10` co-incidences. Each of
the eight extension centers `d` contributes at most one. A fixed selected
transition consequently has at most

```text
10+8 = 18
```

co-incidences with other selected transitions across its eight seeds.

Summing over 84 transitions counts every unordered pair twice, so

```text
sum_Q C(j_Q,2) <= 84*18/2 = 756.                       (2)
```

## 3. Exact moment certificate

For every integer `j` in `{1,2,3,4}`,

```text
1 >= j/2 - C(j,2)/6.
```

Summing this inequality over the bad seeds and using (1)--(2) gives

```text
number of bad seeds
  >= (1/2)*672 - (1/6)*756
  = 210.
```

Hence at most `560-210=350` seeds are transition-free. The verified
complementary-Fano injection maps each rooted positive norm-14 vector to a
distinct transition-free seed. Therefore

```text
#{t: ||t||^2=14 and t_o=+1} <= 350.
```

Every oriented norm-14 vector has seven positive coordinates, so

```text
7*N14 <= 99*350,
N14 <= 4950.                                           (3)
```

The moment relaxation itself is sharp at

```text
n4=42, n3=168, n2=n1=0, n0=350,
```

but this formal distribution is not asserted to come from transition
matchings.

## 4. Rank-28 weighted consequence

Wave 86's exact positive identity also implies

```text
N14 + (37/217)N16 + (43/2387)N18 >= 1997236/341.
```

In the common scope `n3=4158` and `r=28/q=16`, substitute (3) and multiply
by 2,387:

```text
407*N16 + 43*N18 >= 2165002.                           (4)
```

Since shell counts are even, (4) gives the conditional one-shell boundaries

```text
N18=0 => N16>=5320,
N16=0 => N18>=50350.
```

These are lower bounds, not contradictions. A strict compatible upper bound
on the two remaining shells is still missing.
