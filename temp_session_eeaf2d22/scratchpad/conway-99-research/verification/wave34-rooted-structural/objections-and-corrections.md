# Wave 34 rooted-structural objections and corrections

## Verdict

No material mathematical discrepancy survives independent reconstruction.
Two release objections required explicit resolution, and one useful scope
refinement is added without changing the candidate's claim.

## O1: canonical coordinates were not bound to Wave 33

**Initial objection.** The candidate used cyclic Fano coordinates and stated
only that they were permutation-equivalent to the fixed Wave 33 labels.
Permutation-invariant distributions do not by themselves bind an
order-sensitive matrix such as `C_star`.

**Resolution.** The verifier loaded the exact Wave 33 arrays and found all
168 signed-Fano coordinate isomorphisms. The lexicographically first binding
is

```text
candidate points -> Wave33 points:
(0,1,3,2,5,6,4)

candidate lines -> Wave33 lines:
(0,3,5,6,2,4,1).
```

The induced 14-support and 70-O permutations make the candidate support
adjacency and support-to-O incidence agree entrywise with the Wave 33
arrays. The mapping payload has SHA-256

```text
7975c51cc684af88f807c9a284a95962b322b2e29928346611934a97d6bf0262.
```

The same O permutation binds the complete fixed integer `C_star` entrywise.
The candidate-order hash is the released
`9bf08bdd...e9e69`; the exact Wave33-order hash is
`cd6f2f1e...398b1`.

**Status:** resolved; no correction to the theorem.

## O2: the SNF statement needed an exact labeled witness

**Initial objection.** Rational rank 13 alone would not prove that all
nonzero Smith factors equal one.

**Resolution.** The released 13-column witness has determinant `+1` both in
candidate coordinates and after the exact Wave33 permutation. A separate
verifier-owned Wave33 spanning-tree minor, using columns

```text
0,2,4,6,7,8,9,10,20,30,40,50,60
```

after deleting support row 13, also has determinant `+1`. Rank 13 plus an
absolute-unit 13-minor forces all thirteen nonzero Smith factors to be one.

**Status:** resolved and independently verified.

## O3: the 2-factor census might have reused discovery internals

**Initial objection.** Re-executing the candidate's point-degree recursion
would only reproduce candidate-owned evidence.

**Resolution.** Candidate code was not imported or executed. The verifier
used two separately written checks:

1. a line-side coefficient-transfer recursion, which gives
   `4,946,952` underlying factors, `574,118,037` labeled columns, and
   1,090 cached states; and
2. an exhaustive ordered-pair-of-perfect-matchings census. A relative
   permutation records each alternating component, and the verifier divides
   ordered edge colorings by the exact component factor.

The second method independently reproduces all 15 released cycle classes
and their total.

**Status:** resolved and independently verified.

## O4: 574,118,037 is not the full-solution single-column domain

**Initial objection.** The candidate census includes half-cycle type `1`,
which selects both copies of one doubled support label. The verified Wave 33
full criterion forbids those two O vertices from sharing a Q neighbor.

**Resolution and scope refinement.** Stage 1 independently proved that every
duplicate-support pair has state

```text
(g,r,h,c)=(2,0,0,0).
```

Thus the two B rows are disjoint in every full six-block solution. The
released `574,118,037` count is nevertheless correct because the candidate
explicitly scoped it to a **single binary column satisfying only**
`Pb=2*1`. It never claimed compatible 15-tuples or complete O-O
compatibility.

Removing all classes containing a half-cycle `1` leaves exactly

```text
half-cycle types: 7, 5+2, 4+3, 3+2+2
full cycle types: 14, 10+4, 8+6, 6+4+4
duplicate-free single columns: 448,879,368
Pb-only columns removed:        125,238,669.
```

This is a stricter consequence for any full solution, not a discrepancy in
the candidate's stated count.

**Status:** candidate scope confirmed; publication should retain this
clarification.

## O5: the 13+14+43 split might differ from Stage 1's 27+43 split

**Resolution.** The formulations are exactly the same after proving the
notation map:

```text
candidate R       = Stage1 P_F                     (rank 13);
candidate E_W     = Stage1 P_B-P_0                 (rank 14);
candidate Q_U     = Stage1 E                       (rank 43);
candidate H_R     = Stage1 T-11P_F;
candidate E       = Stage1 E_-4                    (rank 16);
candidate L       = 147 Stage1 E_-4.
```

Since `P_F P_B=P_0`, Stage 1's combined dimension is
`13+15-1=27`, exactly candidate `13+14`. No equivalence was assumed; the
projector formulas and fixed action were evaluated exactly.

**Status:** resolved and independently verified.

## O6: the converse projector reduction could omit rank or block conditions

**Initial objection.** The reduced list states symmetry,
`L^2=147L`, `PL=0`, and `B^T L=0`, but does not separately list
`rank(L)=16`.

**Resolution.** Symmetry and the quadratic make `E=L/147` an orthogonal
projector. The annihilators put its range in the 43-dimensional joint
kernel. Hollow binary recovery forces

```text
diag L = 30^28,36^42,
tr L =2352=147*16,
```

so its rank is 16. Conversely,

```text
H=(C_star-7BB^T-L)/21
```

is exactly

```text
H_R-E_W+3Q_U-7E.
```

The verifier checked the S-O, S-Q, O-Q, Q-Q, and O-O actions on the
constant, Fano-image, centered-B, residual-3, and residual-minus-4 summands.
The fixed S-S block is imported unchanged. Both directions hold.

**Status:** resolved and independently verified.

## O7: modular shadows might be mistaken for an exclusion

The exact Wave33-order calculation confirms

```text
L = C_star          (mod 7),
rank_F7(C_star)=5,
C_star^2=0          (mod 7),
L = -BB^T           (mod 3).
```

These are compatible nilpotent shadows. Neither yields a rank contradiction
or an infeasibility certificate.

**Status:** verified constraint; no exclusion.

## Strongest surviving objection

The exact reduction still leaves an unrestricted labeled simple
`2-(15,3,2)` design coupled to an integral rank-16 projector on a
design-dependent 43-space. Neither the 448,879,368 duplicate-free
single-column count nor the 432-dimensional Grassmann locus enumerates
compatible 15-column tuples or quantized projectors.

Therefore binary existence/exclusion, rooted graph extension, the full
endpoint, `n3=708`, Conway-99, and novelty all remain `UNKNOWN`.
