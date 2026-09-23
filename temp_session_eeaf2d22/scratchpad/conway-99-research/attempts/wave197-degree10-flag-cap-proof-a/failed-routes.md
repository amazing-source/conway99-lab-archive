# Wave197 failed and null routes

## Using only the degree-ten row

The degree-ten row is materially stronger than the union bound but does
not by itself yield the final coefficient certificate. The global
exact-three flag cap `n3+h+g<=1287` and old-pair capacity
`a3+b3<=3h` are both needed.

## Treating all labels as degree ten

Bounding every selected exact-three label by ten loses the crucial
private-label contribution. The `p3` private labels have degree exactly
one, producing the coefficient `9*p3` in `S10`.

## Counting companion members separately

The two circuits in one exact-three companion pair realize the same three
labels. A minimal cover cannot select both, so the per-support selected
capacity is one, not two.

## Arithmetic null

The final rational null row has fractional counts and is not a
construction. An integer scalar row at `Q0=7033` may satisfy the displayed
linear inequalities, so no stronger purely scalar claim is made.
