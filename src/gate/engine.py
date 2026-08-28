"""Evaluate a candidate's metrics against the policy.

Rules that make the gate trustworthy:
  * A blocking gate that fails blocks the merge.
  * A metric the policy requires but the candidate does not provide is treated as a
    FAILURE, not a skip — a missing measurement can't be assumed compliant. This is
    the single most important design choice: silence is not a pass.
  * warn gates record failures without blocking.
"""

from __future__ import annotations

from gate.schema import GateDecision, GateResult, Policy


def evaluate_gates(policy: Policy, metrics: dict[str, float]) -> GateDecision:
    results: list[GateResult] = []

    for g in policy.gates:
        if g.metric not in metrics:
            # Missing required metric == failure. Never assume compliant on silence.
            results.append(
                GateResult(
                    gate_id=g.id,
                    metric=g.metric,
                    value=None,
                    threshold=g.threshold,
                    comparator=g.comparator,
                    severity=g.severity,
                    passed=False,
                    detail=f"metric '{g.metric}' not provided by candidate",
                )
            )
            continue

        value = float(metrics[g.metric])
        passed = g.passes(value)
        results.append(
            GateResult(
                gate_id=g.id,
                metric=g.metric,
                value=value,
                threshold=g.threshold,
                comparator=g.comparator,
                severity=g.severity,
                passed=passed,
                detail="ok" if passed else f"{value} {g.comparator} {g.threshold} is false",
            )
        )

    allowed = not any(not r.passed and r.severity == "blocking" for r in results)
    return GateDecision(allowed=allowed, results=results)
