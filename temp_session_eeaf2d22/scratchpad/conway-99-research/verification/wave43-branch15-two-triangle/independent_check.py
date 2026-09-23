#!/usr/bin/env python3
"""Clean-room verifier for the Wave 43 two-coordinate-triangle reduction.

No Wave 43 discovery module is imported.  The checker streams the frozen
OPB components, reconstructs the rooted scaffold and all coordinate triangles,
replays closure and bounded probes, and compares complete clause catalogues.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import re
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = ROOT / "attempts/wave37-proof-producing-endpoint/branch-15.opb.gz"
W42 = ROOT / "attempts/wave42-endpoint-certificate/branch-15-seventh-triangle-delta.opb.gz"
W42_CERT = ROOT / "attempts/wave42-endpoint-certificate/branch-15-combined-propagation-certificate.json"
DISC = ROOT / "attempts/wave43-branch15-two-triangle"
RAW_CAT = DISC / "branch-15-two-coordinate-triangle-delta.opb.gz"
ACTIVE_CAT = DISC / "branch-15-two-coordinate-triangle-active-delta.opb.gz"
DISC_RESULT = DISC / "branch-15-two-coordinate-triangle-result.json"
DISC_CLOSURE = DISC / "branch-15-two-coordinate-triangle-closure.json"
DISC_PROBES = DISC / "branch-15-two-coordinate-triangle-probes.json"

HASHES = {
    BASE: ("7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e",
           "4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5", 574_615),
    W42: ("0840524515920a59fd3d0f0666b496f9e639476dd887d0d90df5bb58a9e8904e",
          "348dc5f4bc9ee99511286a8078d0e4ef79786b57ba39ae572c032e42747be77e", 64_932),
    RAW_CAT: ("82a13e78e514cf35f27190da665bdedaf4fed28c7a6fa2856e22badf63f32797",
              "23fc3b22b4b235cc631bfd0b53ed2806394273aa1b4c691c883ebe343788d3f1", 40_800),
    ACTIVE_CAT: ("858f2a5c66d251497e4c13fb4d633c18fe65afe657937b84444cde55b1a4a631",
                 "0ed3c553d6323632b0466157f0eb7e18cb7597a16ce8eca6654d086c70314476", 34_340),
}
JSON_HASHES = {
    W42_CERT: "ab05feb596c25d0fbb872a0d92978355638218350bdf7606c248ca98ae2469ce",
    DISC_RESULT: "1ab1cc6ad5a3727fec508b8b3f2eb9b52d4034f6aa6768b25feef8f219c45ec8",
    DISC_CLOSURE: "a695b65631d5b6c2ce8f22754fb097428101fca10b443e8452061876f508d31f",
    DISC_PROBES: "4bf195563e7e40b5dd7b5b1228932ca7a6d36426b690a6c826d2e9d0634bcac4",
}

HEADER = re.compile(rb"^\* #variable= ([1-9][0-9]*) #constraint= ([1-9][0-9]*)\n$")
TERM = re.compile(rb"\+1 (~)?x([1-9][0-9]*)")
BOUND = re.compile(rb">= ([0-9]+) ;\n$")
Constraint = tuple[tuple[tuple[int, bool], ...], int]
Clause = tuple[int, ...]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def strict_json(path: Path, expected: str | None = None) -> dict[str, object]:
    raw = path.read_bytes()
    if expected is not None and digest(raw) != expected:
        raise ValueError(f"JSON hash mismatch: {path}")

    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        out: dict[str, object] = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r}")
            out[key] = value
        return out

    result = json.loads(raw, object_pairs_hook=unique)
    if not isinstance(result, dict):
        raise ValueError(f"top-level JSON is not an object: {path}")
    return result


def parse_row(line: bytes) -> Constraint:
    match = BOUND.search(line)
    if match is None:
        raise ValueError("unsupported OPB row")
    literals = tuple((int(x.group(2)), x.group(1) is None) for x in TERM.finditer(line))
    rebuilt = b" ".join(
        (b"+1 x" if sign else b"+1 ~x") + str(var).encode()
        for var, sign in literals
    ) + b" >= " + match.group(1) + b" ;\n"
    if rebuilt != line or not literals or len({v for v, _ in literals}) != len(literals):
        raise ValueError("noncanonical or repeated-literal OPB row")
    return literals, int(match.group(1))


def visit_formula(
    path: Path,
    visitor: Callable[[int, bytes, Constraint], None],
    *,
    bind_hash: bool = False,
) -> None:
    expected_gz, expected_raw, expected_rows = HASHES[path]
    packed = path.read_bytes()
    if bind_hash and digest(packed) != expected_gz:
        raise ValueError(f"gzip hash mismatch: {path}")
    raw_hash = hashlib.sha256()
    count = 0
    with gzip.open(path, "rb") as stream:
        header = stream.readline()
        raw_hash.update(header)
        hm = HEADER.fullmatch(header)
        if hm is None or int(hm.group(1)) != 289_338 or int(hm.group(2)) != expected_rows:
            raise ValueError(f"bad OPB header: {path}")
        for count, line in enumerate(stream, 1):
            raw_hash.update(line)
            visitor(count, line, parse_row(line))
    if count != expected_rows:
        raise ValueError(f"OPB row count mismatch: {path}")
    if bind_hash and raw_hash.hexdigest() != expected_raw:
        raise ValueError(f"raw OPB hash mismatch: {path}")


def evaluate(constraint: Constraint, assignment: dict[int, bool]) -> tuple[str, list[tuple[int, bool]]]:
    literals, lower = constraint
    true_count = 0
    open_lits: list[tuple[int, bool]] = []
    for variable, sign in literals:
        value = assignment.get(variable)
        if value is None:
            open_lits.append((variable, sign))
        elif value is sign:
            true_count += 1
    maximum = true_count + len(open_lits)
    if maximum < lower:
        return "CONTRADICTION", []
    if open_lits and maximum == lower:
        return "FORCE", open_lits
    return "OPEN", []


def replay_base_closure() -> tuple[dict[int, bool], list[dict[str, int]]]:
    assignments: dict[int, bool] = {}
    passes: list[dict[str, int]] = []
    for pass_no in itertools.count(1):
        before = len(assignments)

        def take(_row: int, _raw: bytes, constraint: Constraint) -> None:
            state, forced = evaluate(constraint, assignments)
            if state == "CONTRADICTION":
                raise ValueError("contradiction during clean-room closure")
            for variable, value in forced:
                prior = assignments.get(variable)
                if prior is not None and prior is not value:
                    raise ValueError("closure assignment conflict")
                assignments.setdefault(variable, value)

        visit_formula(BASE, take, bind_hash=pass_no == 1)
        visit_formula(W42, take, bind_hash=pass_no == 1)
        passes.append({"pass": pass_no, "before": before, "after": len(assignments),
                       "new": len(assignments) - before})
        if len(assignments) == before:
            break
    if len(assignments) != 830:
        raise ValueError(f"closure size {len(assignments)} != 830")
    cert = strict_json(W42_CERT, JSON_HASHES[W42_CERT])
    derivations = cert.get("derivations")
    if not isinstance(derivations, list):
        raise ValueError("Wave 42 certificate has no derivations")
    archived = {int(x["variable"]): bool(x["value"]) for x in derivations if isinstance(x, dict)}
    if archived != assignments:
        raise ValueError("clean-room closure differs from Wave 42 assignment catalogue")
    return assignments, passes


def scaffold() -> tuple[list[tuple[int, int]], dict[tuple[int, int], int]]:
    labels = [p for p in itertools.combinations(range(14), 2) if p[1] != (p[0] ^ 1)]
    ids = {p: i for i, p in enumerate(itertools.combinations(range(84), 2), 1)}
    if len(labels) != 84 or len(ids) != 3_486:
        raise AssertionError("rooted scaffold cardinality failed")
    return labels, ids


def edge_value(
    u: int, v: int, labels: Sequence[tuple[int, int]], ids: dict[tuple[int, int], int]
) -> bool | int:
    if u > v:
        u, v = v, u
    if u == v:
        raise ValueError("loop")
    if u == 0:
        return v <= 14
    if v <= 14:
        return (v - 1) == ((u - 1) ^ 1)
    if u <= 14:
        return (u - 1) in labels[v - 15]
    return ids[(u - 15, v - 15)]


def coordinate_catalogue(
    labels: Sequence[tuple[int, int]], ids: dict[tuple[int, int], int]
) -> list[tuple[int, int, int, int]]:
    out: list[tuple[int, int, int, int]] = []
    for coordinate in range(14):
        fibre = [i for i, pair in enumerate(labels) if coordinate in pair]
        if len(fibre) != 12:
            raise AssertionError("coordinate fibre is not 12")
        for left, right in itertools.combinations(fibre, 2):
            out.append((1 + coordinate, 15 + left, 15 + right, ids[(left, right)]))
    if len(out) != 924 or len(set(out)) != 924:
        raise AssertionError("coordinate triangle catalogue failed")
    return out


def enumerate_clauses(assignments: dict[int, bool]) -> tuple[tuple[Clause, ...], dict[str, int]]:
    labels, ids = scaffold()
    all_triangles = coordinate_catalogue(labels, ids)
    eligible = [triangle for triangle in all_triangles if triangle[3] not in assignments]
    counts = Counter(
        "true" if assignments.get(t[3]) is True else
        "false" if assignments.get(t[3]) is False else "unfixed"
        for t in all_triangles
    )
    clauses: set[Clause] = set()
    pair_visits = disjoint = mate_pairs = matching_visits = killed = accepted = 0
    accepted_mate = accepted_anchor = 0
    for index, left in enumerate(eligible):
        lv = left[:3]
        ls = set(lv)
        for right in eligible[index + 1:]:
            pair_visits += 1
            rv = right[:3]
            if ls.intersection(rv):
                continue
            disjoint += 1
            mate = (left[0] - 1) // 2 == (right[0] - 1) // 2
            mate_pairs += int(mate)
            for order in itertools.permutations(rv):
                matching_visits += 1
                edges = list(itertools.combinations(lv, 2))
                edges += list(itertools.combinations(rv, 2))
                edges += list(zip(lv, order))
                needed: set[int] = set()
                impossible = False
                for u, v in edges:
                    state = edge_value(u, v, labels, ids)
                    if state is False:
                        impossible = True
                        break
                    if type(state) is int:
                        needed.add(state)
                if impossible:
                    killed += 1
                    continue
                accepted += 1
                accepted_mate += int(mate)
                accepted_anchor += int(order[0] == right[0])
                clause = tuple(sorted(needed))
                if left[3] not in clause or right[3] not in clause or len(clause) != 4:
                    raise AssertionError("accepted cut is not the required four-variable cut")
                clauses.add(clause)
    ordered = tuple(sorted(clauses))
    return ordered, {
        "coordinate_triangles": len(all_triangles),
        "true": counts["true"], "false": counts["false"], "unfixed": counts["unfixed"],
        "pair_visits": pair_visits, "disjoint_pairs": disjoint, "mate_anchor_pairs": mate_pairs,
        "matching_visits": matching_visits, "killed": killed, "accepted": accepted,
        "accepted_mate": accepted_mate, "accepted_anchor": accepted_anchor,
        "distinct_clauses": len(ordered),
    }


def catalogue_hash(clauses: Sequence[Clause]) -> str:
    compact = json.dumps([list(c) for c in clauses], separators=(",", ":")).encode("ascii")
    return digest(compact)


def opb_bytes(clauses: Sequence[Clause]) -> bytes:
    lines = [f"* #variable= 289338 #constraint= {len(clauses)}"]
    lines.extend(" ".join(f"+1 ~x{v}" for v in c) + " >= 1 ;" for c in clauses)
    return ("\n".join(lines) + "\n").encode("ascii")


def simplify(clauses: Sequence[Clause], assignments: dict[int, bool]) -> tuple[tuple[Clause, ...], int]:
    active: set[Clause] = set()
    satisfied = 0
    for clause in clauses:
        if any(assignments.get(v) is False for v in clause):
            satisfied += 1
            continue
        residual = tuple(v for v in clause if assignments.get(v) is not True)
        if not residual:
            raise ValueError("new catalogue contradicts closure")
        active.add(residual)
    return tuple(sorted(active)), satisfied


def read_negative_catalogue(path: Path) -> tuple[Clause, ...]:
    out: list[Clause] = []

    def take(_row: int, _raw: bytes, constraint: Constraint) -> None:
        literals, lower = constraint
        if lower != 1 or any(sign for _, sign in literals):
            raise ValueError(f"catalogue contains nonnegative row: {path}")
        out.append(tuple(v for v, _ in literals))

    visit_formula(path, take, bind_hash=True)
    if out != sorted(set(out)):
        raise ValueError(f"catalogue is not strictly sorted and unique: {path}")
    return tuple(out)


def prior_overlap(clauses: set[Clause]) -> tuple[int, int]:
    base_negative = 0
    overlap = 0

    def take(_row: int, _raw: bytes, constraint: Constraint) -> None:
        nonlocal base_negative, overlap
        literals, lower = constraint
        if lower == 1 and all(not sign for _, sign in literals):
            base_negative += 1
            overlap += tuple(sorted(v for v, _ in literals)) in clauses

    visit_formula(BASE, take)
    visit_formula(W42, take)
    return base_negative, overlap


def probe_replay(
    closure: dict[int, bool], raw_clauses: Sequence[Clause], active: Sequence[Clause]
) -> tuple[list[dict[str, object]], list[dict[str, int]], list[int]]:
    labels, ids = scaffold()
    controllers = {
        t[3] for t in coordinate_catalogue(labels, ids) if t[3] not in closure
    }
    incidence = Counter(v for clause in active for v in clause if v in controllers)
    selected = [v for v, _ in sorted(incidence.items(), key=lambda item: (-item[1], item[0]))[:32]]
    selection = [{"variable": v, "active_cut_occurrences": incidence[v]} for v in selected]
    states = [
        {"variable": v, "assumed_value": value, "assignment": {**closure, v: value},
         "fixed": False, "contradiction": None, "passes": [], "derivations": []}
        for v in selected for value in (False, True)
    ]
    generated = [
        ("two_coordinate_triangle_delta", i, (
            " ".join(f"+1 ~x{v}" for v in clause) + " >= 1 ;\n"
        ).encode("ascii"), (tuple((v, False) for v in clause), 1))
        for i, clause in enumerate(raw_clauses, 1)
    ]
    for pass_no in itertools.count(1):
        live = [state for state in states if not state["fixed"]]
        if not live:
            break
        starts = {id(s): len(s["assignment"]) for s in live}
        scans = {id(s): {"base": 0, "wave42": 0, "coordinate": 0} for s in live}

        def process(kind: str, row: int, raw: bytes, constraint: Constraint) -> None:
            for state in states:
                if state["fixed"]:
                    continue
                key = "base" if kind == "base_opb" else "wave42" if kind == "seventh_triangle_delta" else "coordinate"
                scans[id(state)][key] += 1
                outcome, forced = evaluate(constraint, state["assignment"])
                if outcome == "CONTRADICTION":
                    state["contradiction"] = {
                        "pass": pass_no, "source_kind": kind, "source_row": row,
                        "source_row_sha256": digest(raw),
                    }
                    state["fixed"] = True
                    continue
                for variable, value in forced:
                    prior = state["assignment"].get(variable)
                    if prior is not None:
                        if prior is not value:
                            raise ValueError("probe assignment conflict")
                        continue
                    state["assignment"][variable] = value
                    literals, lower = constraint
                    state["derivations"].append({
                        "index": len(state["derivations"]) + 1, "pass": pass_no,
                        "variable": variable, "value": value, "source_kind": kind,
                        "source_row": row, "source_row_sha256": digest(raw),
                        "source_term_count": len(literals), "source_bound": lower,
                    })

        # Discovery records physical OPB line numbers for the base (header is
        # line 1), while generated delta catalogues use one-based row numbers.
        visit_formula(BASE, lambda row, raw, c: process("base_opb", row + 1, raw, c))
        visit_formula(W42, lambda row, raw, c: process("seventh_triangle_delta", row, raw, c))
        for kind, row, raw, constraint in generated:
            process(kind, row, raw, constraint)
        for state in states:
            if id(state) not in starts:
                continue
            start, end = starts[id(state)], len(state["assignment"])
            state["passes"].append({
                "pass": pass_no, "assignments_before": start, "assignments_after": end,
                "new_assignments": end - start,
                "base_constraints_scanned": scans[id(state)]["base"],
                "wave42_constraints_scanned": scans[id(state)]["wave42"],
                "coordinate_constraints_scanned": scans[id(state)]["coordinate"],
            })
            if not state["fixed"] and start == end:
                state["fixed"] = True
    records: list[dict[str, object]] = []
    for state in states:
        derivations = state["derivations"]
        sourced = sum(d["source_kind"] == "two_coordinate_triangle_delta" for d in derivations)
        records.append({
            "variable": state["variable"], "assumed_value": state["assumed_value"],
            "status": "CANDIDATE_CONTRADICTION" if state["contradiction"] else "PROPAGATION_FIXED_POINT_NO_CONCLUSION",
            "contradiction": state["contradiction"], "new_forced_variables": len(derivations),
            "coordinate_delta_sourced_derivations": sourced,
            "passes": state["passes"], "derivations": derivations,
        })
    return records, selection, selected


def compute() -> dict[str, object]:
    closure, closure_passes = replay_base_closure()
    clauses, census = enumerate_clauses(closure)
    active, satisfied = simplify(clauses, closure)
    raw_archived = read_negative_catalogue(RAW_CAT)
    active_archived = read_negative_catalogue(ACTIVE_CAT)
    base_negative, overlap = prior_overlap(set(clauses))
    records, selection, selected = probe_replay(closure, clauses, active)
    archived_probes = strict_json(DISC_PROBES, JSON_HASHES[DISC_PROBES])
    raw_payload = opb_bytes(clauses)
    active_payload = opb_bytes(active)
    result = {
        "format": "wave43-branch15-two-triangle-independent-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED",
        "scope": "complete two-coordinate-triangle cut family and 64 bounded probes in frozen branch 15, conditional on n3=4158",
        "inputs": {
            path.relative_to(ROOT).as_posix(): {"gzip_sha256": HASHES[path][0], "raw_sha256": HASHES[path][1]}
            for path in (BASE, W42)
        },
        "closure": {
            "passes": closure_passes, "forced_variables": len(closure),
            "forced_primary_variables": sum(v <= 3486 for v in closure),
            "assignment_stream_sha256": digest(b"".join(
                f"{v}={int(closure[v])}\n".encode() for v in sorted(closure)
            )),
            "exactly_matches_wave42_certificate": True,
        },
        "enumeration": census,
        "raw": {
            "count": len(clauses), "widths": dict(Counter(map(len, clauses))),
            "catalog_sha256": catalogue_hash(clauses), "opb_sha256": digest(raw_payload),
            "deterministic_gzip_sha256": digest(gzip.compress(raw_payload, compresslevel=9, mtime=0)),
            "prior_all_negative_rows_scanned": base_negative, "prior_exact_overlap": overlap,
            "archived_exact_match": clauses == raw_archived,
        },
        "active": {
            "count": len(active), "satisfied": satisfied,
            "widths": dict(Counter(map(len, active))),
            "catalog_sha256": catalogue_hash(active), "opb_sha256": digest(active_payload),
            "deterministic_gzip_sha256": digest(gzip.compress(active_payload, compresslevel=9, mtime=0)),
            "all_slack_three": all(len(c) == 4 and all(v not in closure for v in c) for c in active),
            "archived_exact_match": active == active_archived,
        },
        "probes": {
            "selected": selected, "selection": selection, "records": records,
            "records_exact_match": records == archived_probes.get("records"),
            "selection_exact_match": selection == archived_probes.get("selection"),
            "zero_failed_polarities": all(r["contradiction"] is None for r in records),
            "zero_coordinate_sourced_derivations": all(r["coordinate_delta_sourced_derivations"] == 0 for r in records),
        },
        "result": {
            "branch_15": "UNKNOWN", "endpoint_cases_closed": 0,
            "endpoint_cases_total": 33, "endpoint_excluded": False,
            "strict_upper_bound": "NOT_PROVED", "conway_99": "UNKNOWN",
        },
        "limitations": [
            "Completeness is only for pairs of coordinate-anchored triangles unfixed at the frozen closure.",
            "Prisms involving a triangle without a coordinate anchor remain omitted.",
            "A propagation fixed point is neither SAT nor UNSAT evidence.",
            "The bounded probes cover only 32 selected controller variables.",
            "No automorphism of a completed graph is assumed.",
        ],
    }
    validate(result)
    return result


def validate(value: dict[str, object]) -> None:
    enum = value["enumeration"]
    expected = {
        "coordinate_triangles": 924, "true": 7, "false": 157, "unfixed": 760,
        "pair_visits": 288420, "disjoint_pairs": 259499, "mate_anchor_pairs": 20400,
        "matching_visits": 1556994, "killed": 1516194, "accepted": 40800,
        "accepted_mate": 40800, "accepted_anchor": 40800, "distinct_clauses": 40800,
    }
    if enum != expected:
        raise ValueError(f"enumeration mismatch: {enum}")
    raw, active, probes = value["raw"], value["active"], value["probes"]
    if raw["catalog_sha256"] != "cafd0eddbc8371d59f7fb184b51f6a6facdeee9d1a50bbea7b30b95e2fa2b462":
        raise ValueError("raw catalogue digest mismatch")
    if active["catalog_sha256"] != "8c8afac5833ce5a2739fa6043d255adae5e3eb52b6bc75799fcd2ce86d297bf8":
        raise ValueError("active catalogue digest mismatch")
    if raw["count"] != 40800 or raw["prior_exact_overlap"] != 0 or not raw["archived_exact_match"]:
        raise ValueError("raw catalogue comparison failed")
    if active["count"] != 34340 or active["satisfied"] != 6460 or not active["all_slack_three"] or not active["archived_exact_match"]:
        raise ValueError("active catalogue comparison failed")
    if not all(probes[key] for key in (
        "records_exact_match", "selection_exact_match", "zero_failed_polarities",
        "zero_coordinate_sourced_derivations",
    )):
        summary = {
            key: probes[key]
            for key in (
                "records_exact_match", "selection_exact_match",
                "zero_failed_polarities", "zero_coordinate_sourced_derivations",
            )
        }
        if not probes["records_exact_match"]:
            archived_records = strict_json(DISC_PROBES, JSON_HASHES[DISC_PROBES]).get("records")
            first = next(
                (
                    (index, observed, archived)
                    for index, (observed, archived) in enumerate(
                        zip(probes["records"], archived_records, strict=True)
                    )
                    if observed != archived
                ),
                None,
            )
            summary["first_record_difference"] = first
        raise ValueError(f"bounded probe replay mismatch: {summary}")
    if value["result"] != {
        "branch_15": "UNKNOWN", "endpoint_cases_closed": 0,
        "endpoint_cases_total": 33, "endpoint_excluded": False,
        "strict_upper_bound": "NOT_PROVED", "conway_99": "UNKNOWN",
    }:
        raise ValueError("status wall mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    observed = compute()
    payload = canonical(observed)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    else:
        expected = strict_json(args.verify)
        validate(expected)
        if payload != canonical(expected):
            raise ValueError("archived independent result differs from live replay")
    print("PASS: clean-room branch-15 two-triangle replay")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
