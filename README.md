# Compliance-as-Code Release Gating

Evaluates a release candidate's metrics against a **policy of gates** and decides
merge / block. A single blocking-gate failure stops the release until remediation clears
it. The exit code *is* the gate — wire it as a required CI check and an unsafe change
physically cannot merge.

[![ci](https://github.com/LazyArchitectx/compliance-as-code-gating/actions/workflows/ci.yml/badge.svg)](https://github.com/LazyArchitectx/compliance-as-code-gating/actions)

> **What this is.** A portfolio demonstrator of the *compliance-as-code / release-gating*
> pattern — turning a review checklist into an enforceable, unbypassable merge gate. Clean,
> from-scratch, not a proprietary system.

---

## The idea

The rules a model must satisfy to ship (accuracy floor, bias ratio, drift ceiling, zero
PII, latency budget) live in `release_policy.yaml`, not in someone's head. A candidate's
measured metrics are checked against every gate. Blocking gates that fail stop the merge;
warn gates surface a signal without blocking. The command exits non-zero on any blocking
failure — which is what a branch-protection rule needs to hold the line.

## The rule that makes it trustworthy

**A required metric the candidate doesn't provide is a FAILURE, not a skip.** Silence is
never treated as compliant — a missing measurement blocks the merge exactly as a failed one
does. This is the difference between a gate and a rubber stamp.

## Architecture

```
   release_policy.yaml ─► Engine ─► per gate: candidate metric vs threshold
   (the gates)                        │
                                      ▼
                              GateDecision {allowed, blocking_failures, warnings}
                                      │
                                      ▼
                              exit 0 (merge) | exit 1 (blocked)  ─► required CI check
```

## Quickstart

```bash
pip install -e ".[dev]"

# A clean candidate -> allowed (exit 0):
gatecheck --policy policy/release_policy.yaml --metrics examples/candidate_pass.json

# A failing candidate -> blocked (exit 1):
gatecheck --policy policy/release_policy.yaml --metrics examples/candidate_block.json
```

The blocked run:

```
[PASS]  accuracy-floor: ok
[BLOCK] bias-ratio-floor: 0.62 gte 0.8 is false
[BLOCK] drift-ceiling: 0.34 lte 0.2 is false
[BLOCK] pii-zero: 2.0 eq 0.0 is false
[WARN]  latency-budget: 300.0 lte 250.0 is false
{"allowed": false, "blocking_failures": ["bias-ratio-floor","drift-ceiling","pii-zero"], ...}
```

## Wiring it as a real gate (GitHub)

1. Add a CI job that runs `gatecheck ...` on every pull request.
2. In **Settings → Branches → branch protection**, mark that job a **required** status check.
3. Disable bypass. Now a candidate that fails a blocking gate can't be merged until fixed.

## Testing

```bash
ruff check .     # lint
pytest -v        # 9 tests
```

`tests/test_engine.py` covers the decision logic — including
`test_missing_required_metric_blocks_not_skips`, the rule that silence is not a pass.
`tests/test_cli.py` proves the exit code gates (0 allow / 1 block).

## Project layout

```
policy/release_policy.yaml    the gates a candidate must clear
examples/*.json               sample candidate metrics (pass / block / missing)
src/gate/
  schema.py                   Gate, Policy, GateResult, GateDecision
  policy.py                   load the policy
  engine.py                   evaluate metrics vs gates (incl. missing-metric rule)
  cli.py                      gatecheck — exit code is the gate
tests/                        engine + CLI
docs/DESIGN.md                deeper architecture + rationale
```

## What I'd build next

- Post the decision as a PR comment (pass/block table) via the CI job.
- Policy inheritance: a base policy plus per-model overrides.
- A "diff vs. current production" mode: block only on *regressions*, not absolute floors.

## License

MIT — see [LICENSE](LICENSE).
