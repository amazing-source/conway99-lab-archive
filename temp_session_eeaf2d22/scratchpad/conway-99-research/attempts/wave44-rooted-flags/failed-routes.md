# Failed routes and nonpromotion wall

## Floating MILP infeasibility

An initial SciPy/HiGHS integer run reported the 170-row system infeasible.
This was false. An exact integer model with 91 positive classes satisfies
every row, so the floating status is classified

```text
FALSE_NEGATIVE_REFUTED_BY_EXACT_WITNESS.
```

No solver exit code is used as mathematical evidence.

## Ordinary real Farkas certificate

The continuous LP relaxation is numerically feasible, so an ordinary
equality/nonnegativity Farkas contradiction cannot exist. Searching for such
a ray after the integer false negative would have targeted the wrong proof
system.

## Pure modular contradiction

Coefficient and augmented ranks agreed over the tested small and large
primes. This was a useful warning, but absence of a modular contradiction is
not a feasibility proof. The exact integer witness supersedes the diagnostic.

## Rooted first moments as a graph

The 91-support vector is not an assignment of graph types to actual
seven-subsets. It satisfies aggregate first moments but not explicit overlap
consistency. It is neither a 99-vertex graph nor evidence that one exists.

## Fake PSD products

Products of aggregate rooted counts cannot be substituted for joint rooted
flag densities. Two flags glued along a root may share unlabelled vertices
or impose incompatible edges. A future PSD matrix needs an exact gluing
semantics and higher-order variables.

## Endpoint and upper bound

Exact feasibility supplies no endpoint graph and no contradiction:

```text
n3=4158:                UNKNOWN
strict upper bound:     NOT PROVED
Conway-99:              UNKNOWN
novelty/priority:       UNKNOWN.
```
