# Discovery protocol

1. Freeze the endpoint relation order `I,K,D,C,B`, global valencies
   `(1,18,32,144,36)`, and the one-root local row `(1,5,0,8,4)`.
2. Derive the `3K6` partition and the per-opposite-sector `B2/C4` caps without
   invoking a completed-graph automorphism.
3. Retain unresolved cross-sector `B` choices as variables. Do not select a
   cycle type in the forced structure.
4. Encode the choices as 108 candidate nodes and the degree conditions as 36
   exact-two cap nodes.
5. Run exact 2-WL by repeatedly refining each ordered-pair color with the
   multiset of two-step color pairs through every middle node.
6. Stop only when the number of colors no longer grows, then check that every
   stable color has constant integer intersection numbers.
7. Supply explicit integral 2-factor completions and reject any mutation that
   violates a degree-two cap.
8. Use completed structures only to diagnose completion dependence. Do not
   promote their stable colors to endpoint relations.
9. Preserve the status wall: discovery-only `DERIVED`; endpoint and
   Conway-99 `UNKNOWN`.

