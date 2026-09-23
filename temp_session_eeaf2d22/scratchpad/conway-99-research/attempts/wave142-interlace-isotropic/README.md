# Wave142: interlace/isotropic-matroid checkpoint

This package tests a different representation of the hypothetical
`srg(99,14,1,2)`: principal binary nullities and the isotropic matroid
`IAS(G)=[I|A|I+A]`.

## Exact outcome

- The size-refined vertex-nullity rows are reconstructed through six
  vertices.
- At order six,

  ```text
  I_(6,0)= 45845415 + (4/3)n3
  I_(6,2)=470213205 - 3n3
  I_(6,4)=503184528 + (4/3)n3
  I_(6,6)=101286108 + (1/3)n3.
  ```

- The derived kernel-size moment is
  `16459961595+32*n3`.
- Every principal submatrix of order `86` through `99` has rank `54`;
  its nullity is `|S|-54`.
- The interlace moment needs the support-intersection-zero slice of
  `(x,Ax)`, which is not a coordinate of Wave141's `B[i,j]` table.
- The strongest local isotropic diagonal-toggle inequality gives only
  `n3<=7609140`.

No general bound improves `n3<=4158`; Conway-99 remains `UNKNOWN`.

## Reproduce

```powershell
python -B attempts\wave142-interlace-isotropic\exact_check.py --verify

python -B -m unittest discover `
  -s attempts\wave142-interlace-isotropic -p "test_*.py" -v
```

The checker uses only the Python standard library and performs no
99-vertex subset enumeration.
