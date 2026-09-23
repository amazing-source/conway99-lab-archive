# Wave56 bootstrap-percolation closure space

Status: `DERIVED`, pending independent verification.

The [primary source](https://ajc.maths.uq.edu.au/pdf/93/ajc_v93_p060.pdf)
is Ibrahim, LaFayette, and McCall, *Australasian Journal of Combinatorics*
93(1) (2025), especially Lemma 4.9 and Theorem 4.19.

## Exact results

For a hypothetical `srg(99,14,1,2)`, a nonedge either percolates or has the
unique proper closure

```text
srg(9,4,1,2) = K3 square K3.
```

Writing `P` for induced triangular prisms, `H` for induced
`K3 square K3` closures, and `R,S` for nonpercolating and percolating
nonedges:

```text
n3 + 3P = 4158,
R = 18H,
H <= 231,
6H <= P,
R <= 3P = 4158-n3,
S >= n3.
```

Moreover `2<=m(G,2)<=3`, with `m(G,2)=3` exactly when `H=231`.
This independently recovers the target arithmetic in Theorem 4.19 from the
general closure lemma.

Equality `R=3P` is not proved in general.  It holds exactly when every prism
lies in a rook-graph closure.  At the prism-free endpoint, every one of the
4,158 nonedges percolates.

The first waves from an arbitrary nonedge are exact:

```text
seed:   2 vertices
wave 1: the two common neighbors, completing C4
wave 2: the four unique edge-triangle mates
```

All 64 labeled tip graphs were tested.  Four satisfy the local
`lambda=1,mu=2` caps, but only the empty tip graph is prism-free.  At that
endpoint seed:

```text
allowed next-wave neighborhood masks: 23
exact labeled multiplicity profiles:   35
formal D4 label-orbits:                 11
new vertices in wave 3:                 8 through 16
```

The exact compressed constraint is

```text
x2 + 3*x3 + 6*x4 = 16.
```

This smaller CSP has feasible local profiles and gives no global
contradiction.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave56-percolation-closure\percolation_closure.py `
  --verify attempts\wave56-percolation-closure\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave56-percolation-closure -p "test_*.py" -v
```

The computation aborts below 15 percent free physical memory.  No graph,
endpoint exclusion, stricter `n3` upper bound, or novelty claim follows.
