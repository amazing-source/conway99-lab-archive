#!/usr/bin/env python3
"""Independent semantic and byte-level audit of branch-15.opb.

The checker imports no discovery exporter.  It uses the separate independent
rooted-branch verifier to reconstruct the combinatorial branch data, then
streams an exact expected OPB formula and compares every line.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import itertools
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Iterator, Sequence


VARIABLES = 289_338
CLAUSES = 568_777
ATMOSTS = 5_838
CONSTRAINTS = CLAUSES + ATMOSTS
EDGE_VARIABLES = 3_486
WEDGE_VARIABLES = 285_852
EXPECTED_OPB_SHA = "4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5"
EXPECTED_GZIP_SHA = "7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e"
PINNED_EXACT_SHA = "842ac70b4e938d24f537a56513ff64ea845206c714ce34da467ce146c5c5c928"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def rooted():
    path = (
        repository_root()
        / "verification/wave37-rooted-branches/independent_check.py"
    )
    spec = importlib.util.spec_from_file_location(
        "wave37_independent_rooted_for_opb", path
    )
    require(spec is not None and spec.loader is not None,
            "cannot load independent rooted verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def literal_text(literal: int) -> str:
    return f"x{literal}" if literal > 0 else f"~x{-literal}"


def lower_bound(literals: Sequence[int], bound: int) -> bytes:
    terms = " ".join(f"+1 {literal_text(literal)}" for literal in literals)
    return f"{terms} >= {bound} ;\n".encode("ascii")


@lru_cache(maxsize=1)
def wedge_variables() -> dict[tuple[int, int, int], int]:
    answer = {}
    variable = EDGE_VARIABLES + 1
    for first, second in itertools.combinations(range(84), 2):
        for center in range(84):
            if center in (first, second):
                continue
            answer[(first, second, center)] = variable
            variable += 1
    require(variable - 1 == VARIABLES, "wedge-variable range changed")
    return answer


def edge_literal(first: int, second: int) -> int:
    if first > second:
        first, second = second, first
    return rooted().edge_variables()[(first, second)]


def wedge_implication_lines() -> Iterator[bytes]:
    for (first, second, center), wedge in wedge_variables().items():
        yield lower_bound(
            [-edge_literal(first, center), -edge_literal(second, center), wedge],
            1,
        )


def branch_15_data() -> tuple[int, tuple[int, int], int]:
    matching, endpoint, _ = rooted().refined_orbits()[14]
    parent = rooted().parent_number_for_matching(matching)
    indices = rooted().label_index()
    first_label = indices[(0, 2)]
    second_label = indices[tuple(sorted((4, endpoint)))]
    edge = tuple(sorted((first_label, second_label)))
    return parent, edge, rooted().edge_variables()[edge]


def branch_unit_lines() -> Iterator[bytes]:
    variables = rooted().edge_variables()
    for edge in rooted().endpoint_edges():
        yield lower_bound([-variables[edge]], 1)
    indices = rooted().label_index()
    normalization = tuple(sorted((indices[(0, 2)], indices[(2, 4)])))
    yield lower_bound([variables[normalization]], 1)
    parent, _, refinement_literal = branch_15_data()
    for edge, present in rooted().branch_decisions(parent).items():
        if edge == normalization:
            continue
        variable = variables[edge]
        yield lower_bound([variable if present else -variable], 1)
    yield lower_bound([refinement_literal], 1)


def prism_lines() -> Iterator[bytes]:
    _, clauses = rooted().catalog_record(4)
    for clause in clauses:
        yield lower_bound(clause, 1)


def incidence_target(coordinate: int, label_index: int) -> int:
    label = rooted().labels()[label_index]
    return 2 - int(coordinate in label) - int((coordinate ^ 1) in label)


def coordinate_atmost_lines() -> Iterator[bytes]:
    for label_index in range(84):
        for coordinate in range(14):
            literals = [
                edge_literal(label_index, other)
                for other in rooted().containing(coordinate)
                if other != label_index
            ]
            target = incidence_target(coordinate, label_index)
            # sum(literals)<=target
            yield lower_bound([-literal for literal in literals],
                              len(literals) - target)
            # sum(-literals)<=len-target
            yield lower_bound(literals, target)


def common_neighbor_atmost_lines() -> Iterator[bytes]:
    labels = rooted().labels()
    wedges = wedge_variables()
    for first, second in itertools.combinations(range(84), 2):
        literals = [
            wedges[(first, second, center)]
            for center in range(84)
            if center not in (first, second)
        ]
        literals.append(edge_literal(first, second))
        intersection = len(set(labels[first]) & set(labels[second]))
        bound = 2 - intersection
        yield lower_bound([-literal for literal in literals],
                          len(literals) - bound)


def expected_groups() -> tuple[tuple[str, int, Iterable[bytes]], ...]:
    return (
        ("wedge_implications", WEDGE_VARIABLES, wedge_implication_lines()),
        ("endpoint_and_refined_units", 151, branch_unit_lines()),
        ("fixed_triangle_prism_clauses", 282_774, prism_lines()),
        ("coordinate_equalities", 2_352, coordinate_atmost_lines()),
        ("common_neighbor_upper_bounds", 3_486,
         common_neighbor_atmost_lines()),
    )


def semantic_stream_audit(opb: Path) -> dict[str, object]:
    group_records = {}
    with opb.open("rb") as handle:
        header = handle.readline()
        require(
            header == b"* #variable= 289338 #constraint= 574615\n",
            "OPB header differs from the independent expectation",
        )
        line_number = 1
        for name, expected_count, lines in expected_groups():
            digest = hashlib.sha256()
            count = 0
            for expected in lines:
                actual = handle.readline()
                line_number += 1
                require(
                    actual == expected,
                    f"OPB semantic mismatch at line {line_number} in {name}",
                )
                digest.update(actual)
                count += 1
            require(count == expected_count, f"{name} count changed")
            group_records[name] = {
                "constraint_count": count,
                "sha256": digest.hexdigest(),
            }
        require(handle.read(1) == b"", "OPB has trailing constraints")
    require(
        sum(record["constraint_count"] for record in group_records.values())
        == CONSTRAINTS,
        "semantic group total changed",
    )
    return {
        "status": "PASS",
        "header_variables": VARIABLES,
        "header_constraints": CONSTRAINTS,
        "groups": group_records,
        "every_constraint_byte_identical_to_independent_reconstruction": True,
    }


def syntax_census(opb: Path) -> dict[str, object]:
    term_histogram: Counter[int] = Counter()
    rhs_histogram: Counter[int] = Counter()
    variables_seen = set()
    complemented = 0
    with opb.open("rt", encoding="ascii", newline="\n") as handle:
        next(handle)
        for line_number, line in enumerate(handle, start=2):
            require(line.endswith(" ;\n"), f"bad OPB terminator at {line_number}")
            left, raw_rhs = line[:-3].split(" >= ")
            terms = left.split()
            require(len(terms) % 2 == 0, f"bad term structure at {line_number}")
            literals = terms[1::2]
            require(all(coefficient == "+1" for coefficient in terms[0::2]),
                    f"non-unit coefficient at {line_number}")
            numbers = [
                int(literal[2:] if literal.startswith("~x") else literal[1:])
                for literal in literals
            ]
            require(all(1 <= variable <= VARIABLES for variable in numbers),
                    f"variable out of range at {line_number}")
            variables_seen.update(numbers)
            complemented += sum(literal.startswith("~") for literal in literals)
            term_histogram[len(literals)] += 1
            rhs_histogram[int(raw_rhs)] += 1
    require(len(variables_seen) == VARIABLES, "not all declared variables occur")
    return {
        "status": "PASS",
        "distinct_variables": len(variables_seen),
        "minimum_variable": min(variables_seen),
        "maximum_variable": max(variables_seen),
        "complemented_terms": complemented,
        "term_count_histogram": {
            str(key): term_histogram[key] for key in sorted(term_histogram)
        },
        "rhs_histogram": {
            str(key): rhs_histogram[key] for key in sorted(rhs_histogram)
        },
    }


def gzip_audit(raw: Path, compressed: Path) -> dict[str, object]:
    payload = compressed.read_bytes()
    require(hashlib.sha256(payload).hexdigest() == EXPECTED_GZIP_SHA,
            "compressed hash changed")
    require(payload[:3] == b"\x1f\x8b\x08", "not a deflate gzip stream")
    require(payload[3] == 0, "gzip optional header fields are present")
    require(payload[4:8] == b"\0\0\0\0", "gzip timestamp is not zero")
    require(payload[9] == 255, "gzip OS byte is not normalized")
    restored_digest = hashlib.sha256()
    restored_size = 0
    with gzip.open(compressed, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            restored_digest.update(block)
            restored_size += len(block)
    require(restored_digest.hexdigest() == sha256_file(raw),
            "gzip round trip differs from raw OPB")
    require(restored_size == raw.stat().st_size, "gzip restored size changed")
    return {
        "status": "PASS",
        "compressed_bytes": len(payload),
        "compressed_sha256": EXPECTED_GZIP_SHA,
        "gzip_mtime": 0,
        "gzip_os_byte": 255,
        "restored_bytes": restored_size,
        "restored_sha256": restored_digest.hexdigest(),
        "round_trip_exact": True,
    }


@lru_cache(maxsize=1)
def build_results() -> dict[str, object]:
    root = repository_root()
    directory = root / "attempts/wave37-proof-producing-endpoint"
    opb = directory / "branch-15.opb"
    compressed = directory / "branch-15.opb.gz"
    metadata_path = directory / "branch-15-formula.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    opb_sha = sha256_file(opb)
    require(opb_sha == EXPECTED_OPB_SHA, "raw OPB hash changed")
    require(metadata["opb"] == {
        "bytes": opb.stat().st_size,
        "constraint_count": CONSTRAINTS,
        "path": "attempts/wave37-proof-producing-endpoint/branch-15.opb",
        "sha256": opb_sha,
    }, "formula metadata is not bound to the OPB")

    parent, refinement_edge, refinement_literal = branch_15_data()
    require((parent, refinement_edge, refinement_literal) == (4, (0, 2), 2),
            "independent branch-15 identification changed")
    require(metadata["refined_branch"] == 15 and metadata["parent_branch"] == parent,
            "branch metadata differs")
    require(metadata["branch"]["refinement_edge"] == list(refinement_edge)
            and metadata["branch"]["refinement_literal"] == refinement_literal,
            "refinement metadata differs")
    require(metadata["completed_graph_automorphism_assumed"] is False,
            "metadata claims a completed-graph automorphism")
    require(metadata["claim_label"] == "CANDIDATE_FORMULA_ONLY",
            "formula claim label is inflated")

    inputs = [
        "attempts/wave37-proof-producing-endpoint/export_endpoint_opb.py",
        "attempts/wave37-proof-producing-endpoint/branch-15-formula.json",
        "attempts/wave37-proof-producing-endpoint/branch-15.opb",
        "attempts/wave37-proof-producing-endpoint/branch-15.opb.gz",
        "attempts/wave37-proof-producing-endpoint/compression-audit.json",
    ]
    return {
        "schema_version": 1,
        "role": "verifier",
        "scope": "branch-15 OPB bytes, syntax, exact semantic reconstruction, metadata, deterministic compression, and parser boundary",
        "claim_label": "VERIFIED_FORMULA_ARTIFACT_ONLY",
        "input_sha256": {path: sha256_file(root / path) for path in inputs},
        "formula": {
            "refined_branch": 15,
            "parent_branch": parent,
            "refinement_edge": list(refinement_edge),
            "refinement_literal": refinement_literal,
            "completed_graph_automorphism_assumed": False,
            "bytes": opb.stat().st_size,
            "sha256": opb_sha,
            "constraint_count": CONSTRAINTS,
            "metadata_binding": "PASS",
        },
        "syntax": syntax_census(opb),
        "semantic_reconstruction": semantic_stream_audit(opb),
        "compression": gzip_audit(opb, compressed),
        "exact_parser": {
            "tool": "Exact",
            "source_commit": "b921cd1c4e3b6a7b7ba16dfd9c38c419d5e53ee4",
            "binary_sha256": PINNED_EXACT_SHA,
            "command": "Exact --onlyparse branch-15.opb",
            "exit_code": 0,
            "result": "PARSE_ACCEPTED",
            "evidence_path": "verification/wave37-proof-producing-endpoint/exact-parser-evidence.txt",
            "interpretation": "Syntax acceptance only; no SAT or UNSAT conclusion.",
        },
        "conclusion": {
            "formula_artifact_verified": True,
            "formula_scope": "one refined case out of 33 endpoint-compatible cases",
            "satisfiability_decided": False,
            "unsat_proof_present": False,
            "sat_graph_present": False,
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
            "target_status": "UNKNOWN",
        },
        "limitations": [
            "Only refined branch 15 is represented; the other 32 endpoint-compatible cases are absent.",
            "Exact --onlyparse validates parser acceptance, not satisfiability.",
            "No proof log, proof-checker verdict, assignment, decoded graph, or endpoint decision exists.",
            "The fixed-triangle clauses are a sound partial prism family, not a complete all-prism encoding.",
        ],
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    require(not (args.output and args.verify), "choose one output mode")
    rendered = canonical_json(build_results())
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    elif args.verify:
        require(args.verify.read_text(encoding="utf-8") == rendered,
                "stored result differs from independent regeneration")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
