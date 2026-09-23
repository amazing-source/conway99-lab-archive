"""Emit the exact Wave139 invariant-space dimension record."""

from __future__ import annotations

import json
from pathlib import Path

import gf4_model as model


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "exact-rank.json"


if __name__ == "__main__":
    payload = model.exact_rank_record()
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(payload["self_dual_even_nY_solution_dimension"])
