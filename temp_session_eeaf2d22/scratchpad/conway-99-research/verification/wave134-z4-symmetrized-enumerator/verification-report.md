# Wave134 verification report

## Verdict

The corrected sealed Wave134 checkpoint is independently verified within its
stated conditional scope. The finite rational and integral relaxations for
the corrected model were not run, so realizability and Conway-99 remain
`UNKNOWN`.

## Independent derivation

From

```text
SNF(A)=diag(1^45,3^9,6,12^43,84)
```

reduction modulo four gives

```text
C = im_Z4(A):  Z4^54 x Z2,  |C|=2^109,
Cperp:         Z4^44 x Z2,  |Cperp|=2^89.
```

The factor `2*1` belongs to both codes and swaps zero and two symbols. The
binary residue and torsion identities are

```text
Res(C)=R,              Tor(C)=R+<1>,
Res(Cperp)=D∩even,     Tor(Cperp)=D,
```

where `D=Rperp`, `1` belongs to `D`, and `d(D)>=8`.

All nonzero `Z4` coefficient patterns on at most three graph rows, together
with their `2*1` translates, yield 84 expanded compositions in 42 swap
orbits and exactly 8,557,760 distinct primal words. All even-coefficient-sum
patterns on at most three closed rows yield 44 expanded compositions in 22
swap orbits and exactly 4,126,784 distinct dual words. A direct Venn-atom
enumeration agrees with the formula derivation.

The symmetrized transform is

```text
swe_Cperp(x,y,z)
  = |C|^-1 swe_C(x+2y+z, x-z, x-2y+z).
```

Its substitution matrix squares to `4I`, and two independent coefficient
implementations agree on 28,982 hostile coefficients.

## Verifier vetoes incorporated before final seal

The clean-room checker caught two material pre-publication errors:

1. the initial forced tables omitted mixed coefficient patterns and conflated
   `q_u+q_v` with `q_u-q_v`; and
2. the first corrected package still allowed dual odd-symbol weight 92.

For the second veto, if `d` is a nonzero word in
`Res(Cperp)=D∩even`, then `1+d` is also a nonzero word of `D`. The
minimum-distance bound gives

```text
8 <= wt(d) and 8 <= wt(1+d)=99-wt(d),
```

so `wt(d)<=91`, and evenness sharpens this to `wt(d)<=90`. The four
weight-92 swap orbits are therefore forbidden. The final sealed state counts
are 1,119 primal admissible orbits and 1,114 dual admissible plus 161 dual
forbidden orbits.

## Reproduction results

- Independent result replay: pass.
- Independent unit tests: 10/10 pass.
- Sealed discovery canonical replay: pass.
- Sealed discovery unit tests: 5/5 pass.
- Discovery manifest: 13/13 entries pass.
- Free physical memory after the runs: 55.4 percent.

## Boundary

All earlier rational and numerical searches used an undercounted preseal
model and are explicitly invalidated with inference `NONE`. The corrected
rational and integral models are `UNKNOWN_NOT_RUN`. There is no rational
witness, exact infeasibility certificate, `Z4` code, adjacency matrix, graph,
or resolution of Conway-99 in this package.
