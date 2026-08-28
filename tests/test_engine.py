"""Gate engine tests — the decision logic, including the missing-metric rule."""

from gate.engine import evaluate_gates
from gate.policy import load_policy
from gate.schema import Gate, Policy


def _policy():
    return load_policy("policy/release_policy.yaml")


def test_clean_candidate_is_allowed():
    metrics = {
        "accuracy": 0.91,
        "disparate_impact_ratio": 0.93,
        "psi": 0.07,
        "pii_hits": 0,
        "p95_latency_ms": 180,
    }
    decision = evaluate_gates(_policy(), metrics)
    assert decision.allowed is True
    assert decision.blocking_failures == []


def test_failing_candidate_is_blocked():
    metrics = {
        "accuracy": 0.88,             # below 0.85? no, 0.88 passes
        "disparate_impact_ratio": 0.62,  # below 0.80 -> block
        "psi": 0.34,                  # above 0.20 -> block
        "pii_hits": 2,                # != 0 -> block
        "p95_latency_ms": 300,        # warn only
    }
    decision = evaluate_gates(_policy(), metrics)
    assert decision.allowed is False
    assert set(decision.blocking_failures) == {"bias-ratio-floor", "drift-ceiling", "pii-zero"}
    assert decision.warnings == ["latency-budget"]


def test_missing_required_metric_blocks_not_skips():
    """A required metric the candidate omits is a FAILURE, never an assumed pass."""
    metrics = {"accuracy": 0.90, "psi": 0.05, "pii_hits": 0}  # missing disparate_impact_ratio
    decision = evaluate_gates(_policy(), metrics)
    assert decision.allowed is False
    assert "bias-ratio-floor" in decision.blocking_failures


def test_warn_gate_does_not_block():
    policy = Policy(
        name="p",
        gates=[Gate(id="lat", metric="latency", comparator="lte", threshold=100, severity="warn")],
    )
    decision = evaluate_gates(policy, {"latency": 999})  # fails, but only a warning
    assert decision.allowed is True
    assert decision.warnings == ["lat"]


def test_comparators():
    g = Gate(id="g", metric="m", comparator="gte", threshold=0.85)
    assert g.passes(0.85) is True
    assert g.passes(0.84) is False
