# Retained failed routes and hostile boundaries

## Pairwise trace is not an intersection number

The star projectors need not commute.  Neither `tr(P_xP_y)` nor
`dim(E_x intersect E_y)`, separately or together, determines
`tr(P_xP_yP_xP_y)`.  The explicit `P,Q1,Q2` control proves this by exact
matrices.

## The pairwise trace Gram does not determine fourth order

The two 99-projector controls have the same labelled pairwise trace Gram
and different labelled fourth-trace matrices.  Therefore no argument may
reconstruct the fourth tensor from `2BLB^T` alone.

The controls satisfy:

- nondegenerate ambient dimension 11 over `F_3`;
- 231 labelled singular columns spanning dimension 11;
- centered Gram rank 11 and square zero;
- 99 rank-six trace-zero self-adjoint idempotents;
- seven simplex columns per star;
- column incidence degree three; and
- zero total projector sum.

They fail:

- projective distinctness of the 231 columns;
- dual distance at least four;
- linear point-triangle incidence;
- `BB^T=A+I` for the target SRG;
- the exact selected orthogonality and block-relation profiles; and
- realization by any asserted graph, endpoint code, or cover.

They refute only the pairwise-to-fourth-order implication.

## Exterior square is not additive

Although `sum_x P_x=0`,

```text
sum_x wedge^2(P_x)=0
```

does not follow.  Exterior squaring is quadratic, not linear.  The new
detector therefore supplies no zero row sum without an additional
graph-specific calculation.

## The detector does not count every two-component

The fourth trace is the number of `2`-parts modulo three.  Type `2+2+2`
has three such parts and trace zero.  Reporting the trace as an integer
number of two-components would be false.

## Nonedges remain unclassified

The four cycle-type reduction applies to adjacent vertices.  For a
nonedge, Wave176 only forces a cross-star relation; it does not give a
four-type Gram classification.  No value of
`tr(P_xP_yP_xP_y)` is promoted for nonedges.

## No global contradiction

There is no verified global count of `4+2` edge types and no incompatible
rank, determinant, or positivity bound for the fourth-trace matrix.  The
result is a new exact local detector and a precise missing invariant, not
an endpoint exclusion.
