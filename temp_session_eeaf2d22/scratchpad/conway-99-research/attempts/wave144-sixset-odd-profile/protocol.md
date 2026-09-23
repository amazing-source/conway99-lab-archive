# Wave144 protocol

## Frozen target

Condition on a hypothetical `srg(99,14,1,2)` and the frozen Wave21
six-vertex class census.  For each induced six-set, enumerate the complete
integer outside-neighborhood profile `z_P`, with no assumed automorphism.

Couple the resulting exact output-weight supports only through:

- the 62 affine Wave21 class marginals;
- nonnegative integral class/weight counts; and
- the Krawtchouk reciprocity moments `t=0,1,2,3` from the frozen Wave141
  low-input rows.

## Exactness boundary

- All 64 subsets `P` are allowed.
- Every local variable is a nonnegative integer.
- Exact support means every attainable weight has a witness and every omitted
  weight is excluded by an exhaustive finite enumeration.
- Pair cells, singleton cells, and the empty cell are reconstructed exactly
  after enumerating all cells of size at least three.
- The aggregate endpoint must be an explicit integer certificate.
- The known `n3<=4158` bound is imported, not reproved.
- Aggregate feasibility is not graph realizability.
- Discovery cannot verify itself.

## Reciprocity equation

With

```text
B[i,j] = #{x in F_2^99 : wt(x)=i and wt(Ax)=j},
```

Krawtchouk orthogonality applied to the Wave141 transform gives

```text
sum_j K_t(j) B[6,j] = sum_b K_6(b) B[t,b].
```

The right side is exactly known for `t=0,1,2,3`.
