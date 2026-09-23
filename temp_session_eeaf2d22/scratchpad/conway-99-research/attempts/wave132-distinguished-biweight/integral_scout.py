"""Hard-bounded integral distinguished-row split-enumerator scout."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from math import comb
from pathlib import Path


N = 99
K = 54
ORDER = 1 << K
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "integral-scout.json"
IMAGE_WEIGHTS = [0] + list(range(14, 94, 2))
IMAGE_LOWER = {
    0: 1,
    14: 99,
    24: 4158,
    26: 693,
    30: 70686,
    32: 41580,
    34: 36036,
    36: 8547,
}
DUAL_BASE_LOWER = {
    0: 1,
    15: 99,
    24: 693,
    26: 4158,
    31: 41580,
    33: 79002,
    35: 8316,
    37: 27720,
    39: 231,
    99: 1,
}


def krawtchouk(degree: int, weight: int) -> int:
    return sum(
        (-1) ** overlap
        * comb(weight, overlap)
        * comb(N - weight, degree - overlap)
        for overlap in range(
            max(0, degree - (N - weight)),
            min(weight, degree) + 1,
        )
    )


def dual_lower() -> dict[int, int]:
    result = dict(DUAL_BASE_LOWER)
    for weight, value in list(result.items()):
        result[N - weight] = max(result.get(N - weight, 0), value)
    return result


def worker(timeout_ms: int) -> None:
    from z3 import Int, Solver, Sum, sat

    image = {weight: Int(f"A_{weight}") for weight in IMAGE_WEIGHTS}
    dual = {weight: Int(f"B_{weight}") for weight in range(N + 1)}
    lower_dual = dual_lower()
    solver = Solver()
    solver.set(timeout=timeout_ms)
    for weight in IMAGE_WEIGHTS:
        solver.add(image[weight] >= IMAGE_LOWER.get(weight, 0))
    solver.add(image[0] == 1)
    solver.add(
        Sum([image[weight] for weight in IMAGE_WEIGHTS]) == ORDER
    )
    for degree in range(N + 1):
        solver.add(dual[degree] >= lower_dual.get(degree, 0))
        if 1 <= degree <= 14:
            solver.add(dual[degree] == 0)
        solver.add(
            Sum(
                [
                    image[weight] * krawtchouk(degree, weight)
                    for weight in IMAGE_WEIGHTS
                ]
            )
            == ORDER * dual[degree]
        )
    for weight in range(50):
        solver.add(dual[weight] == dual[N - weight])

    def add_split(
        name: str,
        enumerator: dict,
        distinguished_weight: int,
        odd_multiplier: int | None,
        forced_by_weight: dict[int, dict[int, int]],
    ) -> None:
        for weight, coefficient in enumerator.items():
            lower = max(0, weight + distinguished_weight - N)
            upper = min(weight, distinguished_weight)
            row = {
                intersection: Int(
                    f"{name}_{weight}_{intersection}"
                )
                for intersection in range(lower, upper + 1)
            }
            for value in row.values():
                solver.add(value >= 0)
            for intersection, lower_count in forced_by_weight.get(
                weight, {}
            ).items():
                solver.add(row[intersection] >= lower_count)
            solver.add(Sum(list(row.values())) == 99 * coefficient)
            solver.add(
                Sum(
                    [
                        intersection * value
                        for intersection, value in row.items()
                    ]
                )
                == distinguished_weight * weight * coefficient
            )
            odd_target = (
                weight * coefficient
                if odd_multiplier is None
                else odd_multiplier * coefficient
            )
            solver.add(
                Sum(
                    [
                        value
                        for intersection, value in row.items()
                        if intersection % 2
                    ]
                )
                == odd_target
            )

    add_split(
        "Cr",
        image,
        14,
        None,
        {14: {14: 99, 1: 1386, 2: 8316}},
    )
    add_split(
        "Dq",
        dual,
        15,
        None,
        {15: {15: 99, 3: 1386, 2: 8316}},
    )
    add_split(
        "Cq",
        image,
        15,
        0,
        {14: {14: 99, 2: 9702}},
    )
    add_split(
        "Dr",
        dual,
        14,
        0,
        {15: {14: 99, 2: 9702}},
    )

    status = solver.check()
    result = {
        "solver_status": str(status).upper(),
        "solver_reason_unknown": solver.reason_unknown(),
    }
    if status == sat:
        model = solver.model()
        result["image_coefficients"] = {
            str(weight): model.eval(
                image[weight], model_completion=True
            ).as_long()
            for weight in IMAGE_WEIGHTS
            if model.eval(image[weight], model_completion=True).as_long()
        }
        result["dual_coefficients"] = {
            str(weight): model.eval(
                dual[weight], model_completion=True
            ).as_long()
            for weight in range(N + 1)
            if model.eval(dual[weight], model_completion=True).as_long()
        }
    print(json.dumps(result), flush=True)


def bounded_run(timeout_ms: int, wall_seconds: int) -> dict:
    started = time.monotonic()
    command = [
        sys.executable,
        "-B",
        str(Path(__file__).resolve()),
        "--worker",
        "--timeout-ms",
        str(timeout_ms),
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=wall_seconds,
            check=False,
        )
        elapsed = time.monotonic() - started
        if completed.returncode != 0:
            return {
                "status": "UNKNOWN_WORKER_ERROR",
                "returncode": completed.returncode,
                "stderr_tail": completed.stderr[-1000:],
                "elapsed_seconds": round(elapsed, 3),
            }
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
        payload["status"] = payload.pop("solver_status")
        payload["elapsed_seconds"] = round(elapsed, 3)
        return payload
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - started
        return {
            "status": "UNKNOWN_HARD_TIMEOUT",
            "elapsed_seconds": round(elapsed, 3),
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout-ms", type=int, default=10_000)
    parser.add_argument("--wall-seconds", type=int, default=15)
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    if args.worker:
        worker(args.timeout_ms)
        return
    result = {
        "format": "wave132-integral-split-scout-v1",
        "claim_label": "UNKNOWN",
        "scope": (
            "Integral ordinary MacWilliams coefficients plus all four "
            "distinguished-row parity/first-moment split systems and "
            "the exact forced pair-composition lower rows."
        ),
        "solver_timeout_ms": args.timeout_ms,
        "hard_wall_seconds": args.wall_seconds,
        "result": bounded_run(args.timeout_ms, args.wall_seconds),
        "negative_inference_allowed": False,
        "limitations": [
            "UNKNOWN or timeout is not evidence of infeasibility.",
            "The full genus-two partial-Hadamard transform is not encoded.",
            "An integral split enumerator would not construct a code.",
        ],
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["result"], sort_keys=True))


if __name__ == "__main__":
    main()
