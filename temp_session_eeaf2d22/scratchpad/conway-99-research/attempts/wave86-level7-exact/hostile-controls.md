# Wave 86 hostile controls

- The 15 product forms are checked independent through the exact Sturm
  coordinate range.
- The exact Fricke matrix is checked to square to the identity.
- Reversing the theta-transfer sign changes the formal control's constant
  term from `1` to `-1`.
- Replacing `7^3` by `7^2` changes that constant term to `1/7`.
- The coefficient identity is checked coefficientwise as an affine
  identity, not only on one example.
- The rational bound is not rounded naively: the imported Wave 71
  congruence `S=2 mod 14` is used to obtain `S>=5868`.
- The formal equality control is explicitly labeled as not a lattice or
  graph, and it is replayed exactly through `q^50`.
- The checker refuses to start below 15 percent free physical memory.
