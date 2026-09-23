# Wave 32 literature-package correction ledger

## Independent-audit chronology

The first frozen literature package passed its mathematical applicability
and status audit, but the independent source verifier found three ancillary
bibliographic/scope defects:

1. Source `S06` reversed the published author order.  The corrected order is
   Rudolf Scharlau, then Britta Blaschke.
2. The Hemkemeier--Vallentin description compressed a substantive input
   requirement.  Their incremental decomposition algorithm assumes a
   complete generating system containing all lattice vectors through the
   required bound; it does not manufacture such data for every endpoint.
3. The 14-record set omitted Ali Keramatipour's already-public
   `arXiv:2604.23037v2` SAT report.  That report records computational
   infeasibility, not a checked existence or nonexistence certificate.

The first frozen bytes are identified by:

```text
agent report          8e0d7950eac55e5eb36db9c6b015e7761e80f42f890ed1146fbb4b04036b4c43
source-metadata.json  9db780c7db0151ca90e44781608f6139145b482f65dfa1132ae7fbad580ea85c
audit.md              24dd1de8c3c8a6a6a84abddf2edf65492576643a4e58ed3dd669e4f471b69fab
run-report.yaml       b410a42a2ab7a019609954edc69990794070404206f5c4f04f591b24639c5bda
artifact manifest     7c3c46499f38289690cfd4b51769d98f93c530eeab130b9a73a1d1317eb44572
```

The repaired metadata has 15 records: the original 14 inspected records
plus Keramatipour, explicitly marked as a pre-Wave-32 source added after
independent audit.  The 68-query/17-batch ledger and its chronology are not
rewritten.

Every shorthand for the Wave 31 theorem must retain its hypothesis:

```text
rootless integrally decomposable actual-incidence endpoint:
VERIFIED IMPOSSIBLE
```

The corrections do not change the bounded no-hit conclusion.  Rooted and
rootless integrally indecomposable endpoints, `n3=708`, Conway-99, novelty,
priority, and globally exhaustive literature status remain `UNKNOWN`.
