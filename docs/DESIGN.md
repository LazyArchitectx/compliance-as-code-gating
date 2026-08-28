# Design Notes

Rationale behind the gate — written to be defended in a technical interview.

## Why the exit code is the interface

CI systems gate merges on a step's exit code. By making `gatecheck` exit non-zero on any
blocking failure, the tool needs no special integration: it's a normal command, and a
branch-protection rule marking it "required" turns it into an unbypassable gate. The
interface is the exit code, which is exactly what a required status check consumes.

## Why a missing metric is a failure, not a skip

This is the load-bearing decision. If a candidate omits a required metric, the safe reading
is not "assume it's fine" — it's "we have no evidence it's fine." Treating a missing
measurement as a pass is how gates get quietly defeated: drop the metric, skip the check.
So the engine treats "required but absent" identically to "present and failing." Silence is
never compliance. `test_missing_required_metric_blocks_not_skips` pins this behavior.

## Why blocking vs. warn severity

Not every signal should halt a release. A latency regression might be worth surfacing
without blocking a correctness-critical fix. Modeling severity as a first-class field lets
the policy encode that judgment: blocking gates hold the line; warn gates record a failure
in the output and the exit stays zero. This keeps the gate strict where it must be and
informative everywhere else.

## Why the policy is data

The gates live in YAML, not code. A governance owner can read and change the policy without
touching the engine, and the same file documents the rules and enforces them — there's no
second, drifting description of "what we require." Comparators (`gte`, `lte`, `eq`, ...) are
a small closed set, so a policy is auditable at a glance.

## Relationship to the evidence pipeline

This gate is the enforcement half of a two-part system. A separate evidence pipeline can
*generate* a candidate's metrics (bias ratio, PSI, PII hits); this gate *decides* whether
those metrics clear the bar to merge. Evidence answers "what are the numbers?"; the gate
answers "do the numbers let this ship?"

## Scope and honesty

A from-scratch demonstrator of the pattern. A production version would add PR-comment
reporting, policy inheritance, and regression-relative gating (block on getting worse than
current production, not just on absolute thresholds) — named in the README.
