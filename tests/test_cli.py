"""CLI tests: the exit code is the gate (0 allow / 1 block)."""

import json

from gate.cli import main


def test_passing_candidate_exit_zero(capsys):
    rc = main(["--policy", "policy/release_policy.yaml", "--metrics", "examples/candidate_pass.json"])
    summary = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert rc == 0
    assert summary["allowed"] is True


def test_blocking_candidate_exit_one(capsys):
    rc = main(["--policy", "policy/release_policy.yaml", "--metrics", "examples/candidate_block.json"])
    summary = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert rc == 1
    assert summary["allowed"] is False
    assert summary["blocking_failures"]


def test_missing_metric_candidate_blocks(capsys):
    rc = main(["--policy", "policy/release_policy.yaml", "--metrics", "examples/candidate_missing.json"])
    assert rc == 1


def test_missing_file_errors():
    rc = main(["--policy", "policy/release_policy.yaml", "--metrics", "nope.json"])
    assert rc == 2
