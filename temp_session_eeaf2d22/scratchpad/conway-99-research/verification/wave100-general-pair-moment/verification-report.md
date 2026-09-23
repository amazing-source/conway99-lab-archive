# Wave 100 verification report

Verdict: **VERIFIED SCOPED**.

## Independent derivation

At a root `o`, let `f_o` count the selected mate-forbidden transitions.
They are in bijection with induced triangular prisms containing `o`.
The independent six-root reconstruction gives

```text
sum_o f_o = 6P.
```

Exactly `m_o=84-f_o` selected transitions are seed-eligible. Every such
transition lies in eight seeds. The independent general local enumeration
uses all 10,395 perfect matchings on the 12 endpoints; mate edges are
allowed. It confirms:

- a mate-forbidden transition lies in zero four-point seeds;
- a nonmate transition lies in eight seeds;
- the same `lambda=1` residual-triangle guard used at the endpoint remains
  valid;
- the two other original centers contribute at most 10, and the eight
  fourth-point centers at most eight in total.

Thus the per-transition co-incidence cap is still 18, even when unrelated
local matching edges may be mate transitions. Consequently

```text
sum_Q j_Q = 8m_o
sum_Q C(j_Q,2) <= 9m_o.
```

The pointwise moment certificate gives at least `5m_o/2` bad seeds.
Because the count is integral, the precise rootwise bound is

```text
a14(o)
 <= 560-ceil(5(84-f_o)/2)
  = 350+floor(5f_o/2).
```

The ceiling and floor directions were checked for every integer
`0<=f_o<=84`, including the half-integral odd rows.

Summing requires care: a sum of floors is at most the floor-free sum, not
at least it. More exactly,

```text
sum_o floor(5f_o/2)
 = (5*sum_o f_o - number_of_odd(f_o))/2
 <= 15P.
```

Therefore

```text
7*N14 <= 99*350+15P = 34650+15P.
```

Using `n3+3P=4158` produces the exact coefficient

```text
34650+15P = 55440-5*n3.
```

Finally, the norm-14 vectors form fixed-point-free antipodal pairs, so
`N14` is even. The strongest even integer allowed by the inequality is

```text
N14 <= 2*floor((55440-5*n3)/14).
```

All 1,387 compatible rows `P=0,...,1386` were checked. Antipodal parity
strictly improves the ordinary integer floor on 693 of them. Representative
even bounds are `4950` at `n3=4158`, `4952` at `n3=4155`, `7414` at
`n3=708`, and `7920` at the arithmetic row `n3=0`.

## Discovery comparison and boundary

The nine Wave 100 manifest entries were rehashed against the frozen
manifest hash
`0dedf60c7994f842887c084bae7f6585f8fc98be568c940efb5b5ea90320bc88`.
The discovery formulas, representative rows, sign convention, and scope
agree exactly. All 18 verifier tests and all six discovery tests pass.

The discovery correctly recorded that Wave 99 was unverified at its
creation time. The separate Wave 99 clean-room package now verifies the
needed local lemma.

This theorem bounds `N14` as a function of `n3`. It does not bound `n3`,
control `N16` or `N18`, exclude a graph, or resolve Conway-99. Novelty
remains `UNKNOWN`.

## Potential next strengthening

The floor-sum loss is exactly half the number of roots with odd `f_o`.
Under only `0<=f_o<=84` and `sum f_o=6P`, the current scalar bound is sharp:
an all-even distribution attains it for every compatible `P`. A further
improvement through this route therefore needs a graph-specific theorem
forcing odd rooted prism counts, or another compatibility constraint on the
full vector `(f_o)`. Merely refining scalar floor arithmetic cannot help.
