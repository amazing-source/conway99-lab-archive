# Wave 27 orchestrator correction ledger

Date: 2026-07-24

Status: `RECORDED_NONFATAL_CORRECTIONS`

This ledger preserves three chronology and exposition corrections without
silently rewriting frozen discovery or literature inputs.

## 1. E6 trace parity bridge

The frozen discovery report
`agents/2026-07-23-wave27-h9-classification.md` excludes
`tr(C^2)=2` and then states the next case as `tr(C^2)>=4`, but it does not
spell out the necessary parity bridge

```text
tr(C^2) congruent to tr(C) modulo 2.
```

The independent verifier records and proves that bridge in
`verification/wave27-h9-classification/2026-07-24T002029Z-audit.md` and
tests it explicitly. The theorem and equality witness pass independently;
the omission is a documentation defect in the frozen discovery prose, not a
counterexample to the result.

## 2. Literature protocol interpretation

The frozen file `verification/wave27-literature-audit/protocol.md`
incorrectly allowed `21E6^{-1}` to be read as a factor-two expression. It
remains unchanged as an auditable input. The operational correction in
`verification/wave27-literature-audit/protocol-correction.md` fixes the
meaning to twenty-one times `E6^{-1}` and adds a separate corrective query
family. The final literature counts distinguish the 45 original pairs, five
corrective pairs, and six later A20 pairs. zbMATH 404 responses remain service
failures, not zero-result evidence.

## 3. A20 addendum chronology

The frozen core tensor report correctly leaves
`A20 orthogonal-sum E8^3` as the unique survivor of its stated ADE screen.
Only afterward did the orchestrator freeze
`agents/2026-07-24-wave27-a20-trace-addendum.md`. The blind tensor verifier
intakes and verifies that package separately. Central claims must therefore
retain two steps:

1. the core screen has exactly one survivor; and
2. the later A20 trace addendum excludes that survivor.

The combined conclusion is conditional: under the `n3=708` projector/Schur
endpoint premises and the additional hypothesis that the scaled-dual form is
a full orthogonal sum of irreducible ADE root lattices, no such form exists.
General even rank-44 lattices, nonorthogonal root subsystems, `n3=708`,
Conway-99 existence, and novelty remain `UNKNOWN`.
