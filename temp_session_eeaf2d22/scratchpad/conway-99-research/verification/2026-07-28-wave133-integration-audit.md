# Waves 130, 132, and 133 integration audit

Date UTC: 2026-07-28

Verdict: **PASS WITH UNCHANGED GLOBAL STATUS**.

The orchestrator checked the three sealed discovery packages against their
independent verifier packages and replayed the package manifests and focused
tests.

## Promoted scoped results

1. Wave 130 is `VERIFIED_SCOPED_FINITE`: the level-seven index-10/index-70
   Jacobi necessary-condition relaxation has an exact rational feasible point
   through cutoff 28.  The independent verifier regenerated 239 columns
   without a discovery import or serialized cache and checked all 454
   equalities and 1,686 inequalities.  Exactly 506 inequalities are tight.
2. Wave 132 is `VERIFIED_SCOPED_RATIONAL`: distinguished neighborhood and
   closed-neighborhood moments force `A94=A96=A98=0`, refuting the Wave 131
   point.  A stronger rational split-enumerator point satisfies all four
   low-degree distinguished systems.  Integral and full genus-two feasibility
   are not decided.
3. Wave 133 is `VERIFIED_SCOPED_CONTROL`: the holonomy sign identity and two
   opposite-sign local controls are exact.  The independently reconstructed
   connected endpoint-scale nonorientable surface control proves that the
   stated aggregate parity data do not force a contradiction.

## Manifest bindings

```text
Wave130 discovery: 8b1da27e3acaa059934704a85aaa380e101e1db330925ced6e048330d318e3ae
Wave130 verifier:  5d1aed1c539901077a709ca57e759d71676e432fa31dd80cadf990df7d1a9a8e
Wave132 discovery: 0b99e87b0f39b1c203709d34ffba3f7b5c94f0078c53fe4020dfc3cd03ec510c
Wave132 verifier:  a49d3686fe7ec985f973b198529da97530931b186ca0e166a1f81d73b77a8a26
Wave133 discovery: dae34acdfd3a95c99db79567bf9b8ed20aa1423812dcb4dbe7681730b6d9870a
Wave133 verifier:  96081553148ba8bac3aafdb17a705e2764621e6ffc8aa2373cf77181939f23a9
```

## Status wall

No package constructs a binary or quaternary code, lattice, adjacency
matrix, or strongly regular graph.  No package realizes or excludes rank 28,
excludes the prism-free endpoint, improves `n3<=4158`, or resolves
Conway-99.  Literature novelty remains `UNKNOWN`.
