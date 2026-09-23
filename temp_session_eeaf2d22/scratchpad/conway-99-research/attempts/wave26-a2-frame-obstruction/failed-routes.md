# Wave 26 retained hostile, incomplete, and non-excluding routes

None of the items below is evidence for existence or nonexistence of
`srg(99,14,1,2)`. They delimit the exact `A2` frame obstruction.

## 1. Primitive embedding alone remains open

The proof uses all of

```text
M=Y S Y^T,
Y^T Y=21 S^-1,
M_ii=4,
M_ij in {0,1,-1,-2}.
```

It does not prove that the Wave 24 Gram form cannot embed primitively into
`Z^231` when the projector diagonal, entry set, and tight-frame identity are
discarded.

## 2. The `h=9` arithmetic row remains

The obstruction applies to scaled-dual forms with an orthogonal `A2`
summand. The exact Wave 24 survivor has two such summands, but no
classification was proved for all even rank-44 determinant-nine forms.
Therefore neither all `h=9` lattices nor the `h=9` index row are excluded.

## 3. Allowing off-diagonal `+2` breaks the fiber cap

Inside the frozen survivor, take one fixed root in an `A2` block and pair it
with four norm-two simple roots in four different `E8` blocks. The four
resulting norm-four rows have pairwise inner product `+2`. Thus the
four-row fiber becomes locally valid if `+2` is added to the entry set.
This is a hostile local control, not a complete frame.

## 4. The frame identity cannot be omitted

The checker constructs 18 norm-four rows satisfying every displayed local
off-diagonal restriction. It pairs each of the six oriented roots in one
`A2` block with a three-root zero-sum triple in a separate complement
block. Their central second moment is

```text
[[12,6],[6,12]],
```

not the required

```text
21 A2^-1 = [[14,7],[7,14]].
```

So local norm and entry conditions alone do not force the count 21.

## 5. Rows meeting both `A2` blocks are not an exception

Such a row has norm-two projection to each block. Relative to either chosen
summand, the root in the other block is simply its norm-two complement
component. The row is counted once in each block's separate energy identity,
and the same-root fiber inequality still applies.

## 6. No endpoint promotion

The exact survivor is refuted only as a realization of the required
231-row projector package. Other scaled-dual forms may survive. No
`n3=708` exclusion, graph construction, Conway-99 resolution, or novelty
claim follows.
