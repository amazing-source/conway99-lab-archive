#!/usr/bin/env python3
"""Generate a complete labeled CNF for the Wave 34 rooted criterion.

The fixed cells are the canonical signed-Fano support S (14 vertices), the
fixed S--O incidence F (70 O labels), the zero S--Q block, and the independent
Q cell (15 vertices).  The primary Boolean variables are every ordered entry
of D (the 70 by 70 O--O block) and every entry of B (the 70 by 15 O--Q block).

Every D entry is represented explicitly.  Unit/equivalence clauses impose a
hollow symmetric D.  This is intentionally less compressed than an
upper-triangular representation: the symmetry and hollow gates are visible in
the certified formula.

Only the Python standard library is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, TextIO


S_SIZE = 14
O_SIZE = 70
Q_SIZE = 15

# Canonical Fano lines on points 0,...,6.  Support vertices 0,...,6 are the
# positive/point side and 7,...,13 are the negative/line side.
FANO_LINES = (
    (0, 1, 3),
    (0, 2, 6),
    (0, 4, 5),
    (1, 2, 4),
    (1, 5, 6),
    (2, 3, 5),
    (3, 4, 6),
)


def canonical_fixed_data() -> tuple[list[list[int]], list[dict[str, int]], list[list[int]]]:
    """Return (A_S, O labels, F) for the fixed labeled signed-Fano support."""
    line_sets = [set(line) for line in FANO_LINES]
    support = [[0] * S_SIZE for _ in range(S_SIZE)]
    for point in range(7):
        for line, points in enumerate(line_sets):
            if point not in points:
                support[point][7 + line] = 1
                support[7 + line][point] = 1

    labels: list[dict[str, int]] = []
    for point in range(7):
        for line, points in enumerate(line_sets):
            multiplicity = 2 if point in points else 1
            for copy in range(multiplicity):
                labels.append({"point": point, "line": line, "copy": copy})
    if len(labels) != O_SIZE:
        raise AssertionError(f"expected {O_SIZE} O labels, got {len(labels)}")

    incidence = [[0] * O_SIZE for _ in range(S_SIZE)]
    for o, label in enumerate(labels):
        incidence[label["point"]][o] = 1
        incidence[7 + label["line"]][o] = 1
    return support, labels, incidence


def matrix_product_entry(left: list[list[int]], right: list[list[int]], i: int, j: int) -> int:
    return sum(left[i][k] * right[k][j] for k in range(len(right)))


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


@dataclass
class FamilyStat:
    constraints: int = 0
    variables: int = 0
    clauses: int = 0


class CnfBuilder:
    """Streaming DIMACS builder with exact per-family accounting."""

    def __init__(self, emit_clause: Callable[[tuple[int, ...]], None] | None = None) -> None:
        self.emit_clause = emit_clause
        self.variable_count = 0
        self.clause_count = 0
        self.families: OrderedDict[str, FamilyStat] = OrderedDict()
        self.variable_groups: OrderedDict[str, dict[str, int]] = OrderedDict()

    def _family(self, name: str) -> FamilyStat:
        if name not in self.families:
            self.families[name] = FamilyStat()
        return self.families[name]

    def note_constraint(self, family: str, amount: int = 1) -> None:
        self._family(family).constraints += amount

    def new_var(self, family: str, group: str) -> int:
        self.variable_count += 1
        var = self.variable_count
        self._family(family).variables += 1
        record = self.variable_groups.setdefault(
            group, {"count": 0, "first": var, "last": var, "contiguous": True}
        )
        if record["count"] and var != record["last"] + 1:
            record["contiguous"] = False
        record["count"] += 1
        record["last"] = var
        return var

    def add_clause(self, family: str, literals: Iterable[int]) -> None:
        clause = tuple(int(x) for x in literals)
        if any(x == 0 for x in clause):
            raise ValueError("literal 0 is reserved as the DIMACS terminator")
        if any(abs(x) > self.variable_count for x in clause):
            raise ValueError("clause refers to an unallocated variable")
        self.clause_count += 1
        self._family(family).clauses += 1
        if self.emit_clause is not None:
            self.emit_clause(clause)

    def and2(self, family: str, left: int, right: int, group: str) -> int:
        """Return a fresh variable equivalent to left AND right."""
        out = self.new_var(family, group)
        self.add_clause(family, (-out, left))
        self.add_clause(family, (-out, right))
        self.add_clause(family, (-left, -right, out))
        return out

    def exactly(self, family: str, literals: list[int], target: int) -> None:
        """Encode an exact positive-literal cardinality with threshold states.

        State t(i,j) means that at least j of the first i literals are true.
        The recurrence is encoded as an equivalence, not merely one-way
        propagation.  The terminal units t(n,k) and not t(n,k+1) therefore
        impose equality.
        """
        self.note_constraint(family)
        n = len(literals)
        if target < 0 or target > n:
            self.add_clause(family, ())
            return
        if target == 0:
            for literal in literals:
                self.add_clause(family, (-literal,))
            return
        if target == n:
            for literal in literals:
                self.add_clause(family, (literal,))
            return

        max_threshold = target + 1
        previous: dict[int, int] = {}
        for index, literal in enumerate(literals, start=1):
            current: dict[int, int] = {}
            for threshold in range(1, min(index, max_threshold) + 1):
                out = self.new_var(family, "aux_cardinality")
                a = previous.get(threshold)  # at least threshold before x
                b: int | bool
                if threshold == 1:
                    b = True
                else:
                    b = previous.get(threshold - 1, False)
                self._equiv_or_and(family, out, a if a is not None else False, b, literal)
                current[threshold] = out
            previous = current

        self.add_clause(family, (previous[target],))
        self.add_clause(family, (-previous[target + 1],))

    def _equiv_or_and(
        self,
        family: str,
        out: int,
        a: int | bool,
        b: int | bool,
        x: int,
    ) -> None:
        """Encode out <-> (a OR (b AND x)), simplifying Boolean constants."""
        if a is True:
            self.add_clause(family, (out,))
            return
        if a is False:
            if b is True:
                self.add_clause(family, (-out, x))
                self.add_clause(family, (-x, out))
            elif b is False:
                self.add_clause(family, (-out,))
            else:
                self.add_clause(family, (-out, int(b)))
                self.add_clause(family, (-out, x))
                self.add_clause(family, (-int(b), -x, out))
            return
        if b is True:
            self.add_clause(family, (-out, int(a), x))
            self.add_clause(family, (-int(a), out))
            self.add_clause(family, (-x, out))
            return
        if b is False:
            self.add_clause(family, (-out, int(a)))
            self.add_clause(family, (-int(a), out))
            return
        self.add_clause(family, (-out, int(a), int(b)))
        self.add_clause(family, (-out, int(a), x))
        self.add_clause(family, (-int(a), out))
        self.add_clause(family, (-int(b), -x, out))


def fixed_audit(
    support: list[list[int]], labels: list[dict[str, int]], incidence: list[list[int]]
) -> dict[str, object]:
    """Fail closed on every fixed-cell premise used by the CNF."""
    checks: dict[str, bool] = {}
    checks["support_binary"] = all(x in (0, 1) for row in support for x in row)
    checks["support_symmetric"] = all(
        support[i][j] == support[j][i] for i in range(S_SIZE) for j in range(S_SIZE)
    )
    checks["support_hollow"] = all(support[i][i] == 0 for i in range(S_SIZE))
    checks["support_row_weight_4"] = {sum(row) for row in support} == {4}
    checks["incidence_binary"] = all(x in (0, 1) for row in incidence for x in row)
    checks["incidence_row_weight_10"] = {sum(row) for row in incidence} == {10}
    checks["incidence_column_weight_2"] = {
        sum(incidence[s][o] for s in range(S_SIZE)) for o in range(O_SIZE)
    } == {2}
    checks["O_labels_unique"] = len(
        {(x["point"], x["line"], x["copy"]) for x in labels}
    ) == O_SIZE

    fixed_block_bad: list[list[int]] = []
    for i in range(S_SIZE):
        for j in range(S_SIZE):
            lhs = matrix_product_entry(support, support, i, j) + sum(
                incidence[i][o] * incidence[j][o] for o in range(O_SIZE)
            )
            rhs = 12 * int(i == j) - support[i][j] + 2
            if lhs != rhs:
                fixed_block_bad.append([i, j, lhs, rhs])
    checks["fixed_SS_block"] = not fixed_block_bad
    if not all(checks.values()):
        raise AssertionError({"checks": checks, "fixed_block_bad": fixed_block_bad})

    so_targets: Counter[int] = Counter()
    so_cases: Counter[tuple[int, int, int]] = Counter()
    for s in range(S_SIZE):
        for o in range(O_SIZE):
            asf = sum(
                support[s][t] * incidence[t][o] for t in range(S_SIZE)
            )
            target = 2 - incidence[s][o] - asf
            if target not in (0, 1, 2):
                raise AssertionError(("SO target outside 0..2", s, o, target))
            so_targets[target] += 1
            so_cases[(incidence[s][o], asf, target)] += 1

    ftf_offdiag: Counter[int] = Counter()
    for i in range(O_SIZE):
        for j in range(i + 1, O_SIZE):
            overlap = sum(
                incidence[s][i] * incidence[s][j] for s in range(S_SIZE)
            )
            if overlap not in (0, 1, 2):
                raise AssertionError(("F^T F overlap outside 0..2", i, j, overlap))
            ftf_offdiag[overlap] += 1

    return {
        "checks": checks,
        "fixed_SS_entries_checked": S_SIZE * S_SIZE,
        "support_edge_count": sum(map(sum, support)) // 2,
        "SO_target_histogram": {str(k): so_targets[k] for k in sorted(so_targets)},
        "SO_case_histogram": {
            f"F={key[0]},AS_F={key[1]},target={key[2]}": value
            for key, value in sorted(so_cases.items())
        },
        "FTF_offdiagonal_histogram": {
            str(k): ftf_offdiag[k] for k in sorted(ftf_offdiag)
        },
        "OO_exact_total_target_histogram": {
            str(2 - k): ftf_offdiag[k] for k in sorted(ftf_offdiag, reverse=True)
        },
        "support_adjacency_sha256": sha256_bytes(canonical_bytes(support)),
        "O_labels_sha256": sha256_bytes(canonical_bytes(labels)),
        "support_to_O_incidence_sha256": sha256_bytes(canonical_bytes(incidence)),
    }


def build_encoding(emit_clause: Callable[[tuple[int, ...]], None] | None = None) -> tuple[
    CnfBuilder,
    list[list[int]],
    list[list[int]],
    dict[str, object],
]:
    support, labels, incidence = canonical_fixed_data()
    fixed = fixed_audit(support, labels, incidence)
    builder = CnfBuilder(emit_clause)

    # Primary variables are row-major and contiguous.  A full ordered D is
    # deliberate so symmetry and hollowness are explicit CNF clauses.
    d = [
        [
            builder.new_var("primary_variables", "primary_D")
            for _ in range(O_SIZE)
        ]
        for _ in range(O_SIZE)
    ]
    b = [
        [
            builder.new_var("primary_variables", "primary_B")
            for _ in range(Q_SIZE)
        ]
        for _ in range(O_SIZE)
    ]

    # D is hollow and symmetric.
    for i in range(O_SIZE):
        builder.note_constraint("D_hollow")
        builder.add_clause("D_hollow", (-d[i][i],))
    for i in range(O_SIZE):
        for j in range(i + 1, O_SIZE):
            builder.note_constraint("D_symmetry")
            builder.add_clause("D_symmetry", (-d[i][j], d[j][i]))
            builder.add_clause("D_symmetry", (d[i][j], -d[j][i]))

    # Quotient row constraints: D has row weight 9 and B has row weight 3.
    for i in range(O_SIZE):
        builder.exactly(
            "D_row_weight_9", [d[i][j] for j in range(O_SIZE) if j != i], 9
        )
        builder.exactly("B_row_weight_3", list(b[i]), 3)

    # S-Q block: F B = 2 J.
    for s in range(S_SIZE):
        support_o = [o for o in range(O_SIZE) if incidence[s][o]]
        for q in range(Q_SIZE):
            builder.exactly(
                "SQ_block_FB_equals_2J", [b[o][q] for o in support_o], 2
            )

    # S-O block: A_S F + F D = 2J - F.
    for s in range(S_SIZE):
        support_o = [o for o in range(O_SIZE) if incidence[s][o]]
        for o in range(O_SIZE):
            asf = sum(
                support[s][t] * incidence[t][o] for t in range(S_SIZE)
            )
            target = 2 - incidence[s][o] - asf
            literals = [d[o_prime][o] for o_prime in support_o if o_prime != o]
            builder.exactly("SO_block_ASF_plus_FD", literals, target)

    # O-O diagonal: (F^T F + D^2 + B B^T)[i,i] = 14.
    # Since F columns have weight 2 and Boolean squares equal themselves,
    # this is sum(D row off-diagonal, B row) = 12.
    for i in range(O_SIZE):
        builder.exactly(
            "OO_block_diagonal",
            [d[i][j] for j in range(O_SIZE) if j != i] + list(b[i]),
            12,
        )

    # O-O off diagonal:
    # sum_k D[i,k]D[k,j] + sum_q B[i,q]B[j,q] + D[i,j]
    #     = 2 - (F^T F)[i,j].
    for i in range(O_SIZE):
        for j in range(i + 1, O_SIZE):
            products: list[int] = []
            for k in range(O_SIZE):
                if k in (i, j):
                    continue
                products.append(
                    builder.and2(
                        "OO_block_offdiagonal",
                        d[i][k],
                        d[k][j],
                        "aux_product_DD",
                    )
                )
            for q in range(Q_SIZE):
                products.append(
                    builder.and2(
                        "OO_block_offdiagonal",
                        b[i][q],
                        b[j][q],
                        "aux_product_BB_OO",
                    )
                )
            overlap = sum(
                incidence[s][i] * incidence[s][j] for s in range(S_SIZE)
            )
            builder.exactly(
                "OO_block_offdiagonal", products + [d[i][j]], 2 - overlap
            )

    # O-Q block: D B = 2J - B, or sum D[i,k]B[k,q] + B[i,q] = 2.
    for i in range(O_SIZE):
        for q in range(Q_SIZE):
            products = [
                builder.and2(
                    "OQ_block_DB",
                    d[i][k],
                    b[k][q],
                    "aux_product_DB",
                )
                for k in range(O_SIZE)
                if k != i
            ]
            builder.exactly("OQ_block_DB", products + [b[i][q]], 2)

    # Q-Q diagonal and off diagonal: B^T B = 12I + 2J.
    for q in range(Q_SIZE):
        builder.exactly(
            "QQ_block_column_weight_14", [b[o][q] for o in range(O_SIZE)], 14
        )
    for q in range(Q_SIZE):
        for r in range(q + 1, Q_SIZE):
            products = [
                builder.and2(
                    "QQ_block_pair_intersection_2",
                    b[o][q],
                    b[o][r],
                    "aux_product_BB_QQ",
                )
                for o in range(O_SIZE)
            ]
            builder.exactly("QQ_block_pair_intersection_2", products, 2)

    return builder, d, b, {
        "fixed": fixed,
        "O_labels": labels,
        "support": support,
        "incidence": incidence,
    }


def primary_map(d: list[list[int]], b: list[list[int]], labels: list[dict[str, int]]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "D": {
            "shape": [O_SIZE, O_SIZE],
            "layout": "row-major full ordered matrix",
            "first_variable": d[0][0],
            "last_variable": d[-1][-1],
            "formula": "var(D[i,j]) = 1 + 70*i + j",
            "symmetry": "explicit equivalence clauses",
            "diagonal": "explicit negative unit clauses",
        },
        "B": {
            "shape": [O_SIZE, Q_SIZE],
            "layout": "row-major",
            "first_variable": b[0][0],
            "last_variable": b[-1][-1],
            "formula": "var(B[i,q]) = 4901 + 15*i + q",
        },
        "vertex_order": {
            "S": [0, 13],
            "O": [14, 83],
            "Q": [84, 98],
            "O_labels": labels,
        },
    }


def semantic_inventory() -> dict[str, object]:
    return {
        "primary_binary_variables": {
            "D_ordered_entries": O_SIZE * O_SIZE,
            "B_entries": O_SIZE * Q_SIZE,
            "total": O_SIZE * O_SIZE + O_SIZE * Q_SIZE,
        },
        "structural_constraints": {
            "D_hollow_units": O_SIZE,
            "D_symmetry_pairs": O_SIZE * (O_SIZE - 1) // 2,
            "Q_Q_fixed_zero_entries": Q_SIZE * Q_SIZE,
            "S_Q_fixed_zero_entries": S_SIZE * Q_SIZE,
        },
        "quotient_constraints": {
            "D_row_weight_9": O_SIZE,
            "B_row_weight_3": O_SIZE,
        },
        "six_blocks": {
            "SS_fixed_entries_checked": S_SIZE * S_SIZE,
            "SQ_FB_equals_2J": S_SIZE * Q_SIZE,
            "SO_ASF_plus_FD_equals_2J_minus_F": S_SIZE * O_SIZE,
            "OO_diagonal": O_SIZE,
            "OO_offdiagonal_unique": O_SIZE * (O_SIZE - 1) // 2,
            "OQ_DB_equals_2J_minus_B": O_SIZE * Q_SIZE,
            "QQ_diagonal": Q_SIZE,
            "QQ_offdiagonal_unique": Q_SIZE * (Q_SIZE - 1) // 2,
        },
        "coverage": {
            "automorphism_assumed": False,
            "fixed_OQ_design_assumed": False,
            "D_domain": "all labeled symmetric hollow binary 70x70 matrices",
            "B_domain": "all labeled binary 70x15 matrices",
            "symmetric_matrix_entries_encoded_once": "OO and QQ off-diagonal equations",
            "omitted_zero_terms": "D diagonal products only; D[i,i]=0 is explicitly encoded",
        },
    }


def criterion_specification(fixed_data: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "claim_label": "CANDIDATE",
        "scope": "complete unrestricted labeled rooted six-block binary graph-extension criterion",
        "sizes": {"S": S_SIZE, "O": O_SIZE, "Q": Q_SIZE, "total": 99},
        "notation": {
            "A_S": "fixed 14x14 support adjacency",
            "F": "fixed 14x70 support-to-O incidence",
            "D": "unknown symmetric hollow binary 70x70 O-O adjacency",
            "B": "unknown binary 70x15 O-Q incidence",
        },
        "full_adjacency_block_matrix": [
            ["A_S", "F", "0_(14x15)"],
            ["F^T", "D", "B"],
            ["0_(15x14)", "B^T", "0_(15x15)"],
        ],
        "fixed": {
            "Fano_lines": [list(line) for line in FANO_LINES],
            "support_vertex_order": [
                *[f"P{point}" for point in range(7)],
                *[f"L{line}" for line in range(7)],
            ],
            "O_labels": fixed_data["O_labels"],
            "A_S_rows": ["".join(map(str, row)) for row in fixed_data["support"]],
            "F_rows": ["".join(map(str, row)) for row in fixed_data["incidence"]],
            "S_Q": "all zero",
            "Q_Q": "all zero",
        },
        "domain": {
            "D_entries_binary": True,
            "D_symmetric": True,
            "D_diagonal_zero": True,
            "B_entries_binary": True,
            "automorphism_or_orbit_restriction": False,
            "fixed_B_design": False,
        },
        "row_and_column_constraints": {
            "A_S_row_weight": 4,
            "F_row_weight": 10,
            "F_column_weight": 2,
            "D_row_weight": 9,
            "B_row_weight": 3,
            "B_column_weight": 14,
        },
        "six_integer_block_equations": [
            {
                "block": "SS",
                "shape": [14, 14],
                "equation": "A_S^2 + F F^T = 12 I_14 - A_S + 2 J_14",
                "mode": "fixed entrywise generator assertion",
            },
            {
                "block": "SQ",
                "shape": [14, 15],
                "equation": "F B = 2 J_(14,15)",
                "mode": "210 exact-cardinality constraints",
            },
            {
                "block": "SO",
                "shape": [14, 70],
                "equation": "A_S F + F D = 2 J_(14,70) - F",
                "mode": "980 exact-cardinality constraints",
            },
            {
                "block": "OO",
                "shape": [70, 70],
                "equation": "F^T F + D^2 + B B^T = 12 I_70 - D + 2 J_70",
                "mode": "70 diagonal plus 2415 unique off-diagonal constraints",
            },
            {
                "block": "OQ",
                "shape": [70, 15],
                "equation": "D B = 2 J_(70,15) - B",
                "mode": "1050 exact-cardinality constraints",
            },
            {
                "block": "QQ",
                "shape": [15, 15],
                "equation": "B^T B = 12 I_15 + 2 J_15",
                "mode": "15 diagonal plus 105 unique off-diagonal constraints",
            },
        ],
        "linearization": {
            "product": "fresh y with clauses (-y or x), (-y or z), (-x or -z or y)",
            "cardinality": "equivalent threshold recurrence plus exact terminal units",
            "fixed_zero_product_terms_omitted": "only terms containing explicit D[i,i]=0",
        },
        "certificate_requirements": {
            "SAT": "full 99x99 graph reconstructed and independently checked",
            "UNSAT": "proof-producing complete-domain proof checked against the exact CNF and an independently audited mapping",
        },
    }


def audit_document(builder: CnfBuilder, fixed_data: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "status": "ENCODING_COUNT_AUDIT_ONLY",
        "claim_label": "CANDIDATE",
        "domain": semantic_inventory(),
        "fixed_data": fixed_data["fixed"],
        "cnf": {
            "variables": builder.variable_count,
            "clauses": builder.clause_count,
            "families": {
                name: {
                    "semantic_constraints": stat.constraints,
                    "variables": stat.variables,
                    "clauses": stat.clauses,
                }
                for name, stat in builder.families.items()
            },
            "variable_groups": builder.variable_groups,
            "cardinality_encoding": "equivalent threshold recurrence t(i,j) with exact terminal units",
            "and_encoding": "three-clause Tseitin equivalence y iff (x and z)",
        },
        "certificate_paths": {
            "SAT": [
                "complete DIMACS assignment",
                "decode_model.py emits full 99x99 adjacency JSON",
                "check_witness.py independently checks fixed partition, six blocks, and A^2=12I-A+2J",
            ],
            "UNSAT": [
                "proof-producing solver runs on the exact SHA-256-pinned DIMACS",
                "proof artifact must be LRAT or another independently checkable complete proof",
                "external solver and proof-checker source/version/hash must be recorded before execution",
                "proof checker must accept the exact formula; solver exit code alone is rejected",
            ],
        },
        "limitations": [
            "This audit counts an exact formula; it is not a SAT or UNSAT result.",
            "No symmetry breaking is present.",
            "No fixed 2-(15,3,2) design is selected.",
        ],
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def dimacs_emitter(handle: TextIO) -> Callable[[tuple[int, ...]], None]:
    def emit(clause: tuple[int, ...]) -> None:
        if clause:
            handle.write(" ".join(str(x) for x in clause))
            handle.write(" 0\n")
        else:
            handle.write("0\n")

    return emit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--primary-map", type=Path, required=True)
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    if args.audit_only and args.output is not None:
        parser.error("--audit-only and --output are mutually exclusive")
    if not args.audit_only and args.output is None:
        parser.error("either --audit-only or --output is required")
    return args


def main() -> int:
    args = parse_args()
    counted, d, b, fixed_data = build_encoding()
    audit = audit_document(counted, fixed_data)
    pmap = primary_map(d, b, fixed_data["O_labels"])
    spec = criterion_specification(fixed_data)

    if args.audit_only:
        write_json(args.audit, audit)
        write_json(args.primary_map, pmap)
        if args.spec:
            write_json(args.spec, spec)
        print(
            json.dumps(
                {
                    "mode": "audit-only",
                    "variables": counted.variable_count,
                    "clauses": counted.clause_count,
                    "audit": str(args.audit),
                    "primary_map": str(args.primary_map),
                },
                sort_keys=True,
            )
        )
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {counted.variable_count} {counted.clause_count}\n")
        emitted, d2, b2, fixed_data2 = build_encoding(dimacs_emitter(handle))
    if (emitted.variable_count, emitted.clause_count) != (
        counted.variable_count,
        counted.clause_count,
    ):
        raise AssertionError("count and emission passes disagree")
    if d != d2 or b != b2 or fixed_data != fixed_data2:
        raise AssertionError("count and emission metadata disagree")

    formula_hash = hashlib.sha256(args.output.read_bytes()).hexdigest()
    audit["status"] = "COMPLETE_DIMACS_EMITTED"
    audit["cnf"]["path"] = args.output.name
    audit["cnf"]["sha256"] = formula_hash
    audit["cnf"]["bytes"] = args.output.stat().st_size
    write_json(args.audit, audit)
    write_json(args.primary_map, pmap)
    if args.spec:
        write_json(args.spec, spec)
    print(
        json.dumps(
            {
                "mode": "emit",
                "variables": counted.variable_count,
                "clauses": counted.clause_count,
                "bytes": args.output.stat().st_size,
                "sha256": formula_hash,
                "output": str(args.output),
                "audit": str(args.audit),
                "primary_map": str(args.primary_map),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
