# Independent audit

The verifier used only the SHA-bound Wave 37 OPB, Wave 42 seventh-triangle
delta and closure certificate, rooted labelling convention, and the frozen
verification protocol as inputs. It did not import or call either Wave 43
discovery script.

Evidence reproduced:

- compressed/decompressed source hashes and declared/observed OPB counts;
- exact 830-assignment closure, including 174 primary assignments;
- the full 924-record coordinate-triangle catalogue and its `7/157/760`
  closure classification;
- all 288,420 unordered eligible pairs and 1,556,994 matching visits;
- 40,800 unique width-four cuts and zero exact prior-row overlap;
- raw catalogue SHA-256
  `cafd0eddbc8371d59f7fb184b51f6a6facdeee9d1a50bbea7b30b95e2fa2b462`;
- 34,340 active rows after 6,460 satisfied rows, catalogue SHA-256
  `8c8afac5833ce5a2739fa6043d255adae5e3eb52b6bc75799fcd2ce86d297bf8`;
- exact byte equality of both deterministic OPB/gzip exports;
- exact equality of the selected variables and all 64 probe records.

The mate-anchor characterization was checked per accepted visit: all 40,800
accepted matchings have mate anchors and match the anchors to each other.
No automorphism was used to omit a labelled case.

The verifier rejects promotion to `SAT`, `UNSAT`, branch closure, endpoint
exclusion, a strict upper bound, or a Conway-99 solution. The family omits
prisms involving non-coordinate-anchored triangles, and the probes are a
bounded propagation diagnostic.
