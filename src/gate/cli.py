"""Command-line gate. Exit code is the gate: 0 = merge allowed, 1 = blocked.

Examples
--------
    gatecheck --policy policy/release_policy.yaml --metrics candidate.json
    # in CI: this step failing (exit 1) is what blocks the merge.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gate.engine import evaluate_gates
from gate.policy import load_policy


def _run(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    metrics = json.loads(Path(args.metrics).read_text())
    decision = evaluate_gates(policy, metrics)

    for r in decision.results:
        mark = "PASS" if r.passed else ("BLOCK" if r.severity == "blocking" else "WARN")
        print(f"[{mark}] {r.gate_id}: {r.detail}")

    print(
        json.dumps(
            {
                "allowed": decision.allowed,
                "blocking_failures": decision.blocking_failures,
                "warnings": decision.warnings,
            }
        )
    )

    # The exit code IS the gate. A required CI check failing blocks the merge.
    return 0 if decision.allowed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gatecheck", description=__doc__)
    parser.add_argument("--policy", default="policy/release_policy.yaml")
    parser.add_argument("--metrics", required=True, help="JSON of candidate metrics")
    args = parser.parse_args(argv)
    for p in (args.policy, args.metrics):
        if not Path(p).exists():
            print(f"file not found: {p}", file=sys.stderr)
            return 2
    return _run(args)


if __name__ == "__main__":
    raise SystemExit(main())
