# Wave144: exact six-set outside profiles

This package lifts each of the 62 Wave21 induced six-vertex classes into a
64-cell outside-neighborhood profile.  For a fixed six-set `S`, let

```text
z_P = number of x outside S with N(x) intersect S = P,
```

for every subset `P` of `S`.

## Exact result

The degree and pair-common-neighbor equations are

```text
sum_P z_P = 93,
sum_(P contains v) z_P = 14-deg_H(v),
sum_(P contains u,v) z_P
  = (1 if uv is an edge else 2)-cn_H(u,v).
```

They determine the possible image weight by

```text
wt(A 1_S)
  = number of odd-degree vertices in H
    + sum_(|P| odd) z_P.
```

The checker exactly enumerates the attainable weights, including gaps, for
all 62 source classes.  It confirms the four proposed forced cells:

```text
class 1  -> 66
class 3  -> 56
class 5  -> 46
class 14 -> 36.
```

After coupling the class-count marginals to the Wave141 reciprocity moments
for `t=0,1,2,3`, an explicit nonnegative **integer** aggregate witness still
exists at `n3=4158`.  Every nonzero class/weight cell in that witness has an
explicit integer local `z_P` witness.

Thus the lifted model's optimum, with the already known cap `n3<=4158`
imported, is exactly `4158`.  This is a rigorous null boundary: these
constraints do not strengthen the upper bound.

## What the certificate is not

The aggregate witness does not make choices consistent across overlapping
six-sets.  It is not a graph, and it is not evidence that an
`srg(99,14,1,2)` exists.  Conversely, endpoint survival in this relaxation
does not establish that stronger profile lifts will also survive.

## Reproduce

```powershell
python -B attempts\wave144-sixset-odd-profile\exact_check.py --verify

python -B -m unittest discover `
  -s attempts\wave144-sixset-odd-profile -p "test_*.py" -v
```

The exact support enumerator and certificate replay use only the Python
standard library.

## Most promising continuation

The missing information is compatibility between profiles of overlapping
six-sets.  Two concrete next lifts are:

1. extend each selected six-profile through a seventh vertex and require
   compatible deletion marginals; or
2. introduce joint cells for two six-sets sharing five vertices, then
   eliminate them to obtain new inequalities on the current aggregate table.

Higher reciprocity moments `t=4,5,6` are another route, but they require
additional low-input rows rather than only the already frozen Wave141 data.
