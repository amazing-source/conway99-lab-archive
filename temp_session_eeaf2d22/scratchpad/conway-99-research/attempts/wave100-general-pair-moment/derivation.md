# General prism-sensitive pair-moment bound

Claim label: `DERIVED`; independent verification required.

Fix a root `o`, and let `f_o` be the number of induced prisms containing it.
Exactly `m_o=84-f_o` selected transitions are supported on three distinct
mate groups and therefore occur in four-point seeds.

The Wave 99 pair-moment calculation applies verbatim to these `m_o`
transitions:

```text
sum_Q j_Q = 8m_o,
sum_Q C(j_Q,2) <= 9m_o.
```

Using `1 >= j/2-C(j,2)/6` for `j=1,2,3,4`, the number of bad seeds is at
least

```text
4m_o-(3/2)m_o = (5/2)m_o.
```

After integer rounding, the number of rooted valid seeds is at most

```text
560-ceil(5(84-f_o)/2)
  = 350+floor(5f_o/2).
```

The complementary-Fano seed map is injective, so this bounds rooted
positive norm-14 vectors. Sum over the 99 roots:

```text
7*N14
 <= 99*350 + sum_o floor(5f_o/2)
 <= 34650 + (5/2)sum_o f_o.
```

The verified rooted-prism identity `sum_o f_o=6P` gives

```text
7*N14 <= 34650+15P.
```

Finally `n3+3P=4158`, hence

```text
7*N14 <= 55440-5*n3,
N14 <= floor((55440-5*n3)/7).
```

Since vectors occur in antipodal pairs,

```text
N14 <= 2*floor((55440-5*n3)/14).
```

The endpoint values include:

| `n3` | `P` | ordinary floor | even upper |
|---:|---:|---:|---:|
| 4158 | 0 | 4950 | 4950 |
| 4155 | 1 | 4952 | 4952 |
| 708 | 1150 | 7414 | 7414 |
| 0 | 1386 | 7920 | 7920 |

No shell-sum or `n3` contradiction follows without upper bounds for
`N16` and `N18`.
