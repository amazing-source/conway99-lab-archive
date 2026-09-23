# Wave 110 protocol

Role: construction.

Freeze the sealed Wave 105 discovery and verifier manifests before inspecting
or changing the encoding. Preserve the exact motif-conditional extension
domain. Add only relabeling symmetry constraints within classes of outside
vertices having the same fixed motif-neighborhood pattern.

The symmetry constraint must:

1. compare adjacency only to vertices outside the row's own pattern class;
2. use a proved lexicographic CNF equivalence;
3. retain at least one labeling of every colored extension graph;
4. avoid fixing a labelled `X0` representative; and
5. be described as encoding symmetry, never a target automorphism.

Run branches `e(X0)=0,1,2,3` sequentially for 45 seconds each. Refuse a build
below 20% free physical memory and require at least 15% free after every run.
Directly replay a SAT graph against `A^2=12I-A+2J`. Treat timeout and
uncertified UNSAT as `UNKNOWN`.
