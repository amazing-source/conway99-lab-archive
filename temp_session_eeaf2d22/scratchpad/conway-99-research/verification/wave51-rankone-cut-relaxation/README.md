# Wave 51: exact finite rank-one cut probe

Status: **VERIFIED_SCOPED**.

## Result

The fixed balanced relaxation consisting of:

- all 170 Wave44 equations;
- 208 nonnegative order-seven variables and `2079<=h11/4<=4158`;
- all 17 frozen Wave45 cuts;
- the first retained Wave47 direction for every one of 17 sources and eight
  root families (136 cuts); and
- one exact Wave49 direction for each of 21 root families

is **exactly feasible over the rationals**.

The certificate has 136 nonzero order-seven coordinates and `h11/4=4158`.
Exact substitution passes all 170 equations and all 174 cuts. Sixty-six cuts
are tight—5 Wave45, 46 Wave47, and 15 Wave49—and the other 108 have strictly
positive slack; the minimum positive exact slack is `133056`.

All 21 Wave49 cuts were independently reconstructed from their primitive
integer directions and the clean-room-verified order-six/order-seven tensors,
with 5,691 exact reconstruction checks.

HiGHS was used only to select an active set. Exact sparse rational RREF produced
a rank-209 point, and a separate replay of the stored fractions supplies the
evidence. The largest denominator has 272 decimal digits.

## Meaning

This refutes one proposed shortcut: these 174 fixed rank-one inequalities
cannot yield a Farkas contradiction with the Wave44 count system.

It does not test every available cut, the full PSD matrices, or integrality.
The witness is not a graph and is not endpoint feasibility evidence.

See [strategy-assessment.md](strategy-assessment.md) for the ranked continuation:
exact facial-dual cutting plane first, proof-producing SAT/PB second, coherent
configuration closure third, and graph coverings only after a forced quotient
appears.

## Reproduce

```powershell
.\.venv\Scripts\python.exe verification\wave51-rankone-cut-relaxation\probe.py --validate
.\.venv\Scripts\python.exe -m unittest verification\wave51-rankone-cut-relaxation\test_probe.py
```

The original construction command is:

```powershell
.\.venv\Scripts\python.exe verification\wave51-rankone-cut-relaxation\probe.py --compute
```

The run enforces a 15% free-physical-memory floor and never modifies the sealed
Wave46--Wave49 artifacts.
