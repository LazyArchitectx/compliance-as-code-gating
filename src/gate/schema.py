"""Validated models for the gating policy and its results."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Comparator = Literal["gte", "lte", "eq", "lt", "gt"]


class Gate(BaseModel):
    """One release gate: a named metric compared against a threshold.

    severity 'blocking' hard-stops a merge on failure; 'warn' records the failure
    but does not block. Most gates are blocking — a warn gate is for signals you
    want visible without halting the release.
    """

    id: str
    metric: str
    comparator: Comparator
    threshold: float
    severity: Literal["blocking", "warn"] = "blocking"

    def passes(self, value: float) -> bool:
        ops = {
            "gte": value >= self.threshold,
            "lte": value <= self.threshold,
            "eq": value == self.threshold,
            "lt": value < self.threshold,
            "gt": value > self.threshold,
        }
        return ops[self.comparator]


class Policy(BaseModel):
    name: str
    gates: list[Gate] = Field(default_factory=list)


class GateResult(BaseModel):
    gate_id: str
    metric: str
    value: float | None
    threshold: float
    comparator: Comparator
    severity: str
    passed: bool
    detail: str


class GateDecision(BaseModel):
    """The overall merge/block decision for a release candidate."""

    allowed: bool
    results: list[GateResult]

    @property
    def blocking_failures(self) -> list[str]:
        return [r.gate_id for r in self.results if not r.passed and r.severity == "blocking"]

    @property
    def warnings(self) -> list[str]:
        return [r.gate_id for r in self.results if not r.passed and r.severity == "warn"]
