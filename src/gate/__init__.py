"""Compliance-as-code release gating.

Evaluates a release candidate's metrics against a policy of gates and decides
merge / block. A single gate failure blocks the release until remediation clears
it. Designed to run as a required CI check: the same policy that documents the
rules also enforces them at the merge button.
"""

from gate.engine import evaluate_gates
from gate.policy import load_policy
from gate.schema import GateDecision, GateResult, Policy

__all__ = ["GateDecision", "GateResult", "Policy", "evaluate_gates", "load_policy"]
__version__ = "1.0.0"
