#!/usr/bin/env python3
"""Replay a Wave 39 generalized-unit shard certificate from frozen OPB bytes.

This checker is deliberately separate from the generator.  It reads only the
certificate and the published source formula, validates exact byte bindings,
and replays each generalized-unit inference from the cited source constraint.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TERM_RE = re.compile(r"\+1\s+(~)?x([1-9][0-9]*)")
CONSTRAINT_RE = re.compile(
    r"^(?:\+1\s+(?:~)?x[1-9][0-9]*\s+)+>=\s+([0-9]+)\s+;\s*$"
)
HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def no_duplicate_object_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def exact_object(value, keys: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{label} has an invalid schema")
    return value


def exact_int(value, label: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{label} must be an integer >= {minimum}")
    return value


def exact_bool(value, label: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{label} must be Boolean")
    return value


def parse_constraint(text: str) -> tuple[tuple[tuple[int, bool], ...], int]:
    match = CONSTRAINT_RE.fullmatch(text)
    if match is None:
        raise ValueError("unsupported OPB constraint syntax")
    literals = tuple(
        (int(term.group(2)), term.group(1) is None)
        for term in TERM_RE.finditer(text)
    )
    variables = [variable for variable, _ in literals]
    if len(variables) != len(set(variables)):
        raise ValueError("constraint repeats a variable")
    return literals, int(match.group(1))


def load_source(
    source: dict, requested_lines: set[int]
) -> dict[int, str]:
    path_text = source.get("path")
    if not isinstance(path_text, str) or "\\" in path_text:
        raise ValueError("source path must be a repository-relative POSIX path")
    resolved = (REPOSITORY_ROOT / path_text).resolve()
    try:
        resolved.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise ValueError("source path escapes the repository") from error
    compressed = resolved.read_bytes()
    if sha256_bytes(compressed) != source.get("gzip_sha256"):
        raise ValueError("source gzip SHA-256 mismatch")
    if len(compressed) != exact_int(source.get("gzip_bytes"), "gzip_bytes", 1):
        raise ValueError("source gzip byte count mismatch")

    raw_digest = hashlib.sha256()
    selected: dict[int, str] = {}
    constraint_count = 0
    with gzip.open(resolved, "rb") as stream:
        for line_number, raw_line in enumerate(stream, start=1):
            raw_digest.update(raw_line)
            if line_number == 1:
                expected_variables = exact_int(
                    source.get("variables"), "variables", 1
                )
                expected_constraints = exact_int(
                    source.get("constraints"), "constraints", 1
                )
                expected_header = (
                    f"* #variable= {expected_variables} "
                    f"#constraint= {expected_constraints}\n"
                ).encode("ascii")
                if raw_line != expected_header:
                    raise ValueError("source OPB header mismatch")
                continue
            constraint_count += 1
            if line_number in requested_lines:
                selected[line_number] = raw_line.decode("ascii").rstrip("\n")
    if raw_digest.hexdigest() != source.get("raw_sha256"):
        raise ValueError("decompressed OPB SHA-256 mismatch")
    if constraint_count != source.get("constraints"):
        raise ValueError("source OPB constraint count mismatch")
    if set(selected) != requested_lines:
        raise ValueError("certificate cites a missing source line")
    return selected


def validate_certificate(certificate: dict) -> dict[str, object]:
    required_top = {
        "format",
        "role",
        "claim_label",
        "scope",
        "source",
        "branch",
        "source_constraints",
        "trace",
        "logical_summary",
        "coverage",
        "limitations",
    }
    exact_object(certificate, required_top, "certificate")
    if certificate["format"] != "wave39-generalized-unit-shard-certificate-v1":
        raise ValueError("unsupported certificate format")
    if certificate["role"] != "construction":
        raise ValueError("certificate role must be construction")
    if certificate["claim_label"] != "CANDIDATE":
        raise ValueError("certificate claim label must remain CANDIDATE")

    source = exact_object(
        certificate["source"],
        {
            "path",
            "gzip_bytes",
            "gzip_sha256",
            "raw_sha256",
            "variables",
            "constraints",
        },
        "source",
    )
    for field in ("gzip_sha256", "raw_sha256"):
        if not isinstance(source[field], str) or HEX_RE.fullmatch(source[field]) is None:
            raise ValueError(f"{field} is not a SHA-256 digest")

    branch = exact_object(
        certificate["branch"],
        {
            "refined_branch",
            "parent_branch",
            "assumption",
            "assumption_edge",
            "complementary_open_shard",
        },
        "branch",
    )
    if branch["refined_branch"] != 15 or branch["parent_branch"] != 4:
        raise ValueError("certificate is not the frozen branch-15 shard")
    assumption = exact_object(
        branch["assumption"], {"variable", "value"}, "assumption"
    )
    assumption_variable = exact_int(
        assumption["variable"], "assumption variable", 1
    )
    assumption_value = exact_bool(assumption["value"], "assumption value")
    if (assumption_variable, assumption_value) != (187, True):
        raise ValueError("unexpected shard assumption")
    complement = exact_object(
        branch["complementary_open_shard"],
        {"variable", "value"},
        "complementary shard",
    )
    if (
        exact_int(complement["variable"], "complement variable", 1),
        exact_bool(complement["value"], "complement value"),
    ) != (187, False):
        raise ValueError("the complementary shard is not exact")

    source_constraints = certificate["source_constraints"]
    if not isinstance(source_constraints, dict) or not source_constraints:
        raise ValueError("source_constraints must be a nonempty object")
    records: dict[int, dict] = {}
    for key, raw_record in source_constraints.items():
        if not isinstance(key, str) or not key.isdigit() or key.startswith("0"):
            raise ValueError("source constraint key is not canonical")
        line_number = int(key)
        record = exact_object(
            raw_record,
            {"line", "sha256", "term_count", "bound"},
            "source constraint",
        )
        if record["line"] != line_number:
            raise ValueError("source constraint key/line mismatch")
        if (
            not isinstance(record["sha256"], str)
            or HEX_RE.fullmatch(record["sha256"]) is None
        ):
            raise ValueError("source line SHA-256 is invalid")
        exact_int(record["term_count"], "term_count", 1)
        exact_int(record["bound"], "bound", 0)
        records[line_number] = record

    trace = certificate["trace"]
    if not isinstance(trace, list) or not trace:
        raise ValueError("trace must be a nonempty list")
    cited_lines: set[int] = set()
    for event in trace:
        if not isinstance(event, dict):
            raise ValueError("trace event must be an object")
        if event.get("rule") == "generalized_unit":
            exact_object(
                event, {"rule", "source_line", "derive"}, "unit trace event"
            )
            derive = exact_object(
                event["derive"], {"variable", "value"}, "derived literal"
            )
            exact_int(derive["variable"], "derived variable", 1)
            exact_bool(derive["value"], "derived value")
        elif event.get("rule") == "contradiction":
            exact_object(
                event, {"rule", "source_line"}, "contradiction trace event"
            )
        else:
            raise ValueError("unsupported trace rule")
        cited_lines.add(exact_int(event["source_line"], "source line", 2))
    if trace[-1].get("rule") != "contradiction":
        raise ValueError("the final trace event must be a contradiction")
    if cited_lines != set(records):
        raise ValueError("trace/source-constraint coverage mismatch")

    lines = load_source(source, cited_lines)
    parsed: dict[int, tuple[tuple[tuple[int, bool], ...], int]] = {}
    for line_number, record in records.items():
        text = lines[line_number]
        if sha256_bytes((text + "\n").encode("ascii")) != record["sha256"]:
            raise ValueError("source line SHA-256 mismatch")
        literals, bound = parse_constraint(text)
        if len(literals) != record["term_count"] or bound != record["bound"]:
            raise ValueError("source line metadata mismatch")
        parsed[line_number] = literals, bound

    assignments = {assumption_variable: assumption_value}
    derivations = 0
    contradiction_line = None
    for event in trace:
        line_number = event["source_line"]
        literals, bound = parsed[line_number]
        satisfied = sum(
            assignments[variable] == value
            for variable, value in literals
            if variable in assignments
        )
        unknown = [
            (variable, value)
            for variable, value in literals
            if variable not in assignments
        ]
        maximum = satisfied + len(unknown)
        if event["rule"] == "generalized_unit":
            if maximum != bound:
                raise ValueError("generalized-unit source is not tight")
            derive = event["derive"]
            literal = (derive["variable"], derive["value"])
            if literal not in unknown:
                raise ValueError("derived literal is not forced by the source")
            assignments[literal[0]] = literal[1]
            derivations += 1
        else:
            if maximum >= bound:
                raise ValueError("claimed contradiction remains satisfiable")
            contradiction_line = line_number

    if assignments.get(24) is not True:
        raise ValueError("normalization unit x24=1 was not derived")
    if assignments.get(2) is not True:
        raise ValueError("refinement unit x2=1 was not derived")
    if assignments.get(3591) is not False:
        raise ValueError("common-neighbor capacity did not derive x3591=0")

    coverage = certificate["coverage"]
    if not isinstance(coverage, dict):
        raise ValueError("coverage must be an object")
    expected_coverage = {
        "closed_shards": 1,
        "exhaustive_polarity_shards": 2,
        "closed_shard": "branch15 AND x187=1",
        "open_shard": "branch15 AND x187=0",
        "closed_endpoint_cases": 0,
        "total_endpoint_cases": 33,
    }
    if coverage != expected_coverage:
        raise ValueError("coverage boundary is misstated")

    return {
        "status": "PASS_GENERALIZED_UNIT_SHARD_REPLAY",
        "refined_branch": 15,
        "assumption": "x187=1",
        "entailed_literal": "x187=0",
        "derivation_count": derivations,
        "contradiction_line": contradiction_line,
        "closed_shards": 1,
        "exhaustive_polarity_shards": 2,
        "closed_endpoint_cases": 0,
        "total_endpoint_cases": 33,
        "endpoint_status": "UNKNOWN",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    certificate = json.loads(
        args.certificate.read_text(encoding="utf-8"),
        object_pairs_hook=no_duplicate_object_keys,
    )
    result = validate_certificate(certificate)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
