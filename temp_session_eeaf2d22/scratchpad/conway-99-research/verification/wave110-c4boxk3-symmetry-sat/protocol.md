# Wave 110 independent verification protocol

Role: verifier.

Freeze the sealed discovery manifest before inspection. Work only in this
verification directory.

Independently:

1. reconstruct `C4 box K3`, its 87 forced incidence rows, and the exact
   variable, clause, and cardinality counts;
2. test the submitted lex-CNF as an existential encoding of Boolean
   lexicographic order;
3. prove the simultaneous row-order theorem using one shared weighted orbit
   potential, checking why columns inside the compared class are omitted;
4. prove that the four `e(X0)` branches partition all labelled `X0` graphs
   without a canonical-label assumption;
5. validate every preserved raw-log hash and its fail-closed status;
6. rerun the discovery audit, tests, and four sequential 45-second branches;
   and
7. preserve every timeout as `UNKNOWN`.

The verifier must veto any target-automorphism assumption, any incomplete
branch fixing, or any graph, UNSAT, Conway-99, or novelty promotion.
