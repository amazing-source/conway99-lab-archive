# Wave 59 incidence spectral-excess space

Status: discovery-only `DERIVED`, pending independent verification.

Conditional on a prism-free `srg(99,14,1,2)`, the point--triangle incidence
graph is a connected `(7,3)`-biregular graph on `99+231` vertices with

```text
spectrum:
  +/-sqrt(21)^1, +/-sqrt(10)^54, +/-sqrt(3)^44, 0^132
girth:   8
diameter: 6
```

Its point-root layers are equitable:

```text
1,7,14,84,84,140
{7,2,6,2,5; 1,1,1,2,3}.
```

Its triangle-root layers are

```text
1,3,18,36,180,60,32,
```

but distance-four `B` and `C` triangles have two and one predecessors,
respectively. Thus the incidence graph is not distance-biregular.

The regular 18-valent triangle graph has spectrum

```text
18^1, 7^54, 0^44, (-3)^132
```

and diameter three. Its spectral excess is 50 while its actual excess is 32.
The exact defect is

```text
p3(K)-A_D = (A_C-2A_B)/4,
||p3(K)-A_D||^2 = 18.
```

The orthogonal projection residual of `A_D` from the polynomial adjacency
algebra has normalized squared norm `288/25`. A separate binary
pair-neighborhood Gram matrix `153I+10K+A_B` is positive definite of rank
231.

Ihara--Bass gives exact simple-cycle counts

```text
C8=2079, C10=33264, C12=250866, C14=2494800.
```

All results are consistent. No graph, endpoint exclusion, strict `n3` upper
bound, or novelty claim follows.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave59-incidence-spectral-excess\incidence_spectral.py `
  --verify attempts\wave59-incidence-spectral-excess\exact-result.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave59-incidence-spectral-excess -p "test_*.py" -v
```
