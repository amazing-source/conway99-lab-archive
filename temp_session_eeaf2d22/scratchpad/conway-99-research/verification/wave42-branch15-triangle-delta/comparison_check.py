#!/usr/bin/env python3
"""Post-freeze comparison of the clean-room and discovery clause catalogues."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DISCOVERY = ROOT / "attempts" / "wave42-endpoint-certificate"
RAW_CATALOG = DISCOVERY / "branch-15-seventh-triangle-delta.opb.gz"
ACTIVE_CATALOG = (
    DISCOVERY / "branch-15-seventh-triangle-active-delta.opb.gz"
)
DISCOVERY_RESULT = DISCOVERY / "branch-15-seventh-triangle-result.json"
INDEPENDENT_RESULT = HERE / "independent-results.json"

EXPECTED = {
    "raw": {
        "gzip_sha256": (
            "0840524515920a59fd3d0f0666b496f9e639476dd887d0d90df5bb58a9e8904e"
        ),
        "raw_sha256": (
            "348dc5f4bc9ee99511286a8078d0e4ef79786b57ba39ae572c032e42747be77e"
        ),
        "constraints": 64_932,
        "widths": {"3": 132, "5": 64_800},
        "normalized_sha256": (
            "e82aaa6b6f9cad3d27dbfb36069446a62aafbb2629fabc2a8492d243c1320635"
        ),
    },
    "active": {
        "gzip_sha256": (
            "63e07c1196c4cfd315f72b311221233fa61f608f0dd856f3d00391bd5f5286b9"
        ),
        "raw_sha256": (
            "6ef7d69d217077b30a39cc9a85f65881d9389516201de7fdbcf593f23a6fb2c0"
        ),
        "constraints": 33_778,
        "widths": {"3": 91, "4": 580, "5": 33_107},
        "normalized_sha256": (
            "fc8925756861e850b28bfb9e18844dd75c525b75f4061f70089df696843ad903"
        ),
    },
}
EXPECTED_RESULT_SHA256 = (
    "2faa09eee4217d19fc1e1ac8f9705129e1cd57d47c0016a1d2bc229d87d8b184"
)

HEADER = re.compile(
    rb"^\* #variable= ([1-9][0-9]*) #constraint= ([1-9][0-9]*)\n$"
)
ROW = re.compile(
    rb"^\+1 ~x([1-9][0-9]*)(?: \+1 ~x([1-9][0-9]*))* >= 1 ;\n$"
)
TERM = re.compile(rb"\+1 ~x([1-9][0-9]*)")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def strict_load(path: Path) -> dict[str, object]:
    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def canonical(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def parse_catalog(path: Path) -> dict[str, object]:
    compressed = path.read_bytes()
    raw_hasher = hashlib.sha256()
    clauses: list[tuple[int, ...]] = []
    with gzip.open(path, "rb") as stream:
        header = stream.readline()
        raw_hasher.update(header)
        match = HEADER.fullmatch(header)
        if match is None:
            raise ValueError(f"noncanonical OPB header: {path}")
        variables = int(match.group(1))
        declared = int(match.group(2))
        if variables != 289_338:
            raise ValueError(f"wrong variable count: {path}")
        previous: tuple[int, ...] | None = None
        for line in stream:
            raw_hasher.update(line)
            if ROW.fullmatch(line) is None:
                raise ValueError(f"noncanonical negative clause row: {path}")
            clause = tuple(int(item) for item in TERM.findall(line))
            if tuple(sorted(set(clause))) != clause:
                raise ValueError(f"clause is not sorted and duplicate-free: {path}")
            if previous is not None and clause <= previous:
                raise ValueError(f"catalog is not strictly sorted: {path}")
            previous = clause
            clauses.append(clause)
    if len(clauses) != declared:
        raise ValueError(f"declared and observed constraint counts differ: {path}")
    normalized = hashlib.sha256()
    for clause in clauses:
        normalized.update(",".join(map(str, clause)).encode("ascii") + b"\n")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "gzip_sha256": sha256(compressed),
        "raw_sha256": raw_hasher.hexdigest(),
        "variables": variables,
        "constraints": len(clauses),
        "widths": {
            str(width): count
            for width, count in sorted(Counter(map(len, clauses)).items())
        },
        "normalized_clause_stream_sha256": normalized.hexdigest(),
    }


def compute() -> dict[str, object]:
    independent = strict_load(INDEPENDENT_RESULT)
    discovery_result_bytes = DISCOVERY_RESULT.read_bytes()
    discovery_result = strict_load(DISCOVERY_RESULT)
    raw = parse_catalog(RAW_CATALOG)
    active = parse_catalog(ACTIVE_CATALOG)
    delta = independent.get("delta")
    if not isinstance(delta, dict):
        raise ValueError("independent result has no delta")
    return {
        "format": "wave42-branch15-triangle-delta-comparison-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED_REDUCTION",
        "comparison_boundary": "post-clean-room-implementation-freeze",
        "discovery_result": {
            "path": DISCOVERY_RESULT.relative_to(ROOT).as_posix(),
            "sha256": sha256(discovery_result_bytes),
            "claim_label": discovery_result.get("claim_label"),
        },
        "raw_catalog": raw,
        "active_catalog": active,
        "independent_clause_streams": {
            "raw_sha256": delta.get("raw_clause_stream_sha256"),
            "active_sha256": delta.get("active_clause_stream_sha256"),
        },
        "result": {
            "raw_catalog_exact_match": (
                raw["normalized_clause_stream_sha256"]
                == delta.get("raw_clause_stream_sha256")
            ),
            "active_catalog_exact_match": (
                active["normalized_clause_stream_sha256"]
                == delta.get("active_clause_stream_sha256")
            ),
            "branch_15_closed": False,
            "endpoint_cases_closed": 0,
            "endpoint_cases_total": 33,
            "conway_99": "UNKNOWN",
        },
        "limitations": [
            "The equality is between exact normalized positive-variable clause sets.",
            "The reduction is conditional on endpoint branch 15 and n3=4158.",
            "Neither exact catalogue match is a SAT or UNSAT certificate.",
            "Branch 15, the endpoint, and Conway-99 remain UNKNOWN.",
        ],
    }


def validate(result: dict[str, object]) -> None:
    if result.get("claim_label") != "VERIFIED_SCOPED_REDUCTION":
        raise ValueError("wrong verifier label")
    discovery = result.get("discovery_result")
    if not isinstance(discovery, dict):
        raise ValueError("missing discovery binding")
    if discovery.get("sha256") != EXPECTED_RESULT_SHA256:
        raise ValueError("discovery result hash mismatch")
    if discovery.get("claim_label") != "CANDIDATE":
        raise ValueError("discovery claim was improperly promoted in place")
    independent = result.get("independent_clause_streams")
    if not isinstance(independent, dict):
        raise ValueError("missing independent streams")
    for name, key in (("raw", "raw_sha256"), ("active", "active_sha256")):
        catalog = result.get(f"{name}_catalog")
        if not isinstance(catalog, dict):
            raise ValueError(f"missing {name} catalog")
        expected = EXPECTED[name]
        for field in ("gzip_sha256", "raw_sha256", "constraints", "widths"):
            if catalog.get(field) != expected[field]:
                raise ValueError(f"{name} catalog {field} mismatch")
        if catalog.get("normalized_clause_stream_sha256") != expected[
            "normalized_sha256"
        ]:
            raise ValueError(f"{name} normalized stream mismatch")
        if independent.get(key) != expected["normalized_sha256"]:
            raise ValueError(f"{name} independent stream mismatch")
    outcome = result.get("result")
    if not isinstance(outcome, dict):
        raise ValueError("missing comparison outcome")
    if outcome.get("raw_catalog_exact_match") is not True:
        raise ValueError("raw catalogue does not exactly match")
    if outcome.get("active_catalog_exact_match") is not True:
        raise ValueError("active catalogue does not exactly match")
    if outcome.get("branch_15_closed") is not False:
        raise ValueError("branch 15 is not closed")
    if outcome.get("endpoint_cases_closed") != 0:
        raise ValueError("no endpoint case is closed")
    if outcome.get("conway_99") != "UNKNOWN":
        raise ValueError("Conway-99 status inflation")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    observed = compute()
    validate(observed)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical(observed))
    else:
        expected = strict_load(args.verify)
        validate(expected)
        if canonical(observed) != canonical(expected):
            raise ValueError("live comparison differs from archived result")
    print(json.dumps(observed["result"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
