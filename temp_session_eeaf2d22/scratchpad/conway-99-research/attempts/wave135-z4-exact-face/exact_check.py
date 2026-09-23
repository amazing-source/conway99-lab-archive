"""Independent exact replay for the Wave135 affine-face checkpoint."""

from __future__ import annotations

import argparse
import importlib.util
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE134 = ROOT / "attempts" / "wave134-z4-symmetrized-enumerator"
SPEC = importlib.util.spec_from_file_location(
    "wave134_exact_check", WAVE134 / "exact_check.py"
)
MODEL = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODEL)
PRIME = 2_147_483_647
ORBIT_TOTAL = 1 << 108
TORSION_SHELL_TOTAL = 1 << 54


def modular_rank(rows: list[list[int]], prime: int = PRIME) -> int:
    basis: dict[int, list[int]] = {}
    for original in rows:
        row = [value % prime for value in original]
        for pivot in sorted(basis):
            factor = row[pivot]
            if factor:
                row = [
                    (left - factor * right) % prime
                    for left, right in zip(row, basis[pivot])
                ]
        pivot = next((column for column, value in enumerate(row) if value), None)
        if pivot is None:
            continue
        inverse = pow(row[pivot], prime - 2, prime)
        basis[pivot] = [value * inverse % prime for value in row]
    return len(basis)


def parse_fraction(value: str | int) -> Fraction:
    return Fraction(value)


def character_rows(sources, targets):
    return [
        [
            MODEL.transform_coefficient(source, target)
            for source in sources
        ]
        for target in targets
    ]


def verify_rank(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    dimensions = payload["dimensions"]
    expected = {
        "primal_orbit_variables": 1119,
        "zero_dual_rows": 161,
        "zero_face_rank_Q": 143,
        "zero_face_nullity_Q": 976,
        "affine_rank_before_torsion_shell_Q": 145,
        "affine_dimension_before_torsion_shell_Q": 974,
        "affine_coefficient_rank_Q": 146,
        "affine_dimension_Q": 973,
    }
    for key, value in expected.items():
        if dimensions.get(key) != value:
            raise AssertionError(f"bad dimension {key}")

    sources = MODEL.primal_states()
    targets = MODEL.forbidden_dual_states()
    rows = character_rows(sources, targets)
    basis_indices = payload["forbidden_row_basis"][
        "independent_row_indices"
    ]
    if len(basis_indices) != 143 or len(set(basis_indices)) != 143:
        raise AssertionError("bad forbidden-row basis indices")
    basis_rows = [rows[index] for index in basis_indices]
    if modular_rank(basis_rows) != 143:
        raise AssertionError("forbidden-row basis is not independent")

    dependencies = payload["forbidden_row_dependencies"]["basis"]
    if len(dependencies) != 18:
        raise AssertionError("bad dependency count")
    relation_rows = []
    for dependency in dependencies:
        relation = [0] * len(rows)
        for term in dependency["support"]:
            index = term["row_index"]
            if list(targets[index]) != term["target"]:
                raise AssertionError("dependency target label mismatch")
            relation[index] = int(term["coefficient"])
        for column in range(len(sources)):
            if sum(
                coefficient * rows[index][column]
                for index, coefficient in enumerate(relation)
                if coefficient
            ):
                raise AssertionError("claimed forbidden-row dependency fails")
        relation_rows.append(relation)
    if modular_rank(relation_rows) != 18:
        raise AssertionError("dependency vectors are not independent")

    normalization = [1] * len(sources)
    zero_unit = [0] * len(sources)
    zero_unit[sources.index((99, 0, 0))] = 1
    torsion_shell = [
        1 if state[1] == 0 else 0 for state in sources
    ]
    if modular_rank(
        basis_rows + [normalization, zero_unit, torsion_shell]
    ) != 146:
        raise AssertionError("torsion-extended affine rank is not 146")

    return {
        "forbidden_rows": len(rows),
        "forbidden_rank_Q": 143,
        "dependency_dimension": 18,
        "affine_rank_Q": 146,
        "affine_dimension_Q": 973,
    }


def parse_candidate(payload, sources):
    table = {
        tuple(map(int, key.split(","))): parse_fraction(value)
        for key, value in payload["primal_orbits"].items()
    }
    unknown = set(table) - set(sources)
    if unknown:
        raise AssertionError("witness contains unknown primal orbit")
    return [table.get(state, Fraction(0)) for state in sources]


def verify_candidate(payload) -> dict:
    if payload["classification"] != "EXACT_RATIONAL_FEASIBLE":
        return {
            "classification": payload["classification"],
            "terminal_witness_replayed": False,
        }
    sources = MODEL.primal_states()
    candidate = parse_candidate(payload, sources)
    forced_primal = MODEL.forced_primal()
    for state, value in zip(sources, candidate):
        if value < forced_primal.get(state, 0):
            raise AssertionError(f"primal lower bound fails at {state}")
    if sum(candidate) != ORBIT_TOTAL:
        raise AssertionError("normalization fails")
    if candidate[sources.index((99, 0, 0))] != 1:
        raise AssertionError("A0 fails")
    if sum(
        value
        for state, value in zip(sources, candidate)
        if state[1] == 0
    ) != TORSION_SHELL_TOTAL:
        raise AssertionError("torsion-shell equality fails")

    nonzero = [
        (index, value)
        for index, value in enumerate(candidate)
        if value
    ]
    for target in MODEL.forbidden_dual_states():
        numerator = sum(
            MODEL.transform_coefficient(sources[index], target) * value
            for index, value in nonzero
        )
        if numerator:
            raise AssertionError(f"forbidden dual row nonzero at {target}")
    forced_dual = MODEL.forced_dual()
    for target in MODEL.dual_states():
        numerator = sum(
            MODEL.transform_coefficient(sources[index], target) * value
            for index, value in nonzero
        )
        if numerator < forced_dual.get(target, 0) * ORBIT_TOTAL:
            raise AssertionError(f"dual lower bound fails at {target}")
    return {
        "classification": "EXACT_RATIONAL_FEASIBLE",
        "terminal_witness_replayed": True,
        "primal_rows": len(sources),
        "forbidden_dual_rows": len(MODEL.forbidden_dual_states()),
        "allowed_dual_rows": len(MODEL.dual_states()),
    }


def verify_search(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    classification = payload.get("classification", "")
    allowed = {
        "EXACT_RATIONAL_FEASIBLE",
        "UNKNOWN_WALL",
        "UNKNOWN_MEMORY_GUARD",
        "UNKNOWN_BAD_PRIMAL",
        "UNKNOWN_EQUALITY_REPLAY_FAILURE",
        "UNKNOWN_ROW_GENERATION_STALL",
        "UNKNOWN_ITERATION_LIMIT",
    }
    if (
        classification not in allowed
        and not classification.startswith("UNKNOWN_CDD_")
    ):
        raise AssertionError(f"unrecognized classification {classification}")
    return verify_candidate(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rank",
        type=Path,
        default=HERE / "face-rank.json",
    )
    parser.add_argument(
        "--search",
        type=Path,
        default=HERE / "row-generation.json",
    )
    args = parser.parse_args()
    result = {"rank": verify_rank(args.rank)}
    if args.search.exists():
        result["search"] = verify_search(args.search)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
