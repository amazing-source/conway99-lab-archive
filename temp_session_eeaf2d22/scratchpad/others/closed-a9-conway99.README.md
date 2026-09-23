# Closed-A9 exclusion for a putative Conway 99-graph

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21464959.svg)](https://doi.org/10.5281/zenodo.21464959)

**Status:** public preprint package; exact computations reproduced; not yet specialist-reviewed.

This repository supports the following narrow result:

> In the fixed-point-free order-three quotient of a putative strongly regular graph with parameters `(99,14,1,2)`, the branch with `t=6`, triangle block `P=K_3,3`, and the nine-column cell `A9` closed under the doubled-edge graph `D` is impossible.

This does **not** settle the Conway 99-graph problem, the full order-three case, the full `K_3,3` quotient branch, or the non-closed `A9` case.

## What is checked

The verifiers reconstruct and check:

1. the forced 27-column `X` multiset;
2. all 216 possible closed `D[A9]` matching unions;
3. the cycle distribution `36 / 108 / 72` and reduction to 72 nine-cycles;
4. the exact compression eigenvalues `12, 0, 4m/3`, giving `m <= 2`;
5. exact rational inertia for all `m=0,1,2` cases, leaving 27 two-edge graphs;
6. the split of those graphs into dihedral orbits of sizes 18 and 9;
7. a two-row contradiction for the 18-orbit;
8. a four-row contradiction for the 9-orbit.

The corrected proof does not use the previously claimed seven-row SAT certificate.

## Reproduce

### Python

Requires Python 3.10 or later and only the standard library.

```bash
python3 verifier/verify_closed_A9.py
```

### C++

Requires a C++17 compiler and Boost headers.

```bash
g++ -std=c++17 -O2 verifier/verify_closed_A9.cpp -o verify_closed_A9_cpp
./verify_closed_A9_cpp
```

The two implementations use different row-mask generation methods:

- Python: meet-in-the-middle subset summation;
- C++: direct recursive enumeration of eight-element subsets.

Both use exact rational arithmetic for inertia and no SAT/SMT solver, floating-point eigenvalue test, or graph-isomorphism package.

### Build the paper

The paper uses `biblatex` with `biber`:

```bash
cd paper
pdflatex main.tex
