# Wave 81 protocol

Claim label: `DERIVED`.

## Frozen conditional input

Assume a hypothetical `srg(99,14,1,2)` and the verified Wave 78 norm-16
packing conclusion, itself conditional on the Wave 71 signed-support branch:

- the signed support is `P disjoint union N`, with `|P|=|N|=8`;
- both sign sides are independent;
- the induced support graph is 4-regular and bipartite;
- the 83 outside vertices split as
  `(|X0|,|X1|,|X2|)=(11,64,8)`;
- a vertex in `Xd` meets exactly `d` vertices of each sign side.

Wave 81 validates no upstream lattice or modular-form theorem. It derives
the exact labelled consequences of this frozen graph-theoretic input.

## Enumeration policy

The support enumerator assumes no graph automorphism. It quotients only
coordinate relabellings:

1. send one row to the mask `00001111`;
2. sort row masks;
3. canonically minimize over every choice of anchor row and the `4! 4!`
   column permutations that send it to the anchor mask.

Every `8 x 8` matrix has such a representative. This is isomorphism
normalization, not a restriction on the hypothetical target.

## Status policy

- Exact identities and complete finite enumerations are `DERIVED`.
- Surviving support/coupling rows are necessary incidences, not graph
  constructions.
- Solver or enumerator nonhits are not used outside the proved complete
  finite domains.
- Conway-99 and literature novelty remain `UNKNOWN`.
